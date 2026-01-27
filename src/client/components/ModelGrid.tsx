import React, { useState, useMemo } from 'react';
import ModelCard, { ModelData, getDisplayMetrics } from './ModelCard';
import { Plus, ChevronDown, Filter, X, Users, Activity, TrendingUp, Layers, Database, FlaskConical, Dna } from 'lucide-react';
import { cn } from '@/lib/utils';

// Filter types
type FilterType = 'ancestry' | 'sampleSize' | 'auc' | 'r2' | 'variants' | 'cohorts' | 'methods';

interface RangeFilter {
    min: number | null;
    max: number | null;
    label: string; // Added label for display
}

interface Filters {
    ancestry: string[];
    sampleSize: RangeFilter[];  // Changed to array for multi-select
    auc: RangeFilter[];         // Changed to array for multi-select
    r2: RangeFilter[];          // Changed to array for multi-select
    variants: RangeFilter[];    // Changed to array for multi-select
    cohorts: string[];
    methods: string[];
}

interface ModelGridProps {
    models: ModelData[];
    onSelectModel: (modelId: string) => void;
    onTrainNew: () => void;
    onViewDetails: (model: ModelData) => void;
    onSaveModel?: (model: ModelData) => void;
    activeAncestry?: string[];
    onAncestryChange?: (ancestries: string[]) => void;
}

const ALL_ANCESTRIES = [
    { code: 'EUR', label: 'European' },
    { code: 'AFR', label: 'African' },
    { code: 'EAS', label: 'East Asian' },
    { code: 'SAS', label: 'South Asian' },
    { code: 'AMR', label: 'Hispanic' },
    { code: 'MIX', label: 'Others' }
];

const FILTER_OPTIONS: { type: FilterType; label: string; icon: React.ReactNode }[] = [
    { type: 'ancestry', label: 'Ancestry', icon: <Dna size={14} /> },
    { type: 'sampleSize', label: 'Sample Size', icon: <Users size={14} /> },
    { type: 'auc', label: 'AUC', icon: <Activity size={14} /> },
    { type: 'r2', label: 'R²', icon: <TrendingUp size={14} /> },
    { type: 'variants', label: 'Variants', icon: <Layers size={14} /> },
    { type: 'cohorts', label: 'Cohorts', icon: <Database size={14} /> },
    { type: 'methods', label: 'PRS Methods', icon: <FlaskConical size={14} /> },
];

