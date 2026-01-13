"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { Check, ChevronRight, ChevronLeft, Users, Database, Dna, Activity, Layers, Sparkles, TrendingUp, Info, FlaskConical, X, Bot, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ModelData } from './ModelCard';
import BeeSwarmChart from './BeeSwarmChart';
import DistributionChart from './DistributionChart';

interface SearchSummaryViewProps {
    trait: string;
    models: ModelData[];
    onAncestrySubmit: (ancestries: string[]) => void;
    activeAncestry?: string[];
    onViewDetails?: (model: ModelData) => void;
    onSaveModel?: (model: ModelData, event?: React.MouseEvent) => void;
}

const ancestryConfig = [
    { id: 'EUR', label: 'European', shortLabel: 'EUR', color: 'from-blue-500 to-blue-600' },
    { id: 'AFR', label: 'African', shortLabel: 'AFR', color: 'from-purple-500 to-purple-600' },
    { id: 'EAS', label: 'East Asian', shortLabel: 'EAS', color: 'from-emerald-500 to-emerald-600' },
    { id: 'SAS', label: 'South Asian', shortLabel: 'SAS', color: 'from-orange-500 to-orange-600' },
    { id: 'AMR', label: 'Hispanic', shortLabel: 'AMR', color: 'from-amber-500 to-amber-600' },
    { id: 'MIX', label: 'Others', shortLabel: 'MIX', color: 'from-pink-500 to-pink-600' },
];

// Wizard step configuration
type WizardStep = 'ancestry' | 'sampleSize' | 'auc' | 'r2' | 'variants' | 'cohorts';

const WIZARD_STEPS: { id: WizardStep; label: string; description: string; icon: React.ReactNode }[] = [
    { id: 'ancestry', label: 'Target Ancestry', description: 'Select population groups', icon: <Dna className="w-5 h-5" /> },
    { id: 'sampleSize', label: 'Sample Size', description: 'Training data size', icon: <Users className="w-5 h-5" /> },
    { id: 'auc', label: 'AUC', description: 'Classification accuracy', icon: <Activity className="w-5 h-5" /> },
    { id: 'r2', label: 'R²', description: 'Variance explained', icon: <TrendingUp className="w-5 h-5" /> },
    { id: 'variants', label: 'Variants', description: 'Number of SNPs', icon: <Layers className="w-5 h-5" /> },
    { id: 'cohorts', label: 'Cohorts', description: 'Training cohorts', icon: <Database className="w-5 h-5" /> },
];

// Range filter interface
interface RangeFilter {
    min: number | null;
    max: number | null;
    label: string;
}

