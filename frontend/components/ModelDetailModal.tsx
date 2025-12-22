import React from 'react';
import { X, Download, Activity, Dna, Info, BarChart3, FileText, CheckCircle2 } from 'lucide-react';
import { ModelData, getDisplayMetrics } from './ModelCard';
import { motion, AnimatePresence } from 'framer-motion';

interface ModelDetailModalProps {
    model: ModelData | null;
    isOpen: boolean;
    onClose: () => void;
    onSelect?: (modelId: string) => void;
    onDeepScan?: (modelId: string) => void;
    onTrainNew?: () => void;
    onDownstreamAction?: (action: string) => void;
}

export default function ModelDetailModal({ model, isOpen, onClose, onSelect, onDeepScan, onTrainNew, onDownstreamAction }: ModelDetailModalProps) {
    if (!model) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/40 backdrop-blur-[2px]"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 10 }}
                        className="relative w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden max-h-[90vh] flex flex-col"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-800 shrink-0">
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <div className={`text-xs px-2 py-0.5 rounded-full font-medium ${model.source === 'PennPRS' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' :
                                        model.source === 'PGS Catalog' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' :
                                            'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                                        }`}>
                                        {model.source}
                                    </div>
                                    <span className="text-sm font-mono text-gray-400">{model.id}</span>
                                </div>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{model.name}</h2>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Content (Scrollable) */}
                        <div className="p-6 overflow-y-auto space-y-8">
                            {/* Key Metrics - Standardized Order: AUC -> R2 -> Sample Size */}
                            <div className="grid grid-cols-3 gap-4">
                                {/* Logic: Calculate Display Metrics (Same as ModelCard) */}
                                {(() => {
                                    const { displayAUC, displayR2, isMatched, isDerived, matchedAncestry } = getDisplayMetrics(model);

                                    return (
                                        <>
                                            {/* 1. AUC */}
                                            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800 relative overflow-hidden">
                                                <div className="flex justify-between items-start mb-1">
                                                    <div className="text-xs uppercase tracking-wider text-blue-600 dark:text-blue-400 font-semibold">AUC</div>
                                                    {isMatched && <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 rounded-full font-medium" title={`Matched to Training Ancestry`}>Matched</span>}
                                                    {!isMatched && isDerived && <span className="text-[10px] bg-gray-100 text-gray-600 px-1.5 rounded-full font-medium" title={`Best Available (from ${matchedAncestry})`}>Best ({matchedAncestry})</span>}
                                                </div>
                                                <div className="text-2xl font-bold font-mono text-blue-700 dark:text-blue-300">
                                                    {displayAUC ? displayAUC.toFixed(3) : "N/A"}
                                                </div>
                                                <div className="text-[10px] text-blue-500 mt-1">Classification Accuracy</div>
                                            </div>

                                            {/* 2. R2 */}
                                            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-100 dark:border-purple-800">
                                                <div className="text-xs uppercase tracking-wider text-purple-600 dark:text-purple-400 font-semibold mb-1">R²</div>
                                                <div className="text-2xl font-bold font-mono text-purple-700 dark:text-purple-300">
                                                    {displayR2 ? displayR2.toFixed(4) : "N/A"}
                                                </div>
                                                <div className="text-[10px] text-purple-500 mt-1">Variance Explained</div>
                                            </div>
                                        </>
                                    );
                                })()}

                                {/* 3. Sample Size */}
                                <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-100 dark:border-gray-800">
                                    <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-1">Sample Size</div>
                                    <div className="text-2xl font-bold font-mono text-gray-900 dark:text-white truncate">
                                        {model.sample_size ? (model.sample_size / 1000).toFixed(1) + 'k' : '-'}
                                    </div>
                                    <div className="text-[10px] text-gray-500 mt-1 truncate" title={model.ancestry}>
                                        {model.ancestry || "Unknown Ancestry"}
                                    </div>
                                </div>
                            </div>

                            {/* Secondary Metrics Row (Effects, Variants, etc) - ALWAYS Visible */}
                            <div className="grid grid-cols-2 gap-4 mt-2">
                                <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-100 dark:border-green-800 flex items-center justify-between">
                                    <span className="text-xs font-semibold text-green-700 dark:text-green-400">
                                        {model.metrics?.HR ? 'Hazard Ratio' : model.metrics?.OR ? 'Odds Ratio' : model.metrics?.Beta ? 'Beta' : 'Effect Size'}
                                    </span>
                                    <span className="text-lg font-mono font-bold text-green-700 dark:text-green-300">
                                        {model.metrics?.HR ? model.metrics.HR.toFixed(2) :
                                            model.metrics?.OR ? model.metrics.OR.toFixed(2) :
                                                model.metrics?.Beta ? model.metrics.Beta.toFixed(2) : "N/A"}
                                    </span>
                                </div>

                                <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-800 flex items-center justify-between">
                                    <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">Variants</span>
                                    <span className="text-lg font-mono font-bold text-gray-800 dark:text-gray-200">
                                        {model.num_variants ? model.num_variants.toLocaleString() : "N/A"}
                                    </span>
                                </div>
                            </div>

                            {/* Introduction Description */}
                            <div className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed border-b border-gray-100 dark:border-gray-800 pb-4 mb-4">
                                This Polygenic Risk Score model targets <strong>{model.trait}</strong> and was developed using the <strong>{model.method}</strong> method.
                                {model.source === 'PGS Catalog'
                                    ? " It is curated from the PGS Catalog."
                                    : " It was trained via PennPRS."}
                                <div className="flex items-center gap-2 mt-2 text-xs text-green-600 dark:text-green-400">
                                    <CheckCircle2 className="w-3 h-3" />
                                    <span>Ready for Scoring</span>
                                </div>
                            </div>
                            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-800 text-sm space-y-2 font-mono text-xs">

                                {/* Section A: Predicted Trait */}
                                <div className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-blue-500 pl-2">Predicted Trait</h5>
                                    <div className="grid grid-cols-3 gap-2 mb-2">
                                        <span className="text-gray-500">Reported Trait:</span>
                                        <span className="col-span-2 text-gray-900 dark:text-gray-100 font-medium">{model.trait_reported || model.trait || "N/A"}</span>
                                    </div>
                                    <div className="grid grid-cols-3 gap-2">
                                        <span className="text-gray-500">Mapped Trait(s):</span>
                                        <div className="col-span-2 flex flex-col gap-1">
                                            {model.mapped_traits && model.mapped_traits.length > 0 ? (
                                                model.mapped_traits.map(trait => (
                                                    <div key={trait.id} className="flex items-center gap-2">
                                                        <span className="text-gray-900 dark:text-gray-100">{trait.label}</span>
                                                        <a href={trait.url || '#'} target="_blank" rel="noreferrer" className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 px-1.5 py-0.5 rounded hover:underline font-mono">{trait.id}</a>
                                                    </div>
                                                ))
                                            ) : <span className="text-gray-400">N/A</span>}
                                        </div>
                                    </div>
                                </div>

                                {/* Section B: Score Construction */}
                                <div className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-purple-500 pl-2">Score Construction</h5>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">PGS Name:</span><span className="col-span-2 font-medium text-gray-900 dark:text-gray-100">{model.pgs_name || model.id || "N/A"}</span></div>
                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Genome Build:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.variants_genomebuild || "N/A"}</span></div>
                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Variants:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.num_variants ? model.num_variants.toLocaleString() : "N/A"}</span></div>
                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Method:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.method || "N/A"}</span></div>
                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Parameters:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.params || "N/A"}</span></div>
                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Weight Type:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.weight_type || "N/A"}</span></div>
                                    </div>
                                </div>

                                {/* Section C: Performance Metrics (Table) */}
                                <div className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-green-500 pl-2">Performance Metrics</h5>

                                    <div className="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                                        <table className="w-full text-sm text-left">
                                            <thead className="bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                                                <tr>
                                                    <th className="px-3 py-2 font-medium">Ancestry</th>
                                                    <th className="px-3 py-2 font-medium">Cohorts</th>
                                                    <th className="px-3 py-2 font-medium text-right">Sample Size</th>
                                                    <th className="px-3 py-2 font-medium text-right">AUC [95% CI]</th>
                                                    <th className="px-3 py-2 font-medium text-right">R²</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                                {model.performance_detailed && model.performance_detailed.length > 0 ? (
                                                    model.performance_detailed.map((perf, idx) => (
                                                        <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                                            <td className="px-3 py-2 text-gray-800 dark:text-gray-200">{perf.ancestry || "N/A"}</td>
                                                            <td className="px-3 py-2 text-gray-600 dark:text-gray-400">{perf.cohorts || "N/A"}</td>
                                                            <td className="px-3 py-2 text-right font-mono text-gray-600 dark:text-gray-400">
                                                                {perf.sample_size ? perf.sample_size.toLocaleString() : "N/A"}
                                                            </td>
                                                            <td className="px-3 py-2 text-right">
                                                                <div className="flex flex-col items-end">
                                                                    <span className="font-mono text-blue-600 dark:text-blue-400 font-bold">
                                                                        {perf.auc ? perf.auc.toFixed(3) : "N/A"}
                                                                    </span>
                                                                    {perf.auc_ci_lower && perf.auc_ci_upper && (
                                                                        <span className="text-[10px] text-gray-400 font-mono">
                                                                            [{perf.auc_ci_lower.toFixed(3)} - {perf.auc_ci_upper.toFixed(3)}]
                                                                        </span>
                                                                    )}
                                                                </div>
                                                            </td>
                                                            <td className="px-3 py-2 text-right font-mono text-purple-600 dark:text-purple-400 font-bold">
                                                                {perf.r2 ? perf.r2.toFixed(4) : "N/A"}
                                                            </td>
                                                        </tr>
                                                    ))
                                                ) : (
                                                    <tr>
                                                        <td colSpan={5} className="px-3 py-4 text-center text-gray-500">No detailed performance records available (N/A)</td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                {/* Section D: Source & Metadata */}
                                <div>
                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-yellow-500 pl-2">Source & Metadata</h5>

                                    <div className="grid grid-cols-1 gap-y-2">
                                        {/* Citation */}
                                        <div className="grid grid-cols-3 gap-2">
                                            <span className="text-gray-500">Citation:</span>
                                            <span className="col-span-2">
                                                {model.publication ? (
                                                    <a href={`https://doi.org/${model.publication.doi}`} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                                                        {model.publication.citation}
                                                    </a>
                                                ) : "N/A"}
                                            </span>
                                        </div>

                                        {/* License */}
                                        <div className="grid grid-cols-3 gap-2">
                                            <span className="text-gray-500">License:</span>
                                            <span className="col-span-2 text-gray-900 dark:text-gray-100">{model.license || "N/A"}</span>
                                        </div>

                                        {/* Ancestry Distribution */}
                                        <div className="grid grid-cols-3 gap-2">
                                            <span className="text-gray-500">Ancestry Dist:</span>
                                            <div className="col-span-2">
                                                {model.ancestry_distribution && model.ancestry_distribution.dist && model.ancestry_distribution.dist.length > 0 ? (
                                                    <>
                                                        <div className="flex w-full h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 mb-1">
                                                            {model.ancestry_distribution.dist.map((item, idx) => (
                                                                <div key={idx} className={`${['bg-blue-500', 'bg-purple-500', 'bg-green-500', 'bg-yellow-500', 'bg-pink-500'][idx % 5]}`} style={{ width: `${item.percent}%` }} />
                                                            ))}
                                                        </div>
                                                        <div className="flex flex-wrap gap-x-2 text-[10px] text-gray-600 dark:text-gray-400">
                                                            {model.ancestry_distribution.dist.map((item, idx) => (
                                                                <span key={idx}>{item.ancestry}: {item.percent}%</span>
                                                            ))}
                                                        </div>
                                                    </>
                                                ) : "N/A"}
                                            </div>
                                        </div>

                                        {/* Link */}
                                        <div className="grid grid-cols-3 gap-2">
                                            <span className="text-gray-500">PGS Catalog:</span>
                                            <a href={`https://www.pgscatalog.org/score/${model.id}/`} target="_blank" rel="noreferrer" className="col-span-2 text-blue-600 hover:underline font-mono text-xs break-all">
                                                https://www.pgscatalog.org/score/{model.id}/
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Section C: Performance Metrics (Table) - Moved outside the grey box for width */}


                            {/* Visualization Placeholder */}
                        </div>

                        {/* Footer */}
                        <div className="p-6 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 flex flex-col gap-4 shrink-0">
                            {/* Deep Scan (Contextual) */}
                            {onDeepScan && model.source === 'PennPRS' && !model.metrics?.H2 && (
                                <button
                                    onClick={() => onDeepScan(model.id)}
                                    className="w-full px-4 py-2 text-sm font-medium text-purple-600 bg-purple-50 hover:bg-purple-100 dark:bg-purple-900/20 dark:text-purple-300 dark:hover:bg-purple-900/30 rounded-lg transition-colors flex items-center justify-center gap-2"
                                >
                                    <Dna className="w-4 h-4" />
                                    Deep Scan (Get H2 & Variants)
                                </button>
                            )}

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {/* 1. Evaluate */}
                                <button onClick={() => onDownstreamAction?.("Evaluate on Cohort")} className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:border-blue-500 hover:text-blue-600 transition-colors flex items-center gap-2 justify-center sm:justify-start">
                                    <Activity className="w-4 h-4 text-gray-400 group-hover:text-blue-500" /> Evaluate on Cohort
                                </button>
                                {/* 2. Ensemble */}
                                <button onClick={() => onDownstreamAction?.("Build Ensemble Model")} className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:border-blue-500 hover:text-blue-600 transition-colors flex items-center gap-2 justify-center sm:justify-start">
                                    <BarChart3 className="w-4 h-4 text-gray-400 group-hover:text-blue-500" /> Build Ensemble Model
                                </button>
                                {/* 3. Proteomics */}

                                {/* 4. Train Custom */}
                                <button onClick={() => onTrainNew?.()} className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:border-blue-500 hover:text-blue-600 transition-colors flex items-center gap-2 justify-center sm:justify-start">
                                    <FileText className="w-4 h-4 text-gray-400 group-hover:text-blue-500" /> Train Custom Model
                                </button>
                                {/* 5. Download (Full Width) */}
                                <button
                                    onClick={() => model.download_url && window.open(model.download_url, '_blank')}
                                    disabled={!model.download_url}
                                    className="col-span-1 sm:col-span-2 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg text-sm font-medium text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors flex items-center justify-center gap-2"
                                >
                                    <Download className="w-4 h-4" /> Download Model Files
                                </button>
                            </div>

                            <div className="flex justify-center mt-2">
                                <button onClick={onClose} className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-300 underline underline-offset-4">
                                    Close Details
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
