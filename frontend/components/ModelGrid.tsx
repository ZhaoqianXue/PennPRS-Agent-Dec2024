import React, { useState, useMemo } from 'react';
import ModelCard, { ModelData, getDisplayMetrics } from './ModelCard';
import { Plus, ChevronDown, Filter, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModelGridProps {
    models: ModelData[];
    onSelectModel: (modelId: string) => void;
    onTrainNew: () => void;
    onViewDetails: (model: ModelData) => void;
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

export default function ModelGrid({ models, onSelectModel, onTrainNew, onViewDetails, activeAncestry, onAncestryChange }: ModelGridProps) {
    const [visibleCount, setVisibleCount] = useState(9);
    const [isFilterMenuOpen, setIsFilterMenuOpen] = useState(false);

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

    // Filter Logic: HARD FILTER
    const filteredAndSortedModels = useMemo(() => {
        let processed = [...models];

        // 1. Hard Filter
        if (activeAncestry && activeAncestry.length > 0) {
            processed = processed.filter(m => {
                // Keep if user trained (always visible)
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload" || m.isLoading) return true;

                // STRICTLY check only model.ancestry (Training Ancestry)
                // We deliberately do NOT use getDisplayMetrics here because it checks performance_detailed (Evaluation)
                return checkAncestryMatch(m.ancestry || "", activeAncestry);
            });
        }

        // 2. Sort
        return processed.sort((a, b) => {
            // Priority 0: User Trained / Loading (ALWAYS TOP)
            const isUserA = a.source === "User Trained" || a.source === "PennPRS (Custom)" || a.source === "User Upload" || a.isLoading;
            const isUserB = b.source === "User Trained" || b.source === "PennPRS (Custom)" || b.source === "User Upload" || b.isLoading;
            if (isUserA && !isUserB) return -1;
            if (!isUserA && isUserB) return 1;
            if (isUserA && isUserB) return 0;

            // Priority 1: AUC Magnitude (Matched - optimized by getDisplayMetrics)
            const { displayAUC: aucA = 0 } = getDisplayMetrics(a, activeAncestry);
            const { displayAUC: aucB = 0 } = getDisplayMetrics(b, activeAncestry);
            if (aucA !== aucB) return aucB - aucA;

            // Tie-breaker: R2
            const { displayR2: r2A = 0 } = getDisplayMetrics(a, activeAncestry);
            const { displayR2: r2B = 0 } = getDisplayMetrics(b, activeAncestry);
            if (r2A !== r2B) return r2B - r2A;

            return a.name.localeCompare(b.name);
        });
    }, [models, activeAncestry]);

    const visibleModels = filteredAndSortedModels.slice(0, visibleCount);
    const hasMore = visibleCount < filteredAndSortedModels.length;

    const toggleAncestry = (id: string) => {
        if (!onAncestryChange) return;
        const current = activeAncestry || [];
        if (current.includes(id)) {
            onAncestryChange(current.filter(c => c !== id));
        } else {
            onAncestryChange([...current, id]);
        }
    };

    return (
        <div className="flex flex-col gap-6 w-full mt-4 pb-12">
            {/* 0. Filter Controls */}
            <div className="flex flex-wrap items-center gap-3 mb-2 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
                    <Filter size={16} className="text-gray-500" />
                    <span>Filter:</span>
                </div>

                {/* Active Chips */}
                {activeAncestry && activeAncestry.map(anc => (
                    <button
                        key={anc}
                        onClick={() => toggleAncestry(anc)}
                        className="group flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-blue-50 hover:bg-red-50 text-blue-700 hover:text-red-700 border border-blue-200 hover:border-red-200 transition-colors"
                        title="Click to remove filter"
                    >
                        {ALL_ANCESTRIES.find(a => a.id === anc)?.label || anc}
                        <X size={14} className="opacity-50 group-hover:opacity-100" />
                    </button>
                ))}

                {/* Add Filter Button */}
                <div className="relative">
                    <button
                        onClick={() => setIsFilterMenuOpen(!isFilterMenuOpen)}
                        className={cn(
                            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-dashed transition-colors",
                            isFilterMenuOpen
                                ? "bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-500 text-gray-900 dark:text-gray-100"
                                : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 border-gray-300 dark:border-gray-600 hover:border-gray-400"
                        )}
                    >
                        <Plus size={14} />
                        Add Ancestry
                    </button>

                    {/* Dropdown */}
                    {isFilterMenuOpen && (
                        <>
                            <div className="fixed inset-0 z-10" onClick={() => setIsFilterMenuOpen(false)}></div>
                            <div className="absolute top-full left-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 z-20 py-1 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                                {ALL_ANCESTRIES.filter(a => !activeAncestry?.includes(a.id)).map(anc => {
                                    // Count matching models for this ancestry
                                    const count = models.filter(m => checkAncestryMatch(m.ancestry || "", [anc.id])).length;

                                    return (
                                        <button
                                            key={anc.id}
                                            onClick={() => {
                                                toggleAncestry(anc.id);
                                                setIsFilterMenuOpen(false);
                                            }}
                                            className="w-full text-left px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-between group"
                                        >
                                            <span>{anc.label}</span>
                                            <div className="flex items-center gap-2">
                                                <span className={`text-xs px-1.5 py-0.5 rounded-full ${count > 0 ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-500'}`}>
                                                    {count}
                                                </span>
                                                <span className="text-xs text-gray-400 font-mono opacity-0 group-hover:opacity-100 transition-opacity">{anc.id}</span>
                                            </div>
                                        </button>
                                    );
                                })}
                                {ALL_ANCESTRIES.filter(a => !activeAncestry?.includes(a.id)).length === 0 && (
                                    <div className="px-4 py-2 text-xs text-gray-400 text-center italic">
                                        All selected
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* 1. Preview Models Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-in fade-in duration-500">
                {visibleModels.map((model) => (
                    <ModelCard
                        key={model.id}
                        model={model}
                        onSelect={onSelectModel}
                        onViewDetails={onViewDetails}
                        activeAncestry={activeAncestry}
                    />
                ))}

                {visibleModels.length === 0 && (
                    <div className="col-span-full py-12 flex flex-col items-center justify-center text-center p-8 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700">
                        <Filter className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">No matching models found</h3>
                        <p className="text-gray-500 dark:text-gray-400 max-w-sm mt-2">
                            None of the fetched models match your current ancestry filters. Try removing some filters or viewing "All".
                        </p>
                        <button
                            onClick={() => onAncestryChange?.([])}
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
