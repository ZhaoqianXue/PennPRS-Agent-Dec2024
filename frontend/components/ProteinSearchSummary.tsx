"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { Check, ChevronRight, Users, Database, Dna, Activity, Layers, Sparkles, TrendingUp, Info, FlaskConical, Microscope } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ModelData } from './ModelCard';

interface ProteinModelData extends ModelData {
    protein_name?: string;
    gene_name?: string;
    platform?: string;
    tissue?: string;
    uniprot_id?: string;
    dev_cohorts?: string;
}

interface ProteinSearchSummaryProps {
    trait: string;
    models: ProteinModelData[];
    onAncestrySubmit: (ancestries: string[]) => void;
    activeAncestry?: string[];
}

const ancestryConfig = [
    { id: 'EUR', label: 'European', shortLabel: 'EUR', color: 'from-blue-500 to-blue-600' },
    { id: 'AFR', label: 'African', shortLabel: 'AFR', color: 'from-purple-500 to-purple-600' },
    { id: 'EAS', label: 'East Asian', shortLabel: 'EAS', color: 'from-emerald-500 to-emerald-600' },
    { id: 'SAS', label: 'South Asian', shortLabel: 'SAS', color: 'from-orange-500 to-orange-600' },
    { id: 'AMR', label: 'Hispanic', shortLabel: 'AMR', color: 'from-amber-500 to-amber-600' },
    { id: 'MIX', label: 'Others', shortLabel: 'MIX', color: 'from-pink-500 to-pink-600' },
];

interface ProteinSummaryStats {
    totalModels: number;
    sourceCounts: { local: number; api: number };
    // Sample Size
    sampleSizeRange: { min: number; max: number; median: number; total: number } | null;
    sampleSizeCount: number;
    // Platforms
    platforms: { name: string; count: number }[];
    // Tissues
    tissues: { name: string; count: number }[];
    // Metrics
    r2Range: { min: number; max: number; median: number } | null;
    r2Count: number;
    rhoRange: { min: number; max: number; median: number } | null;
    rhoCount: number;
    // Ancestry
    ancestryCounts: Record<string, number>;
    ancestryDetails: { code: string; label: string; count: number; percent: number }[];
    // Cohorts
    cohorts: { name: string; count: number }[];
    cohortCount: number;
    // Methods
    methods: { name: string; count: number }[];
    methodCount: number;
}

