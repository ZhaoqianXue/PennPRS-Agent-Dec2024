import React, { useState } from 'react';
import { Search, Activity } from 'lucide-react';
import OpenTargetsSearchModal from './OpenTargetsSearchModal';

// Quick access diseases
const quickAccessDiseases = [
    { id: "Alzheimer's disease", name: "Alzheimer's Disease", description: "MONDO_0004975" },
    { id: "Type 2 diabetes", name: "Type 2 Diabetes", description: "MONDO_0005148" },
    { id: "Coronary artery disease", name: "Coronary Artery Disease", description: "MONDO_0004994" },
    { id: "Breast cancer", name: "Breast Cancer", description: "MONDO_0007254" },
    { id: "Prostate cancer", name: "Prostate Cancer", description: "MONDO_0008315" },
    { id: "Atrial fibrillation", name: "Atrial Fibrillation", description: "MONDO_0004981" },
    { id: "Asthma", name: "Asthma", description: "MONDO_0004979" },
    { id: "Rheumatoid arthritis", name: "Rheumatoid Arthritis", description: "MONDO_0008383" },
];

interface DiseaseGridProps {
    onSelect: (trait: string) => void;
}

export default function DiseaseGrid({ onSelect }: DiseaseGridProps) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <div className="w-full max-w-6xl mx-auto space-y-8">
            {/* Search Bar - Click to open modal */}
            <div className="w-full max-w-2xl mx-auto">
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="w-full px-4 py-4 text-left flex items-center gap-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-lg transition-all cursor-text"
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

            {/* Quick Access Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {quickAccessDiseases.map((disease) => (
                    <button
                        key={disease.id}
                        onClick={() => onSelect(disease.id)}
                        className="group flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all duration-200 text-center min-h-[140px]"
                    >
                        <div className="font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 mb-1 text-base">
                            {disease.name}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-500 font-mono">
                            {disease.description}
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
