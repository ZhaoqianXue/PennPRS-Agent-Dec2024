"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { Check, ChevronRight, Users, Database, Dna, Activity, Layers, Sparkles, TrendingUp, Info, FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ModelData } from './ModelCard';

interface SearchSummaryViewProps {
    trait: string;
    models: ModelData[];
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

interface SummaryStats {
    totalModels: number;
    // Sample Size
    sampleSizeRange: { min: number; max: number; median: number; total: number } | null;
    sampleSizeCount: number;
    // Ancestry
    ancestryCounts: Record<string, number>;
    ancestryDetails: { code: string; label: string; count: number; percent: number }[];
    // R²
    r2Range: { min: number; max: number; median: number } | null;
    r2Count: number;
    // Cohorts
    cohorts: { name: string; count: number }[];
    cohortCount: number;
    // AUC
    aucRange: { min: number; max: number; median: number } | null;
    aucCount: number;
    // Methods
    methods: { name: string; count: number }[];
    methodCount: number;
    // Source
    sourceCounts: { pgsCatalog: number; pennprs: number };
}

function computeStats(models: ModelData[]): SummaryStats {
    const stats: SummaryStats = {
        totalModels: models.length,
        sampleSizeRange: null,
        sampleSizeCount: 0,
        ancestryCounts: {},
        ancestryDetails: [],
        r2Range: null,
        r2Count: 0,
        cohorts: [],
        cohortCount: 0,
        aucRange: null,
        aucCount: 0,
        methods: [],
        methodCount: 0,
        sourceCounts: { pgsCatalog: 0, pennprs: 0 }
    };

    if (models.length === 0) return stats;

    // Source Counts
    models.forEach(m => {
        if (m.source === 'PGS Catalog') stats.sourceCounts.pgsCatalog++;
        else stats.sourceCounts.pennprs++;
    });

    // Sample Size - complete stats
    const sampleSizes = models.map(m => m.sample_size).filter((s): s is number => s !== undefined && s > 0);
    stats.sampleSizeCount = sampleSizes.length;
    if (sampleSizes.length > 0) {
        const sorted = [...sampleSizes].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        const total = sampleSizes.reduce((a, b) => a + b, 0);
        stats.sampleSizeRange = {
            min: Math.min(...sampleSizes),
            max: Math.max(...sampleSizes),
            median,
            total
        };
    }

    // Ancestry Distribution - detailed breakdown
    const ancestryMap: Record<string, string> = {
        'european': 'EUR', 'eur': 'EUR',
        'african': 'AFR', 'afr': 'AFR',
        'east asian': 'EAS', 'eas': 'EAS',
        'south asian': 'SAS', 'sas': 'SAS',
        'hispanic': 'AMR', 'amr': 'AMR', 'admixed american': 'AMR',
        'multi-ancestry': 'MIX', 'mix': 'MIX', 'other': 'MIX', 'others': 'MIX'
    };

    models.forEach(m => {
        if (m.ancestry) {
            const parts = m.ancestry.split(',').map(s => s.trim().toLowerCase());
            parts.forEach(p => {
                const code = ancestryMap[p] || p.toUpperCase();
                if (ancestryConfig.some(a => a.id === code)) {
                    stats.ancestryCounts[code] = (stats.ancestryCounts[code] || 0) + 1;
                }
            });
        }
    });

    // Build ancestry details with percentages
    const totalAncestryModels = Object.values(stats.ancestryCounts).reduce((a, b) => a + b, 0);
    stats.ancestryDetails = ancestryConfig.map(anc => ({
        code: anc.id,
        label: anc.label,
        count: stats.ancestryCounts[anc.id] || 0,
        percent: totalAncestryModels > 0 ? ((stats.ancestryCounts[anc.id] || 0) / totalAncestryModels) * 100 : 0
    })).filter(a => a.count > 0).sort((a, b) => b.count - a.count);

    // R² - complete stats with median
    const r2Values = models.map(m => m.metrics?.R2).filter((r): r is number => r !== undefined && r > 0);
    stats.r2Count = r2Values.length;
    if (r2Values.length > 0) {
        const sorted = [...r2Values].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        stats.r2Range = { min: Math.min(...r2Values), max: Math.max(...r2Values), median };
    }

    // Cohorts - with counts
    const cohortCounts: Record<string, number> = {};
    models.forEach(m => {
        if (m.dev_cohorts) {
            m.dev_cohorts.split(',').forEach(c => {
                const trimmed = c.trim();
                if (trimmed) {
                    cohortCounts[trimmed] = (cohortCounts[trimmed] || 0) + 1;
                }
            });
        }
    });
    stats.cohorts = Object.entries(cohortCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);
    stats.cohortCount = stats.cohorts.length;

    // AUC - complete stats with median
    const aucValues = models.map(m => m.metrics?.AUC).filter((a): a is number => a !== undefined && a > 0);
    stats.aucCount = aucValues.length;
    if (aucValues.length > 0) {
        const sorted = [...aucValues].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        stats.aucRange = { min: Math.min(...aucValues), max: Math.max(...aucValues), median };
    }

    // Methods - with counts
    const methodCounts: Record<string, number> = {};
    models.forEach(m => {
        if (m.method) {
            methodCounts[m.method] = (methodCounts[m.method] || 0) + 1;
        }
    });
    stats.methods = Object.entries(methodCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);
    stats.methodCount = stats.methods.length;

    return stats;
}

function formatNumber(n: number): string {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(0)}k`;
    return n.toLocaleString();
}

export default function SearchSummaryView({
    trait,
    models,
    onAncestrySubmit,
    activeAncestry
}: SearchSummaryViewProps) {
    const [selected, setSelected] = useState<string[]>(activeAncestry || []);
    const stats = useMemo(() => computeStats(models), [models]);

    useEffect(() => {
        if (activeAncestry) {
            setSelected(activeAncestry);
        }
    }, [activeAncestry]);

    const toggleSelection = (id: string) => {
        setSelected(prev =>
            prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
        );
    };

    const handleContinue = () => {
        onAncestrySubmit(selected);
    };

    // Count models that match selected ancestry
    const matchingCount = useMemo(() => {
        if (selected.length === 0) return models.length;

        const ancestryMap: Record<string, string> = {
            'EUR': 'european', 'AFR': 'african', 'EAS': 'east asian',
            'SAS': 'south asian', 'AMR': 'hispanic', 'MIX': 'multi-ancestry'
        };

        return models.filter(m => {
            if (!m.ancestry) return false;
            const normalized = m.ancestry.toLowerCase();
            return selected.some(s =>
                normalized.includes(s.toLowerCase()) ||
                normalized.includes(ancestryMap[s] || '')
            );
        }).length;
    }, [models, selected]);

    return (
        <div className="p-6 max-w-4xl mx-auto h-full flex flex-col animate-in fade-in duration-500 overflow-y-auto">
            {/* Header */}
            <div className="mb-6 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-full text-sm font-medium mb-4">
                    <Sparkles className="w-4 h-4" />
                    Search Complete
                </div>
                <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-2">
                    {models.length} Models Found for "{trait}"
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    {stats.sourceCounts.pgsCatalog} from PGS Catalog • {stats.sourceCounts.pennprs} from PennPRS
                </p>
            </div>

            {/* Summary Sections - Vertical Layout with Complete Info */}
            {/* Order: Sample Size → Ancestry → AUC → R² → Cohorts → Methods */}
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
                        <div className="text-gray-400 italic">No sample size data available</div>
                    )}
                </div>

                {/* 2. Ancestry Distribution */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
                            <Dna className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Ancestry Distribution</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.ancestryDetails.length} ancestry groups</span>
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
                        <div className="text-gray-400 italic">No ancestry data available</div>
                    )}
                </div>

                {/* 3. AUC Range */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">
                            <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">AUC (Classification Accuracy)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.aucCount} models with data</span>
                    </div>
                    {stats.aucRange ? (
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Minimum</div>
                                <div className="text-lg font-bold font-mono text-green-600 dark:text-green-400">{stats.aucRange.min.toFixed(3)}</div>
                            </div>
                            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <div className="text-xs text-green-600 dark:text-green-400 mb-1">Median</div>
                                <div className="text-lg font-bold font-mono text-green-600 dark:text-green-400">{stats.aucRange.median.toFixed(3)}</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Maximum</div>
                                <div className="text-lg font-bold font-mono text-green-600 dark:text-green-400">{stats.aucRange.max.toFixed(3)}</div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-400 italic">No AUC data available</div>
                    )}
                </div>

                {/* 4. R² Range */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">R² (Variance Explained)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.r2Count} models with data</span>
                    </div>
                    {stats.r2Range ? (
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Minimum</div>
                                <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400">{stats.r2Range.min.toFixed(4)}</div>
                            </div>
                            <div className="text-center p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                                <div className="text-xs text-indigo-600 dark:text-indigo-400 mb-1">Median</div>
                                <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400">{stats.r2Range.median.toFixed(4)}</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="text-xs text-gray-500 mb-1">Maximum</div>
                                <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400">{stats.r2Range.max.toFixed(4)}</div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-400 italic">No R² data available</div>
                    )}
                </div>

                {/* 5. Cohorts */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-amber-100 dark:bg-amber-900/40 rounded-lg">
                            <Database className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Training/Development Cohorts</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.cohortCount} unique cohorts</span>
                    </div>
                    {stats.cohorts.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {stats.cohorts.map(cohort => (
                                <span key={cohort.name} className="px-3 py-1.5 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 text-sm font-medium rounded-lg border border-amber-200 dark:border-amber-800">
                                    {cohort.name} <span className="text-amber-400 ml-1">({cohort.count})</span>
                                </span>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-400 italic">No cohort data available</div>
                    )}
                </div>

                {/* 6. PRS Methods */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-rose-100 dark:bg-rose-900/40 rounded-lg">
                            <FlaskConical className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">PRS Methods</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.methodCount} unique methods</span>
                    </div>
                    {stats.methods.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {stats.methods.map(method => (
                                <span key={method.name} className="px-3 py-1.5 bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-300 text-sm font-medium rounded-lg border border-rose-200 dark:border-rose-800">
                                    {method.name} <span className="text-rose-400 ml-1">({method.count})</span>
                                </span>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-400 italic">No method data available</div>
                    )}
                </div>
            </div>

            {/* Ancestry Filter Section */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg">
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

                {/* Ancestry Grid with Checkboxes (Square, Multi-Select) */}
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
                                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md"
                                        : hasModels
                                            ? "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-blue-300 hover:shadow-sm"
                                            : "border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 opacity-50 cursor-not-allowed"
                                )}
                            >
                                {/* Square Checkbox for Multi-Select */}
                                <div className={cn(
                                    "absolute top-2 right-2 w-5 h-5 rounded flex items-center justify-center transition-all border-2",
                                    isSelected
                                        ? "bg-blue-500 border-blue-500 text-white"
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
                <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-900/30 mb-4">
                    <Info className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                    <p className="text-xs text-blue-700 dark:text-blue-300">
                        <strong>Tip:</strong> You can select multiple ancestries. Models trained on similar populations may provide better prediction accuracy for your cohort.
                    </p>
                </div>

                {/* Action Footer */}
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                        {selected.length === 0 ? (
                            <span>Showing all <strong className="text-gray-900 dark:text-white">{models.length}</strong> models</span>
                        ) : (
                            <span>
                                <strong className="text-blue-600 dark:text-blue-400">{matchingCount}</strong> of {models.length} models match your selection
                            </span>
                        )}
                    </div>

                    <button
                        onClick={handleContinue}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 rounded-xl font-semibold transition-all shadow-lg transform active:scale-[0.98] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-blue-500/25 text-white"
                    >
                        {selected.length > 0 ? `View ${matchingCount} Models` : `View All Models`}
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