function computeProteinStats(models: ProteinModelData[]): ProteinSummaryStats {
    const stats: ProteinSummaryStats = {
        totalModels: models.length,
        sourceCounts: { local: 0, api: 0 },
        sampleSizeRange: null,
        sampleSizeCount: 0,
        platforms: [],
        tissues: [],
        r2Range: null,
        r2Count: 0,
        rhoRange: null,
        rhoCount: 0,
        ancestryCounts: {},
        ancestryDetails: [],
        cohorts: [],
        cohortCount: 0,
        methods: [],
        methodCount: 0
    };

    if (models.length === 0) return stats;

    const platformMap: Record<string, number> = {};
    const tissueMap: Record<string, number> = {};
    const cohortMap: Record<string, number> = {};
    const methodMap: Record<string, number> = {};
    const r2Values: number[] = [];
    const rhoValues: number[] = [];
    const sampleSizes: number[] = [];

    models.forEach(m => {
        // Source Count
        if (m.source?.toLowerCase().includes('api')) stats.sourceCounts.api++;
        else stats.sourceCounts.local++;

        // Platform & Tissue
        if (m.platform) platformMap[m.platform] = (platformMap[m.platform] || 0) + 1;
        if (m.tissue) tissueMap[m.tissue] = (tissueMap[m.tissue] || 0) + 1;

        // Metrics
        if (m.metrics?.R2 && typeof m.metrics.R2 === 'number') r2Values.push(m.metrics.R2);
        if (m.metrics?.Rho && typeof m.metrics.Rho === 'number') rhoValues.push(m.metrics.Rho);
        if (m.sample_size) sampleSizes.push(m.sample_size);

        // Cohorts
        if (m.dev_cohorts) {
            m.dev_cohorts.split(',').forEach(c => {
                const trimmed = c.trim();
                if (trimmed) cohortMap[trimmed] = (cohortMap[trimmed] || 0) + 1;
            });
        }

        // Methods
        if (m.method) {
            methodMap[m.method] = (methodMap[m.method] || 0) + 1;
        }
    });

    stats.platforms = Object.entries(platformMap).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
    stats.tissues = Object.entries(tissueMap).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
    stats.cohorts = Object.entries(cohortMap).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
    stats.cohortCount = stats.cohorts.length;
    stats.methods = Object.entries(methodMap).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
    stats.methodCount = stats.methods.length;

    const getStats = (values: number[]) => {
        if (values.length === 0) return null;
        const sorted = [...values].sort((a, b) => a - b);
        return {
            min: Math.min(...values),
            max: Math.max(...values),
            median: sorted[Math.floor(sorted.length / 2)],
            total: values.reduce((a, b) => a + b, 0)
        };
    };

    stats.r2Range = getStats(r2Values);
    stats.r2Count = r2Values.length;
    stats.rhoRange = getStats(rhoValues);
    stats.rhoCount = rhoValues.length;
    stats.sampleSizeRange = getStats(sampleSizes);
    stats.sampleSizeCount = sampleSizes.length;

    const ancestryMapping: Record<string, string> = {
        'european': 'EUR', 'eur': 'EUR',
        'african': 'AFR', 'afr': 'AFR',
        'east asian': 'EAS', 'eas': 'EAS',
        'south asian': 'SAS', 'sas': 'SAS',
        'hispanic': 'AMR', 'amr': 'AMR',
        'multi-ancestry': 'MIX', 'mix': 'MIX'
    };

    models.forEach(m => {
        if (m.ancestry) {
            const parts = m.ancestry.split(',').map(s => s.trim().toLowerCase());
            parts.forEach(p => {
                const code = ancestryMapping[p] || p.toUpperCase();
                if (ancestryConfig.some(a => a.id === code)) {
                    stats.ancestryCounts[code] = (stats.ancestryCounts[code] || 0) + 1;
                }
            });
        }
    });

    const totalAnc = Object.values(stats.ancestryCounts).reduce((a, b) => a + b, 0);
    stats.ancestryDetails = ancestryConfig.map(anc => ({
        code: anc.id,
        label: anc.label,
        count: stats.ancestryCounts[anc.id] || 0,
        percent: totalAnc > 0 ? ((stats.ancestryCounts[anc.id] || 0) / totalAnc) * 100 : 0
    })).filter(a => a.count > 0).sort((a, b) => b.count - a.count);

    return stats;
}

