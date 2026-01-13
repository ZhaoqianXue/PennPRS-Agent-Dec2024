import React from 'react';
import { Download, Activity, Dna, Info, ExternalLink } from 'lucide-react';

export interface ModelData {
    id: string;
    name: string;
    trait: string;
    ancestry: string;
    method: string;
    metrics?: { R2?: number; AUC?: number; HR?: number; OR?: number; Beta?: number; H2?: number; Rho?: number; };
    source: "PennPRS" | "PGS Catalog" | "User Trained" | "PennPRS (Custom)" | "User Upload" | "OmicsPred";
    download_url?: string;
    num_variants?: number;
    sample_size?: number;
    publication?: {
        date: string;
        citation: string;
        id: string;
        doi: string;
    };
    // New Fields
    trait_detailed?: string;
    trait_efo?: string[];
    license?: string;
    genome_build?: string[];
    covariates?: string;
    performance_comments?: string;
    study_id?: string;
    trait_type?: string;
    submission_date?: string;
    ancestry_distribution?: {
        dist?: Array<{ ancestry: string; percent: number; number?: number }>;
    };
    performance_detailed?: {
        ppm_id: string;
        ancestry?: string;
        cohorts?: string;
        sample_size?: number;
        auc?: number;
        auc_ci_lower?: number;
        auc_ci_upper?: number;
        r2?: number;
        covariates?: string;
        comments?: string;
    }[];
    // New Technical Fields
    pgs_name?: string;
    weight_type?: string;
    params?: string;
    variants_genomebuild?: string;
    // Trait Fields
    trait_reported?: string;
    mapped_traits?: {
        id: string;
        label: string;
        url?: string;
    }[];
    // Development/Training Cohorts
    dev_cohorts?: string;
    // UI States
    isLoading?: boolean; // For optimistic loading state
    status?: "pending" | "running" | "completed" | "failed";
}

interface ModelCardProps {
    model: ModelData;
    onSelect: (modelId: string) => void;
    onViewDetails: (model: ModelData) => void;
    onSaveModel?: (model: ModelData) => void;
    activeAncestry?: string[];
}

export const getDisplayMetrics = (model: ModelData, forcedAncestry?: string[]) => {
    // Ancestry Mapping (Code -> Full Name prefix)
    const ancestryMap: Record<string, string> = {
        'EUR': 'European',
        'AFR': 'African',
        'EAS': 'East Asian',
        'SAS': 'South Asian',
        'AMR': 'Hispanic', // or 'Ad Mixed American'
        'MIX': 'Multi-ancestry'
    };

    let displayAUC = model.metrics?.AUC;
    let displayR2 = model.metrics?.R2;
    let isMatched = false;
    let isDerived = false;
    let matchedAncestry = ""; // For tooltip

    // Helper to get matching status
    const checkAncestryMatch = (ancestryString: string | undefined, targets: string[]) => {
        if (!ancestryString) return false;
        const normalized = ancestryString.toLowerCase();
        return targets.some(t => normalized.includes(t.toLowerCase()) || (ancestryMap[t] && normalized.includes(ancestryMap[t].toLowerCase())));
    };

    // 1. Check Root Ancestry Match (for Filtering)
    if (forcedAncestry && forcedAncestry.length > 0) {
        isMatched = checkAncestryMatch(model.ancestry, forcedAncestry);
    }

    // 2. Performance Metric Logic
    // If we have detailed performance records, find the best match to Display
    if (model.performance_detailed && model.performance_detailed.length > 0) {
        // Priority: forcedAncestry (User Select) > model.ancestry (System Default)
        const targetRaw = forcedAncestry && forcedAncestry.length > 0
            ? forcedAncestry
            : (model.ancestry || "").split(",").map(s => s.trim());

        const targetAncestryNames = targetRaw.map(code => ancestryMap[code] || code);

        const matchedRecords = model.performance_detailed.filter(p => {
            const pAnc = (p.ancestry || "").toLowerCase();
            return targetAncestryNames.some(target => pAnc.includes(target.toLowerCase()));
        });

        // Pick Best Match
        const matchedRecord = matchedRecords.length > 0
            ? matchedRecords.reduce((prev, current) => (prev.auc || 0) > (current.auc || 0) ? prev : current, matchedRecords[0])
            : null;

        if (matchedRecord && matchedRecord.auc) {
            displayAUC = matchedRecord.auc;
            displayR2 = matchedRecord.r2;
            // If we found a specific performance match, that's even better validation
            isMatched = true;
            isDerived = true;
            matchedAncestry = matchedRecord.ancestry || "";
        } else {
            // Fallback to Max
            const maxRecord = model.performance_detailed.reduce((prev, current) => {
                return (prev.auc || 0) > (current.auc || 0) ? prev : current;
            }, model.performance_detailed[0]);

            if (maxRecord && maxRecord.auc) {
                displayAUC = maxRecord.auc;
                displayR2 = maxRecord.r2 || model.metrics?.R2;
                isDerived = true;
                matchedAncestry = maxRecord.ancestry || "";
            }
        }
    }

    return { displayAUC, displayR2, isMatched, isDerived, matchedAncestry };
};