function formatNumber(n: number): string {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(0)}k`;
    return n.toLocaleString();
}



// Preset range options for each filter type
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


const FILTER_LABELS: Record<'sampleSize' | 'auc' | 'r2' | 'variants', string> = {
    sampleSize: 'Sample Size',
    auc: 'AUC',
    r2: 'R²',
    variants: 'Variants',
};

// Updated interface for multi-select range filter
interface RangeFilterDropdownProps {
    type: 'sampleSize' | 'auc' | 'r2' | 'variants';
    range: { min: number; max: number } | null;
    selectedRanges: RangeFilter[];
    onToggle: (range: RangeFilter) => void;
}

function RangeFilterDropdown({ type, range, selectedRanges, onToggle }: RangeFilterDropdownProps) {
    const presets = PRESET_RANGES[type];
    const label = FILTER_LABELS[type];

    const isSelected = (presetLabel: string) => {
        return selectedRanges.some(r => r.label === presetLabel);
    };

    return (
        <div className="py-1">
            <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100 dark:border-gray-700">
                Select {label} Range
            </div>
            {range && (
                <div className="px-4 py-2 text-xs text-gray-400 border-b border-gray-100 dark:border-gray-700">
                    Data range: {type === 'auc' ? range.min.toFixed(3) : type === 'r2' ? range.min.toFixed(4) : formatNumber(range.min)} - {type === 'auc' ? range.max.toFixed(3) : type === 'r2' ? range.max.toFixed(4) : formatNumber(range.max)}
                </div>
            )}
            {presets.map((preset, index) => {
                const selected = isSelected(preset.label);
                return (
                    <button
                        key={index}
                        onClick={() => onToggle({ min: preset.min, max: preset.max, label: preset.label })}
                        className={cn(
                            "w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center gap-3",
                            selected
                                ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                                : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                        )}
                    >
                        <div className={cn(
                            "w-4 h-4 rounded border flex items-center justify-center transition-colors",
                            selected
                                ? "bg-blue-600 border-blue-600"
                                : "border-gray-300 dark:border-gray-600"
                        )}>
                            {selected && (
                                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                            )}
                        </div>
                        <span>{preset.label}</span>
                    </button>
                );
            })}
        </div>
    );
}


export default function ModelGrid({ models, onSelectModel, onTrainNew, onViewDetails, onSaveModel, activeAncestry, onAncestryChange }: ModelGridProps) {
    const [visibleCount, setVisibleCount] = useState(9);
    const [openFilterMenu, setOpenFilterMenu] = useState<FilterType | null>(null);

    // Local filter state (synced with activeAncestry for ancestry)
    const [filters, setFilters] = useState<Filters>({
        ancestry: activeAncestry || [],
        sampleSize: [],
        auc: [],
        r2: [],
        variants: [],
        cohorts: [],
        methods: [],
    });

    // Pending filter state - for selections not yet applied
    const [pendingFilters, setPendingFilters] = useState<Filters>({
        ancestry: [],
        sampleSize: [],
        auc: [],
        r2: [],
        variants: [],
        cohorts: [],
        methods: [],
    });

    // Initialize pending filters when opening a dropdown
    const openFilterDropdown = (type: FilterType) => {
        if (openFilterMenu === type) {
            setOpenFilterMenu(null);
        } else {
            // Copy current filter values to pending
            setPendingFilters(prev => ({
                ...prev,
                [type]: type === 'ancestry' || type === 'cohorts' || type === 'methods'
                    ? [...filters[type]]
                    : [...filters[type]]
            }));
            setOpenFilterMenu(type);
        }
    };

    // Apply pending filters
    const applyFilters = (type: FilterType) => {
        setFilters(prev => ({
            ...prev,
            [type]: pendingFilters[type]
        }));
        if (type === 'ancestry') {
            onAncestryChange?.(pendingFilters.ancestry);
        }
        setOpenFilterMenu(null);
    };

    // Cancel and close dropdown
    const cancelFilters = () => {
        setOpenFilterMenu(null);
    };

    // Sync ancestry filter with parent component
    React.useEffect(() => {
        if (activeAncestry) {
            setFilters(prev => ({ ...prev, ancestry: activeAncestry }));
        }
    }, [activeAncestry]);

    // Compute available options for categorical filters
    const availableOptions = useMemo(() => {
        const cohortSet = new Set<string>();
        const methodSet = new Set<string>();

        models.forEach(m => {
            if (m.dev_cohorts) {
                m.dev_cohorts.split(',').forEach(c => {
                    const trimmed = c.trim();
                    if (trimmed) cohortSet.add(trimmed);
                });
            }
            if (m.method) {
                methodSet.add(m.method);
            }
        });

        return {
            cohorts: Array.from(cohortSet).sort(),
            methods: Array.from(methodSet).sort(),
        };
    }, [models]);

    // Compute ranges for numeric filters
    const numericRanges = useMemo(() => {
        const sampleSizes = models.map(m => m.sample_size).filter((s): s is number => s !== undefined && s > 0);
        const aucValues = models.map(m => m.metrics?.AUC).filter((a): a is number => a !== undefined && a > 0);
        const r2Values = models.map(m => m.metrics?.R2).filter((r): r is number => r !== undefined && r > 0);
        const variantCounts = models.map(m => m.num_variants).filter((v): v is number => v !== undefined && v > 0);

        return {
            sampleSize: sampleSizes.length > 0 ? { min: Math.min(...sampleSizes), max: Math.max(...sampleSizes) } : null,
            auc: aucValues.length > 0 ? { min: Math.min(...aucValues), max: Math.max(...aucValues) } : null,
            r2: r2Values.length > 0 ? { min: Math.min(...r2Values), max: Math.max(...r2Values) } : null,
            variants: variantCounts.length > 0 ? { min: Math.min(...variantCounts), max: Math.max(...variantCounts) } : null,
        };
    }, [models]);

    // Helper for Ancestry Matching (Normalized)
    const checkAncestryMatch = (ancestryString: string, targets: string[]) => {
        if (!ancestryString) return false;
        // Ancestry Map for normalization (Align with ModelCard)
        const ancestryMap: Record<string, string> = {
            'EUR': 'European', 'AFR': 'African', 'EAS': 'East Asian',
            'SAS': 'South Asian', 'AMR': 'Hispanic', 'MIX': 'Multi-ancestry'
        };

        const normalized = ancestryString.toLowerCase();
        return targets.some(t => {
            const targetCode = t.toUpperCase(); // e.g. EUR
            const targetName = ancestryMap[targetCode] || t; // e.g. European

            // check if the model's ancestry string contains either the code or the full name
            return normalized.includes(targetCode.toLowerCase()) ||
                normalized.includes(targetName.toLowerCase());
        });
    };

    // Filter Logic: Apply ALL filters
    const filteredAndSortedModels = useMemo(() => {
        let processed = [...models];

        // 1. Ancestry Filter
        if (filters.ancestry.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                return checkAncestryMatch(m.ancestry || "", filters.ancestry);
            });
        }

        // 2. Sample Size Filter (multi-select: match ANY selected range)
        if (filters.sampleSize.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                if (!m.sample_size) return false;
                return filters.sampleSize.some(range => {
                    const minOk = range.min === null || m.sample_size! >= range.min;
                    const maxOk = range.max === null || m.sample_size! <= range.max;
                    return minOk && maxOk;
                });
            });
        }

        // 3. AUC Filter (multi-select: match ANY selected range)
        if (filters.auc.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                const auc = m.metrics?.AUC;
                if (!auc) return false;
                return filters.auc.some(range => {
                    const minOk = range.min === null || auc >= range.min;
                    const maxOk = range.max === null || auc <= range.max;
                    return minOk && maxOk;
                });
            });
        }

        // 4. R² Filter (multi-select: match ANY selected range)
        if (filters.r2.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                const r2 = m.metrics?.R2;
                if (!r2) return false;
                return filters.r2.some(range => {
                    const minOk = range.min === null || r2 >= range.min;
                    const maxOk = range.max === null || r2 <= range.max;
                    return minOk && maxOk;
                });
            });
        }

        // 5. Variants Filter (multi-select: match ANY selected range)
        if (filters.variants.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                if (!m.num_variants) return false;
                return filters.variants.some(range => {
                    const minOk = range.min === null || m.num_variants! >= range.min;
                    const maxOk = range.max === null || m.num_variants! <= range.max;
                    return minOk && maxOk;
                });
            });
        }

        // 6. Cohorts Filter
        if (filters.cohorts.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                if (!m.dev_cohorts) return false;
                const modelCohorts = m.dev_cohorts.split(',').map(c => c.trim());
                return filters.cohorts.some(c => modelCohorts.includes(c));
            });
        }

        // 7. Methods Filter
        if (filters.methods.length > 0) {
            processed = processed.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;
                if (!m.method) return false;
                return filters.methods.includes(m.method);
            });
        }

        // Sort
        return processed.sort((a, b) => {
            const isUserA = a.source === "User Trained" || a.source === "PennPRS (Custom)" || a.source === "User Upload" || a.isLoading;
            const isUserB = b.source === "User Trained" || b.source === "PennPRS (Custom)" || b.source === "User Upload" || b.isLoading;
            if (isUserA && !isUserB) return -1;
            if (!isUserA && isUserB) return 1;
            if (isUserA && isUserB) return 0;

            const { displayAUC: aucA = 0 } = getDisplayMetrics(a, filters.ancestry);
            const { displayAUC: aucB = 0 } = getDisplayMetrics(b, filters.ancestry);
            if (aucA !== aucB) return aucB - aucA;

            const { displayR2: r2A = 0 } = getDisplayMetrics(a, filters.ancestry);
            const { displayR2: r2B = 0 } = getDisplayMetrics(b, filters.ancestry);
            if (r2A !== r2B) return r2B - r2A;

            return a.name.localeCompare(b.name);
        });
    }, [models, filters]);

    const visibleModels = filteredAndSortedModels.slice(0, visibleCount);
    const hasMore = visibleCount < filteredAndSortedModels.length;

    // Toggle ancestry in pending filters
    const togglePendingAncestry = (id: string) => {
        setPendingFilters(prev => ({
            ...prev,
            ancestry: prev.ancestry.includes(id)
                ? prev.ancestry.filter(c => c !== id)
                : [...prev.ancestry, id]
        }));
    };

    // Toggle categorical in pending filters (cohorts, methods)
    const togglePendingCategorical = (type: 'cohorts' | 'methods', value: string) => {
        setPendingFilters(prev => ({
            ...prev,
            [type]: prev[type].includes(value)
                ? prev[type].filter(v => v !== value)
                : [...prev[type], value]
        }));
    };

    // Toggle range filter in pending filters
    const togglePendingRange = (type: 'sampleSize' | 'auc' | 'r2' | 'variants', range: RangeFilter) => {
        setPendingFilters(prev => {
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

    // Toggle ancestry filter (for removing from chips)
    const toggleAncestry = (id: string) => {
        const newAncestry = filters.ancestry.includes(id)
            ? filters.ancestry.filter(c => c !== id)
            : [...filters.ancestry, id];
        setFilters(prev => ({ ...prev, ancestry: newAncestry }));
        onAncestryChange?.(newAncestry);
    };

    // Toggle categorical filter (for removing from chips)
    const toggleCategoricalFilter = (type: 'cohorts' | 'methods', value: string) => {
        setFilters(prev => ({
            ...prev,
            [type]: prev[type].includes(value)
                ? prev[type].filter(v => v !== value)
                : [...prev[type], value]
        }));
    };

    // Toggle range filter (for removing from chips)
    const toggleRangeFilter = (type: 'sampleSize' | 'auc' | 'r2' | 'variants', range: RangeFilter) => {
        setFilters(prev => {
            const currentRanges = prev[type];
            const existingIndex = currentRanges.findIndex(r => r.label === range.label);
            if (existingIndex >= 0) {
                // Remove if already selected
                return {
                    ...prev,
                    [type]: currentRanges.filter((_, i) => i !== existingIndex)
                };
            } else {
                // Add new range
                return {
                    ...prev,
                    [type]: [...currentRanges, range]
                };
            }
        });
    };

    // Clear a specific filter
    const clearFilter = (type: FilterType) => {
        if (type === 'ancestry') {
            setFilters(prev => ({ ...prev, ancestry: [] }));
            onAncestryChange?.([]);
        } else {
            setFilters(prev => ({ ...prev, [type]: [] }));
        }
    };

    // Remove a single range from a range filter
    const removeRangeFilter = (type: 'sampleSize' | 'auc' | 'r2' | 'variants', label: string) => {
        setFilters(prev => ({
            ...prev,
            [type]: prev[type].filter(r => r.label !== label)
        }));
    };

    // Clear all filters
    const clearAllFilters = () => {
        setFilters({
            ancestry: [],
            sampleSize: [],
            auc: [],
            r2: [],
            variants: [],
            cohorts: [],
            methods: [],
        });
        onAncestryChange?.([]);
    };

    // Check if any filter is active
    const hasActiveFilters = filters.ancestry.length > 0 ||
        filters.sampleSize.length > 0 ||
        filters.auc.length > 0 ||
        filters.r2.length > 0 ||
        filters.variants.length > 0 ||
        filters.cohorts.length > 0 ||
        filters.methods.length > 0;

    // Get active filter count
    const activeFilterCount = (filters.ancestry.length > 0 ? 1 : 0) +
        (filters.sampleSize.length > 0 ? 1 : 0) +
        (filters.auc.length > 0 ? 1 : 0) +
        (filters.r2.length > 0 ? 1 : 0) +
        (filters.variants.length > 0 ? 1 : 0) +
        (filters.cohorts.length > 0 ? 1 : 0) +
        (filters.methods.length > 0 ? 1 : 0);

    // Render filter chip based on type
    const renderFilterChip = (type: FilterType) => {
        const option = FILTER_OPTIONS.find(o => o.type === type)!;

        if (type === 'ancestry' && filters.ancestry.length > 0) {
            return filters.ancestry.map(anc => (
                <button
                    key={`ancestry-${anc}`}
                    onClick={() => toggleAncestry(anc)}
                    className="group flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-purple-50 hover:bg-red-50 text-purple-700 hover:text-red-700 border border-purple-200 hover:border-red-200 transition-colors"
                    title="Click to remove"
                >
                    <Dna size={14} />
                    {ALL_ANCESTRIES.find(a => a.code === anc)?.label || anc}
                    <X size={14} className="opacity-50 group-hover:opacity-100" />
                </button>
            ));
        }

        if (type === 'cohorts' && filters.cohorts.length > 0) {
            return filters.cohorts.map(cohort => (
                <button
                    key={`cohort-${cohort}`}
                    onClick={() => toggleCategoricalFilter('cohorts', cohort)}
                    className="group flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-amber-50 hover:bg-red-50 text-amber-700 hover:text-red-700 border border-amber-200 hover:border-red-200 transition-colors"
                    title="Click to remove"
                >
                    <Database size={14} />
                    {cohort}
                    <X size={14} className="opacity-50 group-hover:opacity-100" />
                </button>
            ));
        }

        if (type === 'methods' && filters.methods.length > 0) {
            return filters.methods.map(method => (
                <button
                    key={`method-${method}`}
                    onClick={() => toggleCategoricalFilter('methods', method)}
                    className="group flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-rose-50 hover:bg-red-50 text-rose-700 hover:text-red-700 border border-rose-200 hover:border-red-200 transition-colors"
                    title="Click to remove"
                >
                    <FlaskConical size={14} />
                    {method}
                    <X size={14} className="opacity-50 group-hover:opacity-100" />
                </button>
            ));
        }

        // Range filters - display each selected range as a chip
        const rangeFilterConfig: { [key in 'sampleSize' | 'auc' | 'r2' | 'variants']: { color: string; bgColor: string; textColor: string; borderColor: string; icon: React.ReactNode } } = {
            sampleSize: { color: 'blue', bgColor: 'bg-blue-50', textColor: 'text-blue-700', borderColor: 'border-blue-200', icon: <Users size={14} /> },
            auc: { color: 'green', bgColor: 'bg-green-50', textColor: 'text-green-700', borderColor: 'border-green-200', icon: <Activity size={14} /> },
            r2: { color: 'indigo', bgColor: 'bg-indigo-50', textColor: 'text-indigo-700', borderColor: 'border-indigo-200', icon: <TrendingUp size={14} /> },
            variants: { color: 'teal', bgColor: 'bg-teal-50', textColor: 'text-teal-700', borderColor: 'border-teal-200', icon: <Layers size={14} /> },
        };

        if (type in rangeFilterConfig) {
            const filterRanges = filters[type as keyof typeof rangeFilterConfig];
            if (filterRanges.length > 0) {
                const cfg = rangeFilterConfig[type as keyof typeof rangeFilterConfig];
                return filterRanges.map((range) => (
                    <button
                        key={`range-${type}-${range.label}`}
                        onClick={() => removeRangeFilter(type as 'sampleSize' | 'auc' | 'r2' | 'variants', range.label)}
                        className={cn(
                            "group flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border",
                            cfg.bgColor, cfg.textColor, cfg.borderColor,
                            "hover:bg-red-50 hover:text-red-700 hover:border-red-200"
                        )}
                        title="Click to remove"
                    >
                        {cfg.icon}
                        {option.label}: {range.label}
                        <X size={14} className="opacity-50 group-hover:opacity-100" />
                    </button>
                ));
            }
        }

        return null;
    };

    return (
        <div className="flex flex-col gap-6 w-full mt-4 pb-12">
            {/* Filter Controls */}
            <div className="flex flex-wrap items-center gap-2 mb-2 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
                    <Filter size={16} className="text-gray-500" />
                    <span>Filter:</span>
                    {activeFilterCount > 0 && (
                        <span className="px-1.5 py-0.5 text-xs bg-blue-600 text-white rounded-full">{activeFilterCount}</span>
                    )}
                </div>

                {/* Active Filter Chips */}
                {FILTER_OPTIONS.map(opt => renderFilterChip(opt.type))}

                {/* Add Filter Buttons */}
                {FILTER_OPTIONS.map(opt => {
                    // Skip if filter already has values
                    if (opt.type === 'ancestry' && filters.ancestry.length > 0) return null;
                    if (opt.type === 'cohorts' && filters.cohorts.length > 0) return null;
                    if (opt.type === 'methods' && filters.methods.length > 0) return null;
                    if (opt.type === 'sampleSize' && filters.sampleSize.length > 0) return null;
                    if (opt.type === 'auc' && filters.auc.length > 0) return null;
                    if (opt.type === 'r2' && filters.r2.length > 0) return null;
                    if (opt.type === 'variants' && filters.variants.length > 0) return null;

                    return (
                        <div key={opt.type} className="relative">
                            <button
                                onClick={() => openFilterDropdown(opt.type)}
                                className={cn(
                                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-dashed transition-colors",
                                    openFilterMenu === opt.type
                                        ? "bg-gray-100 dark:bg-gray-700 border-gray-400 text-gray-900 dark:text-gray-100"
                                        : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 border-gray-300 dark:border-gray-600 hover:border-gray-400"
                                )}
                            >
                                <Plus size={14} />
                                {opt.label}
                            </button>

                            {/* Dropdown Menus */}
                            {openFilterMenu === opt.type && (
                                <>
                                    <div className="fixed inset-0 z-10" onClick={cancelFilters}></div>
                                    <div className="absolute top-full left-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-20 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                                        {/* Ancestry Dropdown */}
                                        {opt.type === 'ancestry' && (
                                            <div className="flex flex-col">
                                                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100 dark:border-gray-700">
                                                    Select Ancestry
                                                </div>
                                                <div className="max-h-64 overflow-y-auto">
                                                    {ALL_ANCESTRIES.map(anc => {
                                                        const count = models.filter(m => checkAncestryMatch(m.ancestry || "", [anc.code])).length;
                                                        const isSelected = pendingFilters.ancestry.includes(anc.code);
                                                        return (
                                                            <button
                                                                key={anc.code}
                                                                onClick={() => togglePendingAncestry(anc.code)}
                                                                className={cn(
                                                                    "w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center gap-3",
                                                                    isSelected
                                                                        ? "bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300"
                                                                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                                                                )}
                                                            >
                                                                <div className={cn(
                                                                    "w-4 h-4 rounded border flex items-center justify-center transition-colors flex-shrink-0",
                                                                    isSelected
                                                                        ? "bg-purple-600 border-purple-600"
                                                                        : "border-gray-300 dark:border-gray-600"
                                                                )}>
                                                                    {isSelected && (
                                                                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                                        </svg>
                                                                    )}
                                                                </div>
                                                                <span className="flex-1">{anc.label}</span>
                                                                <span className={`text-xs px-2 py-0.5 rounded-full ${count > 0 ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'}`}>
                                                                    {count}
                                                                </span>
                                                            </button>
                                                        );
                                                    })}
                                                </div>
                                                {/* Apply/Cancel Buttons */}
                                                <div className="flex gap-2 p-3 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                                                    <button
                                                        onClick={cancelFilters}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors border border-gray-200 dark:border-gray-600"
                                                    >
                                                        Cancel
                                                    </button>
                                                    <button
                                                        onClick={() => applyFilters('ancestry')}
                                                        disabled={pendingFilters.ancestry.length === 0}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                    >
                                                        Apply ({pendingFilters.ancestry.length})
                                                    </button>
                                                </div>
                                            </div>
                                        )}

                                        {/* Range Filter Dropdowns */}
                                        {(opt.type === 'sampleSize' || opt.type === 'auc' || opt.type === 'r2' || opt.type === 'variants') && (
                                            <div className="flex flex-col">
                                                <RangeFilterDropdown
                                                    type={opt.type}
                                                    range={numericRanges[opt.type]}
                                                    selectedRanges={pendingFilters[opt.type]}
                                                    onToggle={(range) => togglePendingRange(opt.type as 'sampleSize' | 'auc' | 'r2' | 'variants', range)}
                                                />
                                                {/* Apply/Cancel Buttons */}
                                                <div className="flex gap-2 p-3 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                                                    <button
                                                        onClick={cancelFilters}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors border border-gray-200 dark:border-gray-600"
                                                    >
                                                        Cancel
                                                    </button>
                                                    <button
                                                        onClick={() => applyFilters(opt.type)}
                                                        disabled={pendingFilters[opt.type].length === 0}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                    >
                                                        Apply ({pendingFilters[opt.type].length})
                                                    </button>
                                                </div>
                                            </div>
                                        )}

                                        {/* Cohorts Dropdown */}
                                        {opt.type === 'cohorts' && (
                                            <div className="flex flex-col">
                                                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100 dark:border-gray-700">
                                                    Select Cohorts
                                                </div>
                                                <div className="max-h-64 overflow-y-auto">
                                                    {availableOptions.cohorts
                                                        .map(cohort => ({
                                                            cohort,
                                                            count: models.filter(m => m.dev_cohorts?.includes(cohort)).length
                                                        }))
                                                        .sort((a, b) => b.count - a.count)
                                                        .map(({ cohort, count }) => {
                                                            const isSelected = pendingFilters.cohorts.includes(cohort);
                                                            return (
                                                                <button
                                                                    key={cohort}
                                                                    onClick={() => togglePendingCategorical('cohorts', cohort)}
                                                                    className={cn(
                                                                        "w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center gap-3",
                                                                        isSelected
                                                                            ? "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300"
                                                                            : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                                                                    )}
                                                                >
                                                                    <div className={cn(
                                                                        "w-4 h-4 rounded border flex items-center justify-center transition-colors flex-shrink-0",
                                                                        isSelected
                                                                            ? "bg-amber-600 border-amber-600"
                                                                            : "border-gray-300 dark:border-gray-600"
                                                                    )}>
                                                                        {isSelected && (
                                                                            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                                            </svg>
                                                                        )}
                                                                    </div>
                                                                    <span className="flex-1 truncate">{cohort}</span>
                                                                    <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 ml-2">{count}</span>
                                                                </button>
                                                            );
                                                        })}
                                                    {availableOptions.cohorts.length === 0 && (
                                                        <div className="px-4 py-3 text-sm text-gray-400 text-center italic">No cohort data</div>
                                                    )}
                                                </div>
                                                {/* Apply/Cancel Buttons */}
                                                <div className="flex gap-2 p-3 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                                                    <button
                                                        onClick={cancelFilters}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors border border-gray-200 dark:border-gray-600"
                                                    >
                                                        Cancel
                                                    </button>
                                                    <button
                                                        onClick={() => applyFilters('cohorts')}
                                                        disabled={pendingFilters.cohorts.length === 0}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                    >
                                                        Apply ({pendingFilters.cohorts.length})
                                                    </button>
                                                </div>
                                            </div>
                                        )}

                                        {/* Methods Dropdown */}
                                        {opt.type === 'methods' && (
                                            <div className="flex flex-col">
                                                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100 dark:border-gray-700">
                                                    Select PRS Methods
                                                </div>
                                                <div className="max-h-64 overflow-y-auto">
                                                    {availableOptions.methods
                                                        .map(method => ({
                                                            method,
                                                            count: models.filter(m => m.method === method).length
                                                        }))
                                                        .sort((a, b) => b.count - a.count)
                                                        .map(({ method, count }) => {
                                                            const isSelected = pendingFilters.methods.includes(method);
                                                            return (
                                                                <button
                                                                    key={method}
                                                                    onClick={() => togglePendingCategorical('methods', method)}
                                                                    className={cn(
                                                                        "w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center gap-3",
                                                                        isSelected
                                                                            ? "bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300"
                                                                            : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                                                                    )}
                                                                >
                                                                    <div className={cn(
                                                                        "w-4 h-4 rounded border flex items-center justify-center transition-colors flex-shrink-0",
                                                                        isSelected
                                                                            ? "bg-rose-600 border-rose-600"
                                                                            : "border-gray-300 dark:border-gray-600"
                                                                    )}>
                                                                        {isSelected && (
                                                                            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                                            </svg>
                                                                        )}
                                                                    </div>
                                                                    <span className="flex-1 truncate">{method}</span>
                                                                    <span className="text-xs px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 ml-2">{count}</span>
                                                                </button>
                                                            );
                                                        })}
                                                    {availableOptions.methods.length === 0 && (
                                                        <div className="px-4 py-3 text-sm text-gray-400 text-center italic">No method data</div>
                                                    )}
                                                </div>
                                                {/* Apply/Cancel Buttons */}
                                                <div className="flex gap-2 p-3 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                                                    <button
                                                        onClick={cancelFilters}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors border border-gray-200 dark:border-gray-600"
                                                    >
                                                        Cancel
                                                    </button>
                                                    <button
                                                        onClick={() => applyFilters('methods')}
                                                        disabled={pendingFilters.methods.length === 0}
                                                        className="flex-1 px-3 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                    >
                                                        Apply ({pendingFilters.methods.length})
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </>
                            )}
                        </div>
                    );
                })}

                {/* Clear All Button */}
                {hasActiveFilters && (
                    <button
                        onClick={clearAllFilters}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors"
                    >
                        <X size={14} />
                        Clear All
                    </button>
                )}
            </div>

            {/* 1. Preview Models Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-in fade-in duration-500">
                {visibleModels.map((model) => (
                    <ModelCard
                        key={model.id}
                        model={model}
                        onSelect={onSelectModel}
                        onViewDetails={onViewDetails}
                        onSaveModel={onSaveModel}
                        activeAncestry={activeAncestry}
                    />
                ))}

                {visibleModels.length === 0 && (
                    <div className="col-span-full py-12 flex flex-col items-center justify-center text-center p-8 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700">
                        <Filter className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">No matching models found</h3>
                        <p className="text-gray-500 dark:text-gray-400 max-w-sm mt-2">
                            None of the fetched models match your current filters. Try removing some filters or viewing all models.
                        </p>
                        <button
                            onClick={clearAllFilters}
                            className="mt-6 text-blue-600 hover:text-blue-700 font-medium text-sm"
                        >
                            Clear all filters
                        </button>
                    </div>
                )}
            </div>

            {/* 2. Load More Button */}
            {hasMore && (
                <div className="flex justify-center py-4">
                    <button
                        onClick={() => setVisibleCount(prev => prev + 9)}
                        className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md hover:bg-gray-50 dark:hover:bg-gray-750 transition-all text-sm font-medium text-gray-600 dark:text-gray-300"
                    >
                        <ChevronDown className="w-4 h-4" />
                        <span>Load More Models ({filteredAndSortedModels.length - visibleCount} remaining)</span>
                    </button>
                </div>
            )}

            {/* 3. Train New Model Card */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <button
                    onClick={onTrainNew}
                    className="group flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900/50 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-all p-8 min-h-[300px]"
                >
                    <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <Plus className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Train New Model</h3>
                    <p className="text-sm text-gray-500 text-center">
                        Use PennPRS API to train a custom model with your parameters
                    </p>
                </button>
            </div>
        </div>
    );
}
