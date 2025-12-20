import React, { useState, useMemo } from 'react';
import ModelCard, { ModelData, getDisplayMetrics } from './ModelCard';
import { Plus, ChevronDown } from 'lucide-react';

interface ModelGridProps {
    models: ModelData[];
    onSelectModel: (modelId: string) => void;
    onTrainNew: () => void;
    onViewDetails: (model: ModelData) => void;
}

export default function ModelGrid({ models, onSelectModel, onTrainNew, onViewDetails }: ModelGridProps) {
    const [visibleCount, setVisibleCount] = useState(9);

    const sortedModels = useMemo(() => {
        return [...models].sort((a, b) => {
            // Priority 0: User Trained / Loading (ALWAYS TOP)
            const isUserA = a.source === "User Trained" || a.source === "PennPRS (Custom)" || a.source === "User Upload" || a.isLoading;
            const isUserB = b.source === "User Trained" || b.source === "PennPRS (Custom)" || b.source === "User Upload" || b.isLoading;

            // Explicit check: if one is user/loading and the other isn't, the user/loading one comes first
            if (isUserA && !isUserB) return -1;
            if (!isUserA && isUserB) return 1;

            if (isUserA && isUserB) {
                // Keep them effectively as-is amongst themselves (or usage time)
                return 0;
            }

            // Priority 1: AUC Magnitude Descending (Using Display Value)
            const { displayAUC: aucA = 0 } = getDisplayMetrics(a);
            const { displayAUC: aucB = 0 } = getDisplayMetrics(b);

            if (aucA !== aucB) {
                return aucB - aucA; // Higher AUC first
            }

            // Tie-breaker 1: R2 Magnitude
            const { displayR2: r2A = 0 } = getDisplayMetrics(a);
            const { displayR2: r2B = 0 } = getDisplayMetrics(b);

            if (r2A !== r2B) return r2B - r2A;

            // Tie-breaker 2: Name
            return a.name.localeCompare(b.name);
        });
    }, [models]);

    const visibleModels = sortedModels.slice(0, visibleCount);
    const hasMore = visibleCount < sortedModels.length;

    const handleLoadMore = () => {
        setVisibleCount(prev => prev + 9);
    };

    return (
        <div className="flex flex-col gap-6 w-full mt-4 pb-12">
            {/* 1. Preview Models Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-in fade-in duration-500">
                {visibleModels.map((model) => (
                    <ModelCard key={model.id} model={model} onSelect={onSelectModel} onViewDetails={onViewDetails} />
                ))}
            </div>

            {/* 2. Load More Button (Between Previews and Train New) */}
            {hasMore && (
                <div className="flex justify-center py-4">
                    <button
                        onClick={handleLoadMore}
                        className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md hover:bg-gray-50 dark:hover:bg-gray-750 transition-all text-sm font-medium text-gray-600 dark:text-gray-300"
                    >
                        <ChevronDown className="w-4 h-4" />
                        <span>Load More Models ({sortedModels.length - visibleCount} remaining)</span>
                    </button>
                </div>
            )}

            {/* 3. Train New Model Card (Always at the bottom) */}
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
