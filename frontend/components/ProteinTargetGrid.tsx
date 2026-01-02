import React, { useState } from 'react';
import { Search, Dna } from 'lucide-react';
import OpenTargetsSearchModal from './OpenTargetsSearchModal';

// Quick access genes
const quickAccessGenes = [
    { id: "APOE", name: "APOE", description: "ENSG00000130203" },
    { id: "TP53", name: "TP53", description: "ENSG00000141510" },
    { id: "EGFR", name: "EGFR", description: "ENSG00000146648" },
    { id: "BRCA1", name: "BRCA1", description: "ENSG00000012048" },
];

// Quick access proteins
const quickAccessProteins = [
    { id: "TNF", name: "TNF (Tumor Necrosis Factor)", description: "ENSG00000232810" },
    { id: "IL6", name: "IL-6 (Interleukin 6)", description: "ENSG00000136244" },
    { id: "CRP", name: "CRP (C-Reactive Protein)", description: "ENSG00000132693" },
    { id: "INS", name: "INS (Insulin)", description: "ENSG00000254647" },
];

interface ProteinTargetGridProps {
    onSelect: (query: string) => void;
}

export default function ProteinTargetGrid({ onSelect }: ProteinTargetGridProps) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <div className="w-full max-w-5xl mx-auto space-y-8">
            {/* Search Bar - Click to open modal */}
            <div className="w-full max-w-2xl mx-auto">
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="w-full px-4 py-4 text-left flex items-center gap-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl hover:border-violet-500 dark:hover:border-violet-500 hover:shadow-lg transition-all cursor-text"
                >
                    <Search className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-500 dark:text-gray-400 text-base">
                        Search for a target, drug, disease, or phenotype...
                    </span>
                </button>
            </div>

            {/* Open Targets Search Modal */}
            <OpenTargetsSearchModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSelect={(query) => {
                    setIsModalOpen(false);
                    onSelect(query);
                }}
            />

            {/* Quick Access Section */}
            <div className="text-center">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Quick Access
                </span>
            </div>

            {/* Quick Access Gene Cards */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Dna className="w-5 h-5 text-violet-500" />
                    Reference Genes
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {quickAccessGenes.map((gene) => (
                        <button
                            key={gene.id}
                            onClick={() => onSelect(gene.id)}
                            className="group p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-violet-400 dark:hover:border-violet-500 hover:shadow-md transition-all text-left"
                        >
                            <div className="font-bold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 mb-1">
                                {gene.name}
                            </div>
                            <div className="text-xs text-gray-400 dark:text-gray-500 font-mono">
                                {gene.description}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Quick Access Protein Cards */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Dna className="w-5 h-5 text-purple-500" />
                    Featured Proteins
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {quickAccessProteins.map((prot) => (
                        <button
                            key={prot.id}
                            onClick={() => onSelect(prot.id)}
                            className="group p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 hover:shadow-md transition-all text-left"
                        >
                            <div className="font-bold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 mb-1 truncate">
                                {prot.name}
                            </div>
                            <div className="text-xs text-gray-400 dark:text-gray-500 font-mono">
                                {prot.description}
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