// Preset range options
const PRESET_RANGES: Record<'sampleSize' | 'auc' | 'r2' | 'variants', { label: string; min: number | null; max: number | null }[]> = {
    sampleSize: [
        { label: '< 10k', min: null, max: 10000 },
        { label: '10k - 50k', min: 10000, max: 50000 },
        { label: '50k - 100k', min: 50000, max: 100000 },
        { label: '100k - 250k', min: 100000, max: 250000 },
        { label: '250k - 500k', min: 250000, max: 500000 },
        { label: '> 500k', min: 500000, max: null },
    ],
    auc: [
        { label: '< 0.6', min: null, max: 0.6 },
        { label: '0.6 - 0.7', min: 0.6, max: 0.7 },
        { label: '0.7 - 0.8', min: 0.7, max: 0.8 },
        { label: '0.8 - 0.9', min: 0.8, max: 0.9 },
        { label: '> 0.9', min: 0.9, max: null },
    ],
    r2: [
        { label: '< 0.01', min: null, max: 0.01 },
        { label: '0.01 - 0.05', min: 0.01, max: 0.05 },
        { label: '0.05 - 0.10', min: 0.05, max: 0.10 },
        { label: '0.10 - 0.20', min: 0.10, max: 0.20 },
        { label: '> 0.20', min: 0.20, max: null },
    ],
    variants: [
        { label: '< 10', min: null, max: 10 },
        { label: '10 - 50', min: 10, max: 50 },
        { label: '50 - 100', min: 50, max: 100 },
        { label: '100 - 500', min: 100, max: 500 },
        { label: '500 - 1,000', min: 500, max: 1000 },
        { label: '> 1,000', min: 1000, max: null },
    ],
};


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
    // Variants
    variantsRange: { min: number; max: number; median: number; total: number } | null;
    variantsCount: number;
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
        sourceCounts: { pgsCatalog: 0, pennprs: 0 },
        variantsRange: null,
        variantsCount: 0
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

    // Variants - complete stats with median and total
    const variantCounts = models.map(m => m.num_variants).filter((v): v is number => v !== undefined && v > 0);
    stats.variantsCount = variantCounts.length;
    if (variantCounts.length > 0) {
        const sorted = [...variantCounts].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        const total = variantCounts.reduce((a, b) => a + b, 0);
        stats.variantsRange = {
            min: Math.min(...variantCounts),
            max: Math.max(...variantCounts),
            median,
            total
        };
    }

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
    activeAncestry,
    onViewDetails,
    onSaveModel
}: SearchSummaryViewProps) {
    const [selected, setSelected] = useState<string[]>(activeAncestry || []);
    const [showWizardModal, setShowWizardModal] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);

    // Filter selections for wizard
    const [wizardFilters, setWizardFilters] = useState({
        ancestry: [] as string[],
        sampleSize: [] as RangeFilter[],
        auc: [] as RangeFilter[],
        r2: [] as RangeFilter[],
        variants: [] as RangeFilter[],
        cohorts: [] as string[],
    });

    const stats = useMemo(() => computeStats(models), [models]);

    // Available cohorts from models
    const availableCohorts = useMemo(() => {
        const cohortSet = new Set<string>();
        models.forEach(m => {
            if (m.dev_cohorts) {
                m.dev_cohorts.split(',').forEach(c => {
                    const trimmed = c.trim();
                    if (trimmed) cohortSet.add(trimmed);
                });
            }
        });
        return Array.from(cohortSet).sort();
    }, [models]);

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

    const handleViewAllModels = () => {
        onAncestrySubmit([]);
    };

    const handleGetRecommendation = () => {
        // Reset wizard state
        setCurrentStep(0);
        setWizardFilters({
            ancestry: [],
            sampleSize: [],
            auc: [],
            r2: [],
            variants: [],
            cohorts: [],
        });
        setShowWizardModal(true);
    };

    const handleNextStep = () => {
        if (currentStep < WIZARD_STEPS.length - 1) {
            setCurrentStep(prev => prev + 1);
        }
    };

    const handlePrevStep = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleWizardSubmit = () => {
        // Submit with ancestry filter
        onAncestrySubmit(wizardFilters.ancestry);
        setShowWizardModal(false);
    };

    const toggleWizardAncestry = (id: string) => {
        setWizardFilters(prev => ({
            ...prev,
            ancestry: prev.ancestry.includes(id)
                ? prev.ancestry.filter(a => a !== id)
                : [...prev.ancestry, id]
        }));
    };

    const toggleWizardRange = (type: 'sampleSize' | 'auc' | 'r2' | 'variants', range: RangeFilter) => {
        setWizardFilters(prev => {
            const currentRanges = prev[type];
            const existingIndex = currentRanges.findIndex(r => r.label === range.label);
            if (existingIndex >= 0) {
                return {
                    ...prev,
                    [type]: currentRanges.filter((_, i) => i !== existingIndex)
                };
            } else {
                return {
                    ...prev,
                    [type]: [...currentRanges, range]
                };
            }
        });
    };

    const toggleWizardCohort = (cohort: string) => {
        setWizardFilters(prev => ({
            ...prev,
            cohorts: prev.cohorts.includes(cohort)
                ? prev.cohorts.filter(c => c !== cohort)
                : [...prev.cohorts, cohort]
        }));
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

    // Get current selection count for progress indicator
    const getStepSelectionCount = (stepId: WizardStep) => {
        switch (stepId) {
            case 'ancestry': return wizardFilters.ancestry.length;
            case 'sampleSize': return wizardFilters.sampleSize.length;
            case 'auc': return wizardFilters.auc.length;
            case 'r2': return wizardFilters.r2.length;
            case 'variants': return wizardFilters.variants.length;
            case 'cohorts': return wizardFilters.cohorts.length;
            default: return 0;
        }
    };

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
                <p className="text-gray-500 dark:text-gray-400 mt-2 text-sm italic">
                    After reviewing the summary, you can explore the full list of models or let the PennPRS Agent recommend models tailored to your specific requirements.
                </p>
            </div>

            {/* Summary Sections - Vertical Layout with Complete Info */}
            {/* Order: Sample Size → Ancestry → AUC → R² → Variants → Cohorts → Methods */}
            <div className="space-y-4 mb-6">

                {/* 1. Ancestry Distribution */}
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

                {/* 2. Sample Size - Interactive Bee Swarm Chart */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                            <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Sample Size Distribution</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.sampleSizeCount} models with data</span>
                    </div>
                    {stats.sampleSizeRange ? (
                        <>
                            <div className="flex items-center justify-between gap-2 mb-4 px-2 py-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Min:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{formatNumber(stats.sampleSizeRange.min)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Median:</span>
                                    <span className="text-sm font-mono font-bold text-blue-600 dark:text-blue-400">{formatNumber(stats.sampleSizeRange.median)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Max:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{formatNumber(stats.sampleSizeRange.max)}</span>
                                </div>
                            </div>
                            <BeeSwarmChart
                                data={models}
                                colorScheme="blue"
                                height={160}
                                onViewDetails={onViewDetails}
                                onSaveModel={onSaveModel}
                                activeAncestry={activeAncestry}
                                valueAccessor={(m) => m.sample_size}
                            />
                        </>
                    ) : (
                        <div className="text-gray-400 italic">No sample size data available</div>
                    )}
                </div>

                {/* 3. AUC - Interactive Bee Swarm Chart */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">
                            <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">AUC (Classification Accuracy)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.aucCount} models with data</span>
                    </div>
                    {stats.aucRange ? (
                        <>
                            <div className="flex items-center justify-between gap-2 mb-4 px-2 py-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Min:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{stats.aucRange.min.toFixed(3)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Median:</span>
                                    <span className="text-sm font-mono font-bold text-green-600 dark:text-green-400">{stats.aucRange.median.toFixed(3)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Max:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{stats.aucRange.max.toFixed(3)}</span>
                                </div>
                            </div>
                            <BeeSwarmChart
                                data={models}
                                colorScheme="green"
                                height={160}
                                onViewDetails={onViewDetails}
                                onSaveModel={onSaveModel}
                                activeAncestry={activeAncestry}
                                formatValue={(v) => v.toFixed(3)}
                                valueAccessor={(m) => m.metrics?.AUC}
                                domain={[0.5, 1.0]}
                                scaleType="linear"
                                xAxisLabel="AUC"
                            />
                        </>
                    ) : (
                        <div className="text-gray-400 italic">No AUC data available</div>
                    )}
                </div>

                {/* 4. R² - Interactive Bee Swarm Chart */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">R² (Variance Explained)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.r2Count} models with data</span>
                    </div>
                    {stats.r2Range ? (
                        <>
                            <div className="flex items-center justify-between gap-2 mb-4 px-2 py-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Min:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{stats.r2Range.min.toFixed(4)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Median:</span>
                                    <span className="text-sm font-mono font-bold text-indigo-600 dark:text-indigo-400">{stats.r2Range.median.toFixed(4)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Max:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{stats.r2Range.max.toFixed(4)}</span>
                                </div>
                            </div>
                            <BeeSwarmChart
                                data={models}
                                colorScheme="purple"
                                height={160}
                                onViewDetails={onViewDetails}
                                onSaveModel={onSaveModel}
                                activeAncestry={activeAncestry}
                                formatValue={(v) => v.toFixed(4)}
                                valueAccessor={(m) => m.metrics?.R2}
                                xAxisLabel="R²"
                            />
                        </>
                    ) : (
                        <div className="text-gray-400 italic">No R² data available</div>
                    )}
                </div>

                {/* 5. Variants - Interactive Bee Swarm Chart */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-teal-100 dark:bg-teal-900/40 rounded-lg">
                            <Layers className="w-5 h-5 text-teal-600 dark:text-teal-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Variants (SNPs)</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.variantsCount} models with data</span>
                    </div>
                    {stats.variantsRange ? (
                        <>
                            <div className="flex items-center justify-between gap-2 mb-4 px-2 py-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Min:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{formatNumber(stats.variantsRange.min)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Median:</span>
                                    <span className="text-sm font-mono font-bold text-teal-600 dark:text-teal-400">{formatNumber(stats.variantsRange.median)}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs text-gray-500">Max:</span>
                                    <span className="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">{formatNumber(stats.variantsRange.max)}</span>
                                </div>
                            </div>
                            <BeeSwarmChart
                                data={models}
                                colorScheme="teal"
                                height={160}
                                onViewDetails={onViewDetails}
                                onSaveModel={onSaveModel}
                                activeAncestry={activeAncestry}
                                valueAccessor={(m) => m.num_variants}
                                scaleType="log"
                                xAxisLabel="Number of Variants"
                            />
                        </>
                    ) : (
                        <div className="text-gray-400 italic">No variants data available</div>
                    )}
                </div>

                {/* 6. Training/Development Cohorts */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-amber-100 dark:bg-amber-900/40 rounded-lg">
                            <Database className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">Training/Development Cohorts</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.cohortCount} unique cohorts</span>
                    </div>
                    {stats.cohorts.length > 0 ? (
                        <DistributionChart
                            data={stats.cohorts.map(c => ({ label: c.name, count: c.count }))}
                            type="bar"
                            colorScheme="amber"
                        />
                    ) : (
                        <div className="text-gray-400 italic">No cohort data available</div>
                    )}
                </div>

                {/* 7. PRS Methods */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-rose-100 dark:bg-rose-900/40 rounded-lg">
                            <FlaskConical className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                        </div>
                        <h4 className="text-base font-bold text-gray-900 dark:text-white">PRS Methods</h4>
                        <span className="text-xs text-gray-400 ml-auto">{stats.methodCount} unique methods</span>
                    </div>
                    {stats.methods.length > 0 ? (
                        <DistributionChart
                            data={stats.methods.map(m => ({ label: m.name, count: m.count }))}
                            type="bar" // Changed to bar as requested
                            color="#E11D48" // Rose-600 to match icon
                        />
                    ) : (
                        <div className="text-gray-400 italic">No method data available</div>
                    )}
                </div>


            </div>

            {/* Action Selection - Binary Choice */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-5">
                    <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                            How would you like to proceed?
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Choose to explore all models or get personalized recommendations
                        </p>
                    </div>
                </div>

                {/* Binary Choice Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Option 1: View All Models */}
                    <button
                        onClick={handleViewAllModels}
                        className="group relative p-6 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-blue-400 hover:shadow-lg transition-all duration-300 text-left"
                    >
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-blue-100 dark:bg-blue-900/40 rounded-xl group-hover:bg-blue-200 dark:group-hover:bg-blue-900/60 transition-colors">
                                <Eye className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div className="flex-1">
                                <h4 className="font-bold text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                    View All Models
                                </h4>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                                    Browse and filter through all {models.length} available models yourself
                                </p>
                                <div className="flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <span>Explore models</span>
                                    <ChevronRight className="w-4 h-4" />
                                </div>
                            </div>
                        </div>
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                    </button>

                    {/* Option 2: Get PennPRS Agent Recommendations */}
                    <button
                        onClick={handleGetRecommendation}
                        className="group relative p-6 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-purple-400 hover:shadow-lg transition-all duration-300 text-left"
                    >
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-purple-100 dark:bg-purple-900/40 rounded-xl group-hover:bg-purple-200 dark:group-hover:bg-purple-900/60 transition-colors">
                                <Bot className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div className="flex-1">
                                <h4 className="font-bold text-gray-900 dark:text-white mb-1 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                                    Get PennPRS Agent Recommendations
                                </h4>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                                    Let PennPRS Agent recommend models tailored to your specific requirements
                                </p>
                                <div className="flex items-center gap-2 text-sm font-medium text-purple-600 dark:text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <span>Start wizard</span>
                                    <ChevronRight className="w-4 h-4" />
                                </div>
                            </div>
                        </div>
                        <div className="absolute top-3 right-3 px-2 py-0.5 bg-gradient-to-r from-purple-500 to-indigo-500 text-white text-xs font-medium rounded-full">
                            Recommended
                        </div>
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                    </button>
                </div>
            </div>

            {/* Multi-Step Wizard Modal */}
            {showWizardModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <div
                        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                        onClick={() => setShowWizardModal(false)}
                    />

                    {/* Modal Content */}
                    <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden animate-in fade-in zoom-in-95 duration-300">
                        {/* Modal Header with Progress */}
                        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-lg">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                            PennPRS Agent Recommendations
                                        </h3>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">
                                            Step {currentStep + 1} of {WIZARD_STEPS.length}: {WIZARD_STEPS[currentStep].label}
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setShowWizardModal(false)}
                                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                                >
                                    <X className="w-5 h-5 text-gray-500" />
                                </button>
                            </div>

                            {/* Step Progress Indicator */}
                            <div className="flex items-center gap-2">
                                {WIZARD_STEPS.map((step, index) => {
                                    const isActive = index === currentStep;
                                    const isCompleted = index < currentStep;
                                    const selectionCount = getStepSelectionCount(step.id);

                                    return (
                                        <div key={step.id} className="flex items-center flex-1">
                                            <div className="flex flex-col items-center flex-1">
                                                <div className={cn(
                                                    "w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all relative",
                                                    isActive
                                                        ? "bg-purple-600 text-white ring-4 ring-purple-100 dark:ring-purple-900/50"
                                                        : isCompleted
                                                            ? "bg-green-500 text-white"
                                                            : "bg-gray-200 dark:bg-gray-700 text-gray-500"
                                                )}>
                                                    {isCompleted ? (
                                                        <Check size={14} strokeWidth={3} />
                                                    ) : (
                                                        index + 1
                                                    )}
                                                    {selectionCount > 0 && !isCompleted && (
                                                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-purple-500 text-white text-[10px] rounded-full flex items-center justify-center">
                                                            {selectionCount}
                                                        </span>
                                                    )}
                                                </div>
                                                <span className={cn(
                                                    "text-[10px] mt-1 font-medium text-center leading-tight hidden sm:block",
                                                    isActive ? "text-purple-600" : "text-gray-400"
                                                )}>
                                                    {step.label}
                                                </span>
                                            </div>
                                            {index < WIZARD_STEPS.length - 1 && (
                                                <div className={cn(
                                                    "h-0.5 flex-1 mx-1 transition-colors",
                                                    isCompleted ? "bg-green-500" : "bg-gray-200 dark:bg-gray-700"
                                                )} />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Modal Body - Step Content */}
                        <div className="p-6 overflow-y-auto max-h-[50vh]">
                            {/* Step 1: Ancestry */}
                            {currentStep === 0 && (
                                <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
                                            <Dna className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 dark:text-white">Target Ancestry</h4>
                                            <p className="text-sm text-gray-500">Select the population group(s) for your study</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                        {ancestryConfig.map((anc) => {
                                            const isSelected = wizardFilters.ancestry.includes(anc.id);
                                            const count = stats.ancestryCounts[anc.id] || 0;
                                            const hasModels = count > 0;

                                            return (
                                                <button
                                                    key={anc.id}
                                                    onClick={() => hasModels && toggleWizardAncestry(anc.id)}
                                                    disabled={!hasModels}
                                                    className={cn(
                                                        "relative p-4 rounded-xl border-2 transition-all duration-200 text-center",
                                                        isSelected
                                                            ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-md"
                                                            : hasModels
                                                                ? "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-purple-300"
                                                                : "border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 opacity-50 cursor-not-allowed"
                                                    )}
                                                >
                                                    <div className={cn(
                                                        "absolute top-2 right-2 w-5 h-5 rounded flex items-center justify-center border-2",
                                                        isSelected ? "bg-purple-500 border-purple-500 text-white" : "border-gray-300 dark:border-gray-600"
                                                    )}>
                                                        {isSelected && <Check size={12} strokeWidth={3} />}
                                                    </div>
                                                    <div className={cn("w-10 h-10 rounded-full mx-auto mb-2 bg-gradient-to-br flex items-center justify-center text-white font-bold text-sm", anc.color)}>
                                                        {anc.shortLabel}
                                                    </div>
                                                    <div className="font-semibold text-sm text-gray-900 dark:text-white mb-1">{anc.label}</div>
                                                    <div className="text-xs text-gray-500">{count} models</div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Step 2: Sample Size */}
                            {currentStep === 1 && (
                                <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                                            <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 dark:text-white">Sample Size Range</h4>
                                            <p className="text-sm text-gray-500">Filter by training data sample size (optional)</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                        {PRESET_RANGES.sampleSize.map((range) => {
                                            const isSelected = wizardFilters.sampleSize.some(r => r.label === range.label);
                                            return (
                                                <button
                                                    key={range.label}
                                                    onClick={() => toggleWizardRange('sampleSize', { ...range, label: range.label })}
                                                    className={cn(
                                                        "p-4 rounded-xl border-2 transition-all duration-200 text-center",
                                                        isSelected
                                                            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md"
                                                            : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-blue-300"
                                                    )}
                                                >
                                                    <div className={cn(
                                                        "w-5 h-5 rounded mx-auto mb-2 flex items-center justify-center border-2",
                                                        isSelected ? "bg-blue-500 border-blue-500 text-white" : "border-gray-300 dark:border-gray-600"
                                                    )}>
                                                        {isSelected && <Check size={12} strokeWidth={3} />}
                                                    </div>
                                                    <div className="font-semibold text-sm text-gray-900 dark:text-white">{range.label}</div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Step 3: AUC */}
                            {currentStep === 2 && (
                                <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">
                                            <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 dark:text-white">AUC Range</h4>
                                            <p className="text-sm text-gray-500">Filter by classification accuracy (optional)</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                        {PRESET_RANGES.auc.map((range) => {
                                            const isSelected = wizardFilters.auc.some(r => r.label === range.label);
                                            return (
                                                <button
                                                    key={range.label}
                                                    onClick={() => toggleWizardRange('auc', { ...range, label: range.label })}
                                                    className={cn(
                                                        "p-4 rounded-xl border-2 transition-all duration-200 text-center",
                                                        isSelected
                                                            ? "border-green-500 bg-green-50 dark:bg-green-900/20 shadow-md"
                                                            : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-green-300"
                                                    )}
                                                >
                                                    <div className={cn(
                                                        "w-5 h-5 rounded mx-auto mb-2 flex items-center justify-center border-2",
                                                        isSelected ? "bg-green-500 border-green-500 text-white" : "border-gray-300 dark:border-gray-600"
                                                    )}>
                                                        {isSelected && <Check size={12} strokeWidth={3} />}
                                                    </div>
                                                    <div className="font-semibold text-sm text-gray-900 dark:text-white">{range.label}</div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Step 4: R² */}
                            {currentStep === 3 && (
                                <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg">
                                            <TrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 dark:text-white">R² Range</h4>
                                            <p className="text-sm text-gray-500">Filter by variance explained (optional)</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                        {PRESET_RANGES.r2.map((range) => {
                                            const isSelected = wizardFilters.r2.some(r => r.label === range.label);
                                            return (
                                                <button
                                                    key={range.label}
                                                    onClick={() => toggleWizardRange('r2', { ...range, label: range.label })}
                                                    className={cn(
                                                        "p-4 rounded-xl border-2 transition-all duration-200 text-center",
                                                        isSelected
                                                            ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 shadow-md"
                                                            : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-indigo-300"
                                                    )}
                                                >
                                                    <div className={cn(
                                                        "w-5 h-5 rounded mx-auto mb-2 flex items-center justify-center border-2",
                                                        isSelected ? "bg-indigo-500 border-indigo-500 text-white" : "border-gray-300 dark:border-gray-600"
                                                    )}>
                                                        {isSelected && <Check size={12} strokeWidth={3} />}
                                                    </div>
                                                    <div className="font-semibold text-sm text-gray-900 dark:text-white">{range.label}</div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Step 5: Variants */}
                            {currentStep === 4 && (
                                <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-teal-100 dark:bg-teal-900/40 rounded-lg">
                                            <Layers className="w-5 h-5 text-teal-600 dark:text-teal-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 dark:text-white">Variants Range</h4>
                                            <p className="text-sm text-gray-500">Filter by number of SNPs (optional)</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                        {PRESET_RANGES.variants.map((range) => {
                                            const isSelected = wizardFilters.variants.some(r => r.label === range.label);
                                            return (
                                                <button
                                                    key={range.label}
                                                    onClick={() => toggleWizardRange('variants', { ...range, label: range.label })}
                                                    className={cn(
                                                        "p-4 rounded-xl border-2 transition-all duration-200 text-center",
                                                        isSelected
                                                            ? "border-teal-500 bg-teal-50 dark:bg-teal-900/20 shadow-md"
                                                            : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-teal-300"
                                                    )}
                                                >
                                                    <div className={cn(
                                                        "w-5 h-5 rounded mx-auto mb-2 flex items-center justify-center border-2",
                                                        isSelected ? "bg-teal-500 border-teal-500 text-white" : "border-gray-300 dark:border-gray-600"
                                                    )}>
                                                        {isSelected && <Check size={12} strokeWidth={3} />}
                                                    </div>
                                                    <div className="font-semibold text-sm text-gray-900 dark:text-white">{range.label}</div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Step 6: Cohorts */}
                            {currentStep === 5 && (
                                <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="p-2 bg-amber-100 dark:bg-amber-900/40 rounded-lg">
                                            <Database className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 dark:text-white">Training Cohorts</h4>
                                            <p className="text-sm text-gray-500">Filter by training/development cohorts (optional)</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                                        {availableCohorts.slice(0, 15).map((cohort) => {
                                            const isSelected = wizardFilters.cohorts.includes(cohort);
                                            const count = models.filter(m => m.dev_cohorts?.includes(cohort)).length;
                                            return (
                                                <button
                                                    key={cohort}
                                                    onClick={() => toggleWizardCohort(cohort)}
                                                    className={cn(
                                                        "p-3 rounded-xl border-2 transition-all duration-200 text-left",
                                                        isSelected
                                                            ? "border-amber-500 bg-amber-50 dark:bg-amber-900/20 shadow-md"
                                                            : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-amber-300"
                                                    )}
                                                >
                                                    <div className="flex items-center gap-2">
                                                        <div className={cn(
                                                            "w-4 h-4 rounded flex items-center justify-center border-2 shrink-0",
                                                            isSelected ? "bg-amber-500 border-amber-500 text-white" : "border-gray-300 dark:border-gray-600"
                                                        )}>
                                                            {isSelected && <Check size={10} strokeWidth={3} />}
                                                        </div>
                                                        <span className="font-medium text-sm text-gray-900 dark:text-white truncate">{cohort}</span>
                                                        <span className="text-xs text-gray-400 ml-auto">({count})</span>
                                                    </div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                    {availableCohorts.length > 15 && (
                                        <p className="text-xs text-gray-400 mt-2 text-center">
                                            Showing top 15 cohorts. Use filters in model grid for more options.
                                        </p>
                                    )}
                                </div>
                            )}

                            {/* Optional indicator */}
                            <div className="flex items-start gap-2 p-3 mt-4 bg-gray-50 dark:bg-gray-900/30 rounded-lg border border-gray-200 dark:border-gray-700">
                                <Info className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                                <p className="text-xs text-gray-500">
                                    This step is optional. You can skip it by clicking "Next Step" without making any selection.
                                </p>
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                                <span>
                                    {Object.values(wizardFilters).flat().length > 0 ? (
                                        <>
                                            <strong className="text-purple-600">{Object.values(wizardFilters).flat().length}</strong> filter(s) selected
                                        </>
                                    ) : (
                                        'No filters selected yet'
                                    )}
                                </span>
                            </div>
                            <div className="flex gap-3">
                                {currentStep > 0 ? (
                                    <button
                                        onClick={handlePrevStep}
                                        className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                                    >
                                        <ChevronLeft className="w-4 h-4" />
                                        Previous
                                    </button>
                                ) : (
                                    <button
                                        onClick={() => setShowWizardModal(false)}
                                        className="px-5 py-2.5 rounded-xl font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                )}

                                {currentStep < WIZARD_STEPS.length - 1 ? (
                                    <button
                                        onClick={handleNextStep}
                                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-semibold transition-all bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white"
                                    >
                                        Next Step
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                ) : (
                                    <button
                                        onClick={handleWizardSubmit}
                                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-semibold transition-all shadow-lg transform active:scale-[0.98] bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 hover:shadow-purple-500/25 text-white"
                                    >
                                        <Bot className="w-4 h-4" />
                                        Get Recommendations
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
