import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface Disease {
    id: string;
    name: string;
    description: string;
}

const diseases: Disease[] = [
    { id: "Alzheimer's disease", name: "Alzheimer's Disease", description: "Neurodegenerative disorder prediction" },
    { id: "Type 2 diabetes", name: "Type 2 Diabetes", description: "Metabolic risk assessment" },
    { id: "Coronary artery disease", name: "Coronary Artery Disease", description: "Cardiovascular health monitoring" },
    { id: "Breast cancer", name: "Breast Cancer", description: "Oncology risk profiling" },
    { id: "Prostate cancer", name: "Prostate Cancer", description: "Male oncology screening" },
    { id: "Atrial fibrillation", name: "Atrial Fibrillation", description: "Cardiac arrhythmia risk" },
    { id: "Asthma", name: "Asthma", description: "Respiratory disease prediction" },
    { id: "Rheumatoid arthritis", name: "Rheumatoid Arthritis", description: "Autoimmune disorder assessment" },
];

interface DiseaseGridProps {
    onSelect: (trait: string) => void;
}

export default function DiseaseGrid({ onSelect }: DiseaseGridProps) {
    const [searchInput, setSearchInput] = useState("");

    const filteredDiseases = diseases.filter(disease =>
        disease.name.toLowerCase().includes(searchInput.toLowerCase()) ||
        disease.description.toLowerCase().includes(searchInput.toLowerCase())
    );

    return (
        <div className="w-full max-w-6xl mx-auto space-y-8">
            {/* Search Bar */}
            <div className="w-full max-w-2xl mx-auto relative">
                <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && filteredDiseases.length === 1) {
                            onSelect(filteredDiseases[0].id);
                        }
                    }}
                    placeholder="Search any disease or phenotype (e.g., diabetes, cancer)..."
                    className="w-full px-6 py-4 pr-14 text-base bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                />
                <button
                    onClick={() => {
                        if (filteredDiseases.length === 1) {
                            onSelect(filteredDiseases[0].id);
                        }
                    }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors"
                >
                    <Search size={24} />
                </button>
            </div>

            {/* Disease Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {filteredDiseases.map((disease) => (
                    <button
                        key={disease.id}
                        onClick={() => onSelect(disease.id)}
                        className="group flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all duration-200 text-center min-h-[140px]"
                    >
                        <div className="font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 mb-1 text-base">
                            {disease.name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                            {disease.description}
                        </div>
                    </button>
                ))}
            </div>

            {filteredDiseases.length === 0 && (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    No diseases found matching "{searchInput}"
                </div>
            )}
        </div>
    );
}
