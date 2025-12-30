"use client";

import React from 'react';
import { X, ExternalLink, Dna, FlaskConical, BarChart3, Info, Network } from 'lucide-react';
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
    tissue_id?: string;
    dataset_name?: string;
    dataset_id?: string;
    tissue?: string;
    genome_build?: string;
    license?: string;

    dev_sample_size?: number;
    eval_sample_size?: number;

    // Raw evaluations list from API
    evaluations?: Array<{
        cohort_label?: string;
        evaluation_type?: string; // e.g. "Training", "External Validation"
        sample?: {
            sample_number?: number;
            ancestry_broad?: string;
            cohorts?: Array<{
                name_short: string;
            }>;
        };
        performance_metrics?: Array<{
            name_short?: string;
            estimate?: number;
        }>;
        match_rate?: number; // Hypothetical, usually not in standard performance list
        missing_rate?: number;
    }>;

    performance_data?: Record<string, { estimate: number }>; // Legacy dict
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

    // Helper to extract a metric from an evaluation item
    const getMetric = (evalItem: any, name: string) => {
        const m = evalItem.performance_metrics?.find((x: any) => x.name_short === name);
        return m ? m.estimate : null;
    };

    // Helper to clean platform name for URL
    // e.g. "Somalogic(3.0)-Proteomics" -> "Somalogic"
    const getPlatformUrl = (platformRaw: string) => {
        if (!platformRaw) return "#";
        // Extract word before ( or -
        const clean = platformRaw.split(/[\(-]/)[0].trim();
        return `https://www.omicspred.org/platform/${clean}`;
    };

    // Helper for Publication URL
    const getPubUrl = () => {
        if (!model.publication) return null;
        if (model.publication.doi && (model.publication.doi.startsWith('http') || model.publication.doi.startsWith('doi.org'))) return model.publication.doi;
        if (model.publication.doi) return `https://doi.org/${model.publication.doi}`;
        if (model.publication.id) return `https://www.omicspred.org/publication/${model.publication.id}`;
        return null;
    };

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
                        className="relative w-full max-w-5xl bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden max-h-[90vh] flex flex-col"
                    >
                        {/* Header path style */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 shrink-0">
                            <div className="flex items-center gap-2 text-lg">
                                <span className="text-blue-600 dark:text-blue-400 font-semibold flex items-center gap-1">
                                    <BarChart3 className="w-5 h-5" />
                                    Genetic Score
                                </span>
                                <span className="text-gray-400">/</span>
                                <h2 className="font-bold text-gray-900 dark:text-white">
                                    {model.id}
                                </h2>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Content Scrollable */}
                        <div className="p-6 overflow-y-auto bg-gray-50/50 dark:bg-gray-950/50 space-y-6">

                            {/* Top Section: Score Info + Linked Annotations */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                                {/* Left: Score Information (2 cols wide) */}
                                <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800">
                                    <div className="bg-blue-600 text-white px-4 py-2 rounded-t-lg font-semibold text-sm">
                                        Score Information
                                    </div>
                                    <div className="p-4 grid grid-cols-[140px_1fr] gap-y-2 gap-x-4 text-sm">
                                        <div className="font-bold text-gray-700 dark:text-gray-300">Score Name:</div>
                                        <div className="text-gray-900 dark:text-gray-100">{model.name}</div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Publication:</div>
                                        <div>
                                            {model.publication ? (
                                                <>
                                                    <a href={getPubUrl() || '#'} target="_blank" rel="noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1">
                                                        {model.publication?.firstauthor ? `${model.publication.firstauthor} et al. ` : ''}
                                                        {model.publication?.journal && <i>{model.publication.journal} </i>}
                                                        ({model.publication?.date?.split('-')[0] || 'Unknown Year'})
                                                        <ExternalLink className="w-3 h-3" />
                                                    </a>
                                                    {model.publication?.id && <span className="text-gray-500 ml-2">({model.publication.id})</span>}
                                                </>
                                            ) : (
                                                <span className="text-gray-500">N/A</span>
                                            )}
                                        </div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Platform:</div>
                                        <div className="text-gray-900 dark:text-gray-100 flex items-center gap-2">
                                            <a href={getPlatformUrl(model.platform || '')} target="_blank" rel="noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                                                {model.platform}
                                            </a>
                                            {/* (3.0) - Proteomics icon mimic */}
                                            <span className="text-red-500 text-xs flex items-center gap-1 font-semibold">
                                                <div className="w-2 h-2 bg-red-500 rounded-sm"></div> Proteomics
                                            </span>
                                        </div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Tissue:</div>
                                        <div>
                                            <a href={`https://www.omicspred.org/tissue/${model.tissue_id || 'UBERON_0001969'}`} target="_blank" rel="noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                                                {model.tissue || "blood plasma (UBERON_0001969)"}
                                            </a>
                                        </div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Dataset:</div>
                                        <div className="text-gray-900 dark:text-gray-100">{model.dataset_id || "Unknown"}</div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Method Name:</div>
                                        <div className="text-gray-900 dark:text-gray-100">{model.method}</div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Reported Trait:</div>
                                        <div className="text-gray-900 dark:text-gray-100">{model.trait}</div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Number of Variants:</div>
                                        <div className="text-white">
                                            <span className="bg-blue-600 px-2 py-0.5 rounded-full text-xs font-bold">{model.num_variants}</span>
                                        </div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Genome Build:</div>
                                        <div className="text-gray-900 dark:text-gray-100">{model.genome_build || "GRCh37"}</div>

                                        <div className="font-bold text-gray-700 dark:text-gray-300">Terms & Licenses:</div>
                                        <div className="text-gray-900 dark:text-gray-100 text-xs">{model.license || "Creative Commons Attribution 4.0 International (CC BY 4.0)"}</div>
                                    </div>
                                </div>

                                {/* Right: Linked Annotations (1 col) */}
                                <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800 h-fit">
                                    <div className="bg-blue-600 text-white px-4 py-2 rounded-t-lg font-semibold text-sm">
                                        Linked Annotations
                                    </div>
                                    <div className="p-4 space-y-4 text-sm">
                                        <div className="flex gap-3">
                                            <div className="mt-0.5"><Dna className="w-4 h-4 text-green-500" /></div>
                                            <div>
                                                <span className="font-bold text-gray-700 dark:text-gray-300">Gene: </span>
                                                <span className="text-gray-900 dark:text-gray-100 ml-2">
                                                    {model.genes?.[0]?.name}
                                                    {model.genes?.[0]?.external_id && (
                                                        <a href={`https://www.omicspred.org/gene/${model.genes[0].external_id}`}
                                                            target="_blank" rel="noreferrer"
                                                            className="text-blue-600 hover:underline ml-1">
                                                            ({model.genes[0].external_id})
                                                        </a>
                                                    )}
                                                </span>
                                            </div>
                                        </div>

                                        {model.proteins && model.proteins.length > 0 && (
                                            <div className="flex gap-3">
                                                <div className="mt-0.5"><FlaskConical className="w-4 h-4 text-red-500" /></div>
                                                <div>
                                                    <span className="font-bold text-gray-700 dark:text-gray-300">Protein: </span>
                                                    <span className="text-gray-900 dark:text-gray-100 ml-2">
                                                        {model.proteins[0].name}
                                                        {model.uniprot_id && (
                                                            <a href={`https://www.omicspred.org/protein/${model.uniprot_id}`}
                                                                target="_blank" rel="noreferrer"
                                                                className="text-blue-600 hover:underline ml-1">
                                                                ({model.uniprot_id})
                                                            </a>
                                                        )}
                                                    </span>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Bottom: Evaluations */}
                            <div>
                                <h3 className="text-lg font-normal text-gray-800 dark:text-gray-200 mb-2">
                                    Evaluations <span className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded text-xs font-bold border border-gray-300 dark:border-gray-700">
                                        {model.evaluations?.length || 0}
                                    </span>
                                </h3>

                                {/* Table */}
                                <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800 overflow-hidden">
                                    <div className="bg-blue-500 h-1 w-full"></div> {/* Blue top bar */}
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm text-left">
                                            <thead className="text-xs font-bold uppercase text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                                                <tr>
                                                    <th className="px-6 py-3">Cohort</th>
                                                    <th className="px-6 py-3">Ancestry</th>
                                                    <th className="px-6 py-3 text-center">Sample size</th>
                                                    <th className="px-6 py-3">Study stage</th>
                                                    <th className="px-6 py-3 text-right">R²</th>
                                                    <th className="px-6 py-3 text-right">Rho</th>
                                                    <th className="px-6 py-3 text-right">Match Rate</th>
                                                    <th className="px-6 py-3 text-right">Missing Rate</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                                {model.evaluations?.map((item, idx) => (
                                                    <tr key={idx} className="hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-colors">
                                                        <td className="px-6 py-3 font-medium text-blue-600 dark:text-blue-400 hover:underline cursor-pointer">
                                                            {(() => {
                                                                const cohortName = item.cohort_label || item.sample?.cohorts?.[0]?.name_short || 'N/A';
                                                                return (
                                                                    <a href={`https://www.omicspred.org/cohort/${cohortName}`} target="_blank" rel="noreferrer">
                                                                        {cohortName}
                                                                    </a>
                                                                );
                                                            })()}
                                                        </td>
                                                        <td className="px-6 py-3 flex items-center gap-2">
                                                            {/* Ancestry Colored Box */}
                                                            <div className={`w-3 h-3 rounded-sm ${item.sample?.ancestry_broad === 'European' ? 'bg-blue-500' :
                                                                item.sample?.ancestry_broad?.includes('Asian') ? 'bg-green-500' :
                                                                    item.sample?.ancestry_broad === 'African' ? 'bg-yellow-500' : 'bg-gray-400'
                                                                }`}></div>
                                                            <span className="text-gray-700 dark:text-gray-300">{item.sample?.ancestry_broad || 'Unknown'}</span>
                                                        </td>
                                                        <td className="px-6 py-3 text-center font-mono">
                                                            <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-bold">
                                                                {item.sample?.sample_number?.toLocaleString() || 0}
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-3 text-gray-700 dark:text-gray-300 font-medium text-xs">
                                                            {item.evaluation_type}
                                                        </td>
                                                        <td className="px-6 py-3 text-right font-mono font-medium text-gray-900 dark:text-gray-100">
                                                            {getMetric(item, 'R2')?.toFixed(3) || '-'}
                                                        </td>
                                                        <td className="px-6 py-3 text-right font-mono font-medium text-gray-900 dark:text-gray-100">
                                                            {getMetric(item, 'Rho')?.toFixed(3) || '-'}
                                                        </td>
                                                        <td className="px-6 py-3 text-right text-gray-500">-</td>
                                                        <td className="px-6 py-3 text-right text-gray-500">-</td>
                                                    </tr>
                                                ))}
                                                {(!model.evaluations || model.evaluations.length === 0) && (
                                                    <tr>
                                                        <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                                                            No evaluation data available.
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
