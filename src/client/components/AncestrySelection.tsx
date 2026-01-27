import React, { useState, useEffect } from 'react';
import { Check, Dna, ArrowRight, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProgressBar } from './ProgressBar';

interface AncestrySelectionProps {
    onSelect: (ancestries: string[]) => void;
    searchProgress: { status: string; total: number; fetched: number; current_action: string } | null;
    isSearchComplete: boolean;
    activeAncestry?: string[]; // Added support for pre-selected ancestry
}

const ancestries = [
    { id: 'EUR', label: 'European', color: 'bg-blue-50 text-blue-700 border-blue-200' },
    { id: 'AFR', label: 'African', color: 'bg-purple-50 text-purple-700 border-purple-200' },
    { id: 'EAS', label: 'East Asian', color: 'bg-green-50 text-green-700 border-green-200' },
    { id: 'SAS', label: 'South Asian', color: 'bg-orange-50 text-orange-700 border-orange-200' },
    { id: 'AMR', label: 'Hispanic', color: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
    { id: 'MIX', label: 'Others', color: 'bg-pink-50 text-pink-700 border-pink-200' }, // Renamed to Others
];

export default function AncestrySelection({ onSelect, searchProgress, isSearchComplete, activeAncestry }: AncestrySelectionProps) {
    const [selected, setSelected] = useState<string[]>(activeAncestry || []);
    const [isSubmitted, setIsSubmitted] = useState(false);

    // Sync with prop if it changes externally
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

    const handleConfirm = () => {
        setIsSubmitted(true);
        onSelect(selected);
    };

    // View State: Waiting for search to complete
    if (isSubmitted && !isSearchComplete && searchProgress) {
        return (
            <div className="flex flex-col items-center justify-center p-12 h-full text-center space-y-8 animate-in fade-in duration-500">
                <div className="space-y-4 max-w-md w-full">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Searching Models...</h2>
                    <p className="text-gray-500 dark:text-gray-400">
                        We are retrieving PRS models from the Catalog and PennPRS based on your disease selection.
                        Narrowing results to: <span className="font-semibold text-blue-600">{selected.length > 0 ? selected.join(", ") : "All Ancestries"}</span>
                    </p>

                    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm">
                        <ProgressBar
                            status={searchProgress.status}
                            total={searchProgress.total}
                            fetched={searchProgress.fetched}
                            currentAction={searchProgress.current_action}
                        />
                    </div>
                </div>
            </div>
        );
    }

    // View State: Selection Screen
    return (
        <div className="p-8 max-w-4xl mx-auto h-full flex flex-col">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">Refine by Ancestry</h2>
                <p className="text-gray-500 dark:text-gray-400 text-lg">
                    {searchProgress && !isSearchComplete
                        ? "While we fetch the models, you can select specific ancestries to prioritize."
                        : "Select one or more ancestry groups to filter models relevant to your cohort."}
                </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                {ancestries.map((anc) => {
                    const isSelected = selected.includes(anc.id);
                    return (
                        <button
                            key={anc.id}
                            onClick={() => toggleSelection(anc.id)}
                            className={cn(
                                "relative p-6 rounded-xl border-2 transition-all duration-200 text-left flex items-start gap-3 group hover:shadow-md",
                                isSelected
                                    ? `border-blue-500 bg-blue-50/50 dark:bg-blue-900/10`
                                    : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-blue-300"
                            )}
                        >
                            <div className={cn(
                                "w-5 h-5 rounded border flex items-center justify-center shrink-0 mt-0.5 transition-colors",
                                isSelected ? "bg-blue-500 border-blue-500 text-white" : "border-gray-300 dark:border-gray-600"
                            )}>
                                {isSelected && <Check size={12} strokeWidth={3} />}
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors">{anc.label}</h3>
                                <div className={cn("text-[10px] font-mono mt-1 w-fit px-1.5 rounded", anc.color)}>
                                    {anc.id}
                                </div>
                            </div>
                        </button>
                    )
                })}
            </div>

            <div className="mt-auto flex justify-between items-center pt-8 border-t border-gray-100 dark:border-gray-800">
                <div className="text-sm text-gray-500">
                    <span className="font-medium text-gray-900 dark:text-white">{selected.length}</span> selected
                    {selected.length === 0 && " (Showing all)"}
                </div>

                <button
                    onClick={handleConfirm}
                    disabled={isSubmitted}
                    className={cn(
                        "flex items-center gap-2 px-8 py-3 rounded-lg font-semibold transition-all shadow-lg transform active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed",
                        selected.length > 0
                            ? "bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-blue-500/25 text-white"
                            : "bg-gray-800 hover:bg-gray-700 text-white"
                    )}
                >
                    {isSubmitted ? (
                        <>
                            <Loader2 className="animate-spin" size={20} /> Processing...
                        </>
                    ) : (
                        <>
                            {selected.length > 0 ? "Apply Ancestry Filter" : "View All Results (No Filter)"}
                            <ArrowRight size={20} />
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