export default function ModelCard({ model, onSelect, onViewDetails, onSaveModel, activeAncestry }: ModelCardProps) {
    // Loading State
    if (model.isLoading) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-blue-200 dark:border-blue-900 shadow-md p-5 flex flex-col h-full relative overflow-hidden animate-pulse">
                <div className="absolute inset-0 bg-blue-50/50 dark:bg-blue-900/10 z-10 flex flex-col items-center justify-center">
                    <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3"></div>
                    <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">Training Model...</span>
                </div>
                {/* Placeholder layout to maintain size */}
                <div className="flex justify-between items-start mb-3 opacity-50">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                </div>
                <div className="space-y-4 mb-4 flex-1 opacity-50">
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                    <div className="flex gap-2">
                        <div className="h-6 bg-gray-100 dark:bg-gray-800 rounded w-1/4"></div>
                        <div className="h-6 bg-gray-100 dark:bg-gray-800 rounded w-1/4"></div>
                    </div>
                </div>
            </div>
        );
    }

    const { displayAUC, displayR2, isMatched } = getDisplayMetrics(model, activeAncestry);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow p-3 flex flex-col h-[280px] w-full">
            <div className="flex justify-between items-start mb-1">
                <div>
                    {/* Header: ID, Source, External Link */}
                    <div className="flex justify-between items-start mb-1">
                        <div className="flex flex-col">
                            <div className="flex items-center gap-2">
                                <span className="font-mono text-sm font-bold text-blue-600 dark:text-blue-400">
                                    {model.id}
                                </span>
                                {/* Source Badge */}
                                <span className={`text-[10px] px-1.5 py-0.5 rounded border ${model.id.startsWith("PGS")
                                    ? "bg-indigo-50 text-indigo-600 border-indigo-100 dark:bg-indigo-900/20 dark:text-indigo-300 dark:border-indigo-800"
                                    : "bg-emerald-50 text-emerald-600 border-emerald-100"
                                    }`}>
                                    {model.id.startsWith("PGS") ? "PGS Catalog" : "PennPRS"}
                                </span>
                            </div>
                        </div>
                        {model.id.startsWith("PGS") && (
                            <a
                                href={`https://www.pgscatalog.org/score/${model.id}/`}
                                target="_blank"
                                rel="noreferrer"
                                className="text-gray-400 hover:text-blue-600 transition-colors"
                                title="View on PGS Catalog"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <ExternalLink size={14} />
                            </a>
                        )}
                    </div>
                    <h3 className="font-semibold text-gray-900 dark:text-white line-clamp-1 cursor-pointer hover:text-blue-600 transition-colors" title={model.name} onClick={() => onViewDetails(model)}>
                        {model.name}
                    </h3>
                </div>
            </div>

            <div className="space-y-1 flex-1 cursor-pointer overflow-hidden" onClick={() => onViewDetails(model)}>
                <div className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                    <Activity className="w-4 h-4 text-gray-400" />
                    <div className="truncate font-medium">{model.trait}</div>
                </div>
                {/* Tags Row: Method | Ancestry | Samples | Cohort (Explicit Labels) */}
                <div className="flex flex-col gap-0.5">
                    {/* Method */}
                    <div className="flex items-center gap-1.5 text-[11px]">
                        <span className="text-gray-500 font-medium min-w-[55px]">Method:</span>
                        <span className="px-1.5 py-0.5 rounded font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 truncate max-w-[150px]">
                            {model.method || "N/A"}
                        </span>
                    </div>

                    {/* Training Ancestry */}
                    <div className="flex items-center gap-1.5 text-[11px]">
                        <span className="text-gray-500 font-medium min-w-[55px]">Ancestry:</span>
                        <span className="px-1.5 py-0.5 rounded font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-800 truncate max-w-[150px]">
                            {model.ancestry || "N/A"}
                        </span>
                    </div>

                    {/* Training Samples */}
                    <div className="flex items-center gap-1.5 text-[11px]">
                        <span className="text-gray-500 font-medium min-w-[55px]">Samples:</span>
                        <span className="px-1.5 py-0.5 rounded font-medium bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-100 dark:border-green-800 truncate max-w-[150px]">
                            {model.sample_size ? (model.sample_size >= 1000 ? `${(model.sample_size / 1000).toFixed(1)}k` : model.sample_size) : "N/A"}
                        </span>
                    </div>

                    {/* Score Development/Training Cohort(s) */}
                    <div className="flex items-center gap-1.5 text-[11px]">
                        <span className="text-gray-500 font-medium min-w-[55px]">Cohort:</span>
                        <span className="px-1.5 py-0.5 rounded font-medium bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border border-amber-100 dark:border-amber-800 truncate max-w-[150px]" title={model.dev_cohorts || "N/A"}>
                            {model.dev_cohorts ? (model.dev_cohorts.split(", ").length > 2 ? `${model.dev_cohorts.split(", ").slice(0, 2).join(", ")}...` : model.dev_cohorts) : "N/A"}
                        </span>
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-1 py-1 border-t border-gray-100 dark:border-gray-800">
                    {/* AUC */}
                    <div className="text-center border-r border-gray-100 dark:border-gray-800 last:border-0">
                        <div className="text-[8px] text-gray-400 font-medium uppercase tracking-wider">
                            AUC
                        </div>
                        <div className={`font-mono font-bold text-xs ${isMatched ? 'text-blue-600 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'}`}>
                            {displayAUC ? displayAUC.toFixed(3) : "N/A"}
                        </div>
                    </div>

                    {/* R2 */}
                    <div className="text-center border-r border-gray-100 dark:border-gray-800 last:border-0">
                        <div className="text-[8px] text-gray-400 font-medium uppercase tracking-wider">
                            R²
                        </div>
                        <div className="font-mono font-bold text-xs text-purple-600 dark:text-purple-400">
                            {displayR2 ? displayR2.toFixed(4) : "N/A"}
                        </div>
                    </div>

                    {/* Variants */}
                    <div className="text-center border-r border-gray-100 dark:border-gray-800 last:border-0">
                        <div className="text-[8px] text-gray-400 font-medium uppercase tracking-wider">
                            Variants
                        </div>
                        <div className="font-mono font-bold text-xs text-gray-700 dark:text-gray-300">
                            {model.num_variants ? (
                                model.num_variants > 1000
                                    ? `${(model.num_variants / 1000).toFixed(1)}k`
                                    : model.num_variants
                            ) : "N/A"}
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex gap-2 mt-auto">
                <button
                    onClick={() => onViewDetails(model)}
                    className="flex-1 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg py-1 text-xs font-medium transition-colors"
                >
                    Details
                </button>
                <button
                    onClick={() => onSaveModel?.(model)}
                    className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg py-1 text-xs font-medium transition-all shadow-sm hover:shadow-md"
                >
                    Save Model
                </button>
            </div>
        </div>
    );
}
