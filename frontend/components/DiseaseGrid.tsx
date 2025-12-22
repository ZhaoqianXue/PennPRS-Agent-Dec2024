import React from 'react';

interface Disease {
    id: string;
    name: string;
    emoji: string;
    description: string;
}

const diseases: Disease[] = [
    { id: "Alzheimer's disease", name: "Alzheimer's Disease", emoji: "🧠", description: "Neurodegenerative disorder prediction" },
    { id: "Type 2 diabetes", name: "Type 2 Diabetes", emoji: "🩸", description: "Metabolic risk assessment" },
    { id: "Coronary artery disease", name: "Coronary Artery Disease", emoji: "❤️", description: "Cardiovascular health monitoring" },
    { id: "Breast cancer", name: "Breast Cancer", emoji: "🎀", description: "Oncology risk profiling" },
];

interface DiseaseGridProps {
    onSelect: (trait: string) => void;
}

export default function DiseaseGrid({ onSelect }: DiseaseGridProps) {
    return (
        <div className="max-w-4xl mx-auto p-6">
            {/* Header moved to parent component */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {diseases.map((disease) => (
                    <button
                        key={disease.id}
                        onClick={() => onSelect(disease.id)}
                        className="group flex flex-col items-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md border-2 border-transparent hover:border-blue-500 transition-all duration-200 text-left"
                    >
                        <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-200">
                            {disease.emoji}
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            {disease.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                            {disease.description}
                        </p>
                    </button>
                ))}
            </div>
        </div>
    );
}