function formatNumber(n: number): string {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(0)}k`;
    return n.toLocaleString();
}

export default function ProteinSearchSummary({
    trait,
    models,
    onAncestrySubmit,
    activeAncestry
}: ProteinSearchSummaryProps) {
    const [selected, setSelected] = useState<string[]>(activeAncestry || []);
    const stats = useMemo(() => computeProteinStats(models), [models]);

    const toggleSelection = (id: string) => {
        setSelected(prev =>
            prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
        );
    };

    const handleContinue = () => {
        onAncestrySubmit(selected);
    };

    const matchingCount = useMemo(() => {
        if (selected.length === 0) return models.length;

        const ancestryMap: Record<string, string> = {
            'EUR': 'european', 'AFR': 'african', 'EAS': 'east asian',
            'SAS': 'south asian', 'AMR': 'hispanic', 'MIX': 'multi-ancestry'
        };

        return models.filter(m => {
            if (!m.ancestry) return false;
            const norm = m.ancestry.toLowerCase();
            return selected.some(s =>
                norm.includes(s.toLowerCase()) ||
                (ancestryMap[s] && norm.includes(ancestryMap[s]))
            );
        }).length;
    }, [models, selected]);

    return (
        <div className="p-6 max-w-4xl mx-auto h-full flex flex-col animate-in fade-in duration-500 overflow-y-auto">
            {/* Header */}
            <div className="mb-6 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-400 rounded-full text-sm font-medium mb-4 border border-violet-100 dark:border-violet-800">
                    <Sparkles className="w-4 h-4" />
                    Search Complete
                </div>
                <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-2">
                    {models.length} Proteomics Models Found for "{trait}"
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    {stats.sourceCounts.api} from OmicsPred API • {stats.sourceCounts.local} from Local Database
                </p>
            </div>

            {/* Vertical Summary Sections */}
            <div className="space-y-4 mb-6">

                {/* 1. Sample Size */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                            <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Sample Size</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.sampleSizeCount} models with data</span>
                    </div>
                    {stats.sampleSizeRange ? (
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Minimum</div>
                                <div className="text-lg font-bold font-mono text-gray-900 dark:text-white">{formatNumber(stats.sampleSizeRange.min)}</div>
                            </div>
                            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Median</div>
                                <div className="text-lg font-bold font-mono text-blue-600 dark:text-blue-400">{formatNumber(stats.sampleSizeRange.median)}</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Maximum</div>
                                <div className="text-lg font-bold font-mono text-gray-900 dark:text-white">{formatNumber(stats.sampleSizeRange.max)}</div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-400 italic text-sm">No sample size data available</div>
                    )}
                </div>

                {/* 2. Ancestry Distribution */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
                            <Dna className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Ancestry Distribution</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.ancestryDetails.length} groups</span>
                    </div>
                    {stats.ancestryDetails.length > 0 ? (
                        <div className="space-y-2">
                            {stats.ancestryDetails.map(anc => (
                                <div key={anc.code} className="flex items-center gap-3">
                                    <div className="w-16 text-sm font-medium text-gray-700 dark:text-gray-300">{anc.label}</div>
                                    <div className="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-purple-500 to-purple-600 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.max(anc.percent, 5)}%` }}
                                        />
                                    </div>
                                    <div className="w-20 text-right text-sm font-mono">
                                        <span className="font-bold text-gray-900 dark:text-white">{anc.count}</span>
                                        <span className="text-gray-400 ml-1">({anc.percent.toFixed(0)}%)</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-400 italic text-sm">No ancestry data available</div>
                    )}
                </div>

                {/* 3. R² Range */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-violet-100 dark:bg-violet-900/40 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">R² (Variance Explained)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.r2Count} models with data</span>
                    </div>
                    {stats.r2Range ? (
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Minimum</div>
                                <div className="text-lg font-bold font-mono text-violet-600 dark:text-violet-400">{stats.r2Range.min.toFixed(4)}</div>
                            </div>
                            <div className="text-center p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
                                <div className="text-xs text-violet-600 dark:text-violet-400 mb-1">Median</div>
                                <div className="text-lg font-bold font-mono text-violet-600 dark:text-violet-400">{stats.r2Range.median.toFixed(4)}</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Maximum</div>
                                <div className="text-lg font-bold font-mono text-violet-600 dark:text-violet-400">{stats.r2Range.max.toFixed(4)}</div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-400 italic text-sm">No R² data available</div>
                    )}
                </div>

                {/* 4. Rho Range */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg">
                            <Activity className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">ρ (Spearman's Correlation)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.rhoCount} models with data</span>
                    </div>
                    {stats.rhoRange ? (
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Minimum</div>
                                <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400">{stats.rhoRange.min.toFixed(3)}</div>
                            </div>
                            <div className="text-center p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                                <div className="text-xs text-indigo-600 dark:text-indigo-400 mb-1">Median</div>
                                <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400">{stats.rhoRange.median.toFixed(3)}</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Maximum</div>
                                <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400">{stats.rhoRange.max.toFixed(3)}</div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-400 italic text-sm">No Rho data available</div>
                    )}
                </div>

                {/* 5. Platforms */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-amber-100 dark:bg-amber-900/40 rounded-lg">
                            <FlaskConical className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Measurement Platforms</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.platforms.length} variants</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {stats.platforms.map(p => (
                            <span key={p.name} className="px-3 py-1.5 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 text-sm font-medium rounded-lg border border-amber-200 dark:border-amber-800">
                                {p.name} <span className="text-amber-400 ml-1">({p.count})</span>
                            </span>
                        ))}
                    </div>
                </div>

                {/* 6. Biological Tissues */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-rose-100 dark:bg-rose-900/40 rounded-lg">
                            <Microscope className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Biological Tissues</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.tissues.length} tissues</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {stats.tissues.slice(0, 15).map(t => (
                            <span key={t.name} className="px-3 py-1.5 bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-300 text-sm font-medium rounded-lg border border-rose-200 dark:border-rose-800">
                                {t.name} <span className="text-rose-400 ml-1">({t.count})</span>
                            </span>
                        ))}
                    </div>
                </div>

                {/* 7. Study Cohorts */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                            <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Training/Development Cohorts</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.cohortCount} unique sources</span>
                    </div>
                    {stats.cohortCount > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {stats.cohorts.slice(0, 15).map(c => (
                                <span key={c.name} className="px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm font-medium rounded-lg border border-blue-200 dark:border-blue-800">
                                    {c.name} <span className="text-blue-400 ml-1">({c.count})</span>
                                </span>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-400 italic text-sm">No cohort data available</div>
                    )}
                </div>

                {/* 8. PRS Methods */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-emerald-100 dark:bg-emerald-900/40 rounded-lg">
                            <Layers className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">PRS Methods</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.methodCount} unique methods</span>
                    </div>
                    {stats.methodCount > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {stats.methods.map(m => (
                                <span key={m.name} className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm font-medium rounded-lg border border-emerald-200 dark:border-emerald-800">
                                    {m.name} <span className="text-emerald-400 ml-1">({m.count})</span>
                                </span>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-400 italic text-sm">No methodology data available</div>
                    )}
                </div>
            </div>

            {/* Ancestry Filter Section */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-gradient-to-br from-violet-500 to-indigo-500 rounded-lg">
                        <Dna className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                            Filter by Target Ancestry
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Select ancestry group(s) to filter models (multi-select)
                        </p>
                    </div>
                </div>

                {/* Ancestry Grid with Checkboxes */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
                    {ancestryConfig.map((anc) => {
                        const isSelected = selected.includes(anc.id);
                        const count = stats.ancestryCounts[anc.id] || 0;
                        const hasModels = count > 0;

                        return (
                            <button
                                key={anc.id}
                                onClick={() => hasModels && toggleSelection(anc.id)}
                                disabled={!hasModels}
                                className={cn(
                                    "relative p-4 rounded-xl border-2 transition-all duration-200 text-center group",
                                    isSelected
                                        ? "border-violet-500 bg-violet-50 dark:bg-violet-900/20 shadow-md"
                                        : hasModels
                                            ? "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-violet-300 hover:shadow-sm"
                                            : "border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 opacity-50 cursor-not-allowed"
                                )}
                            >
                                <div className={cn(
                                    "absolute top-2 right-2 w-5 h-5 rounded flex items-center justify-center transition-all border-2",
                                    isSelected
                                        ? "bg-violet-500 border-violet-500 text-white"
                                        : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
                                )}>
                                    {isSelected && <Check size={12} strokeWidth={3} />}
                                </div>

                                <div className={cn(
                                    "w-10 h-10 rounded-full mx-auto mb-2 bg-gradient-to-br flex items-center justify-center text-white font-bold text-sm",
                                    anc.color
                                )}>
                                    {anc.shortLabel}
                                </div>
                                <div className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                                    {anc.label}
                                </div>
                                <div className={cn(
                                    "text-xs font-medium",
                                    hasModels ? "text-gray-600 dark:text-gray-400" : "text-gray-400 dark:text-gray-600"
                                )}>
                                    {count} {count === 1 ? 'model' : 'models'}
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* Info tip */}
                <div className="flex items-start gap-2 p-3 bg-violet-50 dark:bg-violet-900/10 rounded-lg border border-violet-100 dark:border-violet-900/30 mb-4">
                    <Info className="w-4 h-4 text-violet-500 mt-0.5 shrink-0" />
                    <p className="text-xs text-violet-700 dark:text-violet-300">
                        <strong>Tip:</strong> Filtering by your target ancestry ensures the most accurate genetic score recommendations.
                    </p>
                </div>

                {/* Action Footer */}
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                        {selected.length === 0 ? (
                            <span>Showing all <strong className="text-gray-900 dark:text-white">{models.length}</strong> models</span>
                        ) : (
                            <span>
                                <strong className="text-violet-600 dark:text-violet-400">{matchingCount}</strong> of {models.length} models match your selection
                            </span>
                        )}
                    </div>

                    <button
                        onClick={handleContinue}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 rounded-xl font-semibold transition-all shadow-lg transform active:scale-[0.98] bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 hover:shadow-violet-500/25 text-white"
                    >
                        {selected.length > 0 ? `View ${matchingCount} Models` : `View All Models`}
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
