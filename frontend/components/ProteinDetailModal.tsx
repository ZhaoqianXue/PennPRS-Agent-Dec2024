"use client";

import React from 'react';
import { X, Download, ExternalLink, Dna, FlaskConical, Users, BarChart3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Extended interface for OmicsPred protein scores
interface ProteinScoreData {
    id: string;
    name: string;
    trait: string;
    ancestry: string;
    method: string;
    metrics?: Record<string, number>;
    num_variants?: number;
    sample_size?: number;
    source: string;
    download_url?: string;
    publication?: {
        id?: string;
        citation?: string;
        doi?: string;
        pmid?: number;
        title?: string;
        date?: string;
        journal?: string;
        firstauthor?: string;
    };
    // OmicsPred-specific fields
    protein_name?: string;
    gene_name?: string;
    gene_ensembl_id?: string;
    uniprot_id?: string;
    protein_synonyms?: string[];
    protein_description?: string;
    platform?: string;
    dataset_name?: string;
    dataset_id?: string;
    dev_sample_size?: number;
    eval_sample_size?: number;
    ancestry_dev?: {
        anc?: Record<string, { dist: number; count: number }>;
        count?: number;
    };
    ancestry_eval?: {
        anc?: Record<string, { dist: number; count: number }>;
        count?: number;
    };
    performance_data?: Record<string, { estimate: number }>;
    genes?: Array<{
        name: string;
        external_id?: string;
        descriptions?: string[];
        external_id_source?: string;
        biotype?: string;
    }>;
    proteins?: Array<{
        name: string;
        external_id?: string;
        external_id_source?: string;
        synonyms?: string[];
        descriptions?: string[];
    }>;
    trait_type?: string;
}

interface ProteinDetailModalProps {
    model: ProteinScoreData | null;
    isOpen: boolean;
    onClose: () => void;
    onDownload?: () => void;
}

export default function ProteinDetailModal({ model, isOpen, onClose, onDownload }: ProteinDetailModalProps) {
    if (!model) return null;

    // Parse performance metrics into structured format
    const parsePerformanceData = () => {
        const perf = model.performance_data || {};
        const cohorts: Record<string, { r2?: number; rho?: number; missingRate?: number; matchRate?: number }> = {};

        Object.entries(perf).forEach(([key, val]) => {
            // Extract cohort name from key (e.g., "NSPHS_R2" -> "NSPHS")
            const parts = key.split('_');
            let cohortName = parts[0];
            const metricType = parts.slice(1).join('_');

            // Handle training metrics specially
            if (key.includes('training')) {
                cohortName = model.dataset_name || 'Training';
            }

            if (!cohorts[cohortName]) cohorts[cohortName] = {};

            if (metricType.includes('R2')) {
                cohorts[cohortName].r2 = val.estimate;
            } else if (metricType.includes('Rho')) {
                cohorts[cohortName].rho = val.estimate;
            } else if (metricType.includes('Missing')) {
                cohorts[cohortName].missingRate = val.estimate;
            } else if (metricType.includes('Match')) {
                cohorts[cohortName].matchRate = val.estimate;
            }
        });

        return cohorts;
    };

    const performanceByCohort = parsePerformanceData();

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
                        className="relative w-full max-w-3xl bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden max-h-[90vh] flex flex-col"
                    >
                        {/* Header */}
                        <div className="flex items-start justify-between p-6 border-b border-gray-100 dark:border-gray-800 shrink-0 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300">
                                        OmicsPred
                                    </span>
                                    <span className="text-sm font-mono text-gray-500">{model.id}</span>
                                    <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                                        {model.platform}
                                    </span>
                                </div>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                                    {model.protein_name || model.name}
                                </h2>
                                {model.gene_name && (
                                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                        <Dna className="w-4 h-4 text-violet-500" />
                                        <span className="font-medium">{model.gene_name}</span>
                                        {model.gene_ensembl_id && (
                                            <a
                                                href={`https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=${model.gene_ensembl_id}`}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="text-xs text-violet-600 hover:underline"
                                            >
                                                {model.gene_ensembl_id}
                                            </a>
                                        )}
                                    </div>
                                )}
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Content (Scrollable) */}
                        <div className="p-6 overflow-y-auto space-y-6">
                            {/* Key Metrics Row */}
                            <div className="grid grid-cols-4 gap-3">
                                <div className="bg-violet-50 dark:bg-violet-900/20 p-4 rounded-xl border border-violet-100 dark:border-violet-800">
                                    <div className="text-xs uppercase tracking-wider text-violet-600 dark:text-violet-400 font-semibold mb-1">R²</div>
                                    <div className="text-2xl font-bold font-mono text-violet-700 dark:text-violet-300">
                                        {model.metrics?.R2 ? model.metrics.R2.toFixed(4) : "N/A"}
                                    </div>
                                    <div className="text-[10px] text-violet-500 mt-1">Training</div>
                                </div>

                                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-xl border border-purple-100 dark:border-purple-800">
                                    <div className="text-xs uppercase tracking-wider text-purple-600 dark:text-purple-400 font-semibold mb-1">ρ (Rho)</div>
                                    <div className="text-2xl font-bold font-mono text-purple-700 dark:text-purple-300">
                                        {model.metrics?.Rho ? model.metrics.Rho.toFixed(3) : "N/A"}
                                    </div>
                                    <div className="text-[10px] text-purple-500 mt-1">Correlation</div>
                                </div>

                                <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-xl border border-indigo-100 dark:border-indigo-800">
                                    <div className="text-xs uppercase tracking-wider text-indigo-600 dark:text-indigo-400 font-semibold mb-1">Variants</div>
                                    <div className="text-2xl font-bold font-mono text-indigo-700 dark:text-indigo-300">
                                        {model.num_variants?.toLocaleString() || "N/A"}
                                    </div>
                                    <div className="text-[10px] text-indigo-500 mt-1">SNPs</div>
                                </div>

                                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                                    <div className="text-xs uppercase tracking-wider text-slate-600 dark:text-slate-400 font-semibold mb-1">Samples</div>
                                    <div className="text-2xl font-bold font-mono text-slate-700 dark:text-slate-200">
                                        {model.dev_sample_size ? (model.dev_sample_size / 1000).toFixed(1) + 'k' : "N/A"}
                                    </div>
                                    <div className="text-[10px] text-slate-500 mt-1">{model.ancestry} • Dev</div>
                                </div>
                            </div>

                            {/* Protein Information */}
                            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
                                <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                                    <FlaskConical className="w-4 h-4 text-violet-500" />
                                    Protein Information
                                </h3>
                                <div className="space-y-3 text-sm">
                                    <div className="grid grid-cols-4 gap-2">
                                        <span className="text-gray-500 font-medium">Protein Name:</span>
                                        <span className="col-span-3 text-gray-900 dark:text-gray-100">{model.protein_name || "N/A"}</span>
                                    </div>
                                    {model.uniprot_id && (
                                        <div className="grid grid-cols-4 gap-2">
                                            <span className="text-gray-500 font-medium">UniProt ID:</span>
                                            <span className="col-span-3">
                                                <a
                                                    href={`https://www.uniprot.org/uniprotkb/${model.uniprot_id}`}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="text-violet-600 hover:underline flex items-center gap-1"
                                                >
                                                    {model.uniprot_id}
                                                    <ExternalLink className="w-3 h-3" />
                                                </a>
                                            </span>
                                        </div>
                                    )}
                                    {model.protein_synonyms && model.protein_synonyms.length > 0 && (
                                        <div className="grid grid-cols-4 gap-2">
                                            <span className="text-gray-500 font-medium">Synonyms:</span>
                                            <span className="col-span-3 text-gray-700 dark:text-gray-300">
                                                {model.protein_synonyms.slice(0, 3).join(', ')}
                                                {model.protein_synonyms.length > 3 && ` +${model.protein_synonyms.length - 3} more`}
                                            </span>
                                        </div>
                                    )}
                                    {model.protein_description && (
                                        <div className="grid grid-cols-4 gap-2">
                                            <span className="text-gray-500 font-medium">Function:</span>
                                            <p className="col-span-3 text-gray-700 dark:text-gray-300 text-xs leading-relaxed">
                                                {model.protein_description.slice(0, 300)}
                                                {model.protein_description.length > 300 && '...'}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Performance Metrics Table */}
                            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
                                <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                                    <BarChart3 className="w-4 h-4 text-violet-500" />
                                    Performance by Cohort
                                </h3>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead className="text-xs uppercase text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800">
                                            <tr>
                                                <th className="px-3 py-2 text-left rounded-tl-lg">Cohort</th>
                                                <th className="px-3 py-2 text-right">R²</th>
                                                <th className="px-3 py-2 text-right">ρ (Rho)</th>
                                                <th className="px-3 py-2 text-right">Match Rate</th>
                                                <th className="px-3 py-2 text-right rounded-tr-lg">Missing Rate</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                            {Object.entries(performanceByCohort).map(([cohort, metrics]) => (
                                                <tr key={cohort} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                                    <td className="px-3 py-2 font-medium text-gray-900 dark:text-gray-100">
                                                        {cohort}
                                                        {cohort === model.dataset_name && (
                                                            <span className="ml-2 text-[10px] px-1.5 py-0.5 bg-violet-100 text-violet-600 rounded-full">Train</span>
                                                        )}
                                                    </td>
                                                    <td className="px-3 py-2 text-right font-mono text-violet-600 dark:text-violet-400">
                                                        {metrics.r2 ? metrics.r2.toFixed(3) : "-"}
                                                    </td>
                                                    <td className="px-3 py-2 text-right font-mono text-purple-600 dark:text-purple-400">
                                                        {metrics.rho ? metrics.rho.toFixed(3) : "-"}
                                                    </td>
                                                    <td className="px-3 py-2 text-right font-mono text-gray-600 dark:text-gray-400">
                                                        {metrics.matchRate ? (metrics.matchRate * 100).toFixed(1) + '%' : "-"}
                                                    </td>
                                                    <td className="px-3 py-2 text-right font-mono text-gray-500 dark:text-gray-500">
                                                        {metrics.missingRate ? (metrics.missingRate * 100).toFixed(1) + '%' : "-"}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Dataset & Publication Info */}
                            <div className="grid grid-cols-2 gap-4">
                                {/* Dataset Info */}
                                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
                                    <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2 flex items-center gap-2">
                                        <Users className="w-4 h-4 text-violet-500" />
                                        Dataset
                                    </h4>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Name:</span>
                                            <span className="font-medium text-gray-900 dark:text-gray-100">{model.dataset_name || "N/A"}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">ID:</span>
                                            <span className="font-mono text-xs text-gray-600 dark:text-gray-400">{model.dataset_id || "N/A"}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Platform:</span>
                                            <span className="text-gray-900 dark:text-gray-100">{model.platform}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Ancestry:</span>
                                            <span className="text-gray-900 dark:text-gray-100">{model.ancestry}</span>
                                        </div>
                                        {model.eval_sample_size && (
                                            <div className="flex justify-between">
                                                <span className="text-gray-500">Eval Samples:</span>
                                                <span className="font-mono text-gray-900 dark:text-gray-100">{model.eval_sample_size.toLocaleString()}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Publication */}
                                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
                                    <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">Publication</h4>
                                    {model.publication ? (
                                        <div className="space-y-2 text-sm">
                                            <p className="text-gray-700 dark:text-gray-300 text-xs leading-relaxed line-clamp-3">
                                                {model.publication.title}
                                            </p>
                                            <p className="text-gray-500 text-xs">
                                                {model.publication.citation}
                                            </p>
                                            <div className="flex gap-2 mt-2">
                                                {model.publication.doi && (
                                                    <a
                                                        href={`https://doi.org/${model.publication.doi}`}
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className="text-xs px-2 py-1 bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300 rounded hover:underline"
                                                    >
                                                        DOI
                                                    </a>
                                                )}
                                                {model.publication.pmid && (
                                                    <a
                                                        href={`https://pubmed.ncbi.nlm.nih.gov/${model.publication.pmid}/`}
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className="text-xs px-2 py-1 bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 rounded hover:underline"
                                                    >
                                                        PubMed
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-gray-400 text-sm">No publication info</p>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 shrink-0">
                            <div className="flex gap-3">
                                <a
                                    href={model.download_url || `https://www.omicspred.org/score/${model.id}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="flex-1 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                    View on OmicsPred
                                </a>
                                <button
                                    onClick={onClose}
                                    className="px-6 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg text-sm font-medium transition-colors"
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
