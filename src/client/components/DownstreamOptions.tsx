import React from 'react';
import { BarChart2, Share2, FlaskConical, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

interface DownstreamOptionsProps {
    modelId: string;
    trait: string;
    onAction: (action: string) => void;
}

export default function DownstreamOptions({ modelId, trait, onAction }: DownstreamOptionsProps) {
    const options = [
        {
            id: 'benchmark',
            title: 'Benchmark Performance',
            description: 'Evaluate this model against specific test cohorts (e.g., UKB, AoU).',
            icon: BarChart2,
            color: 'bg-blue-500',
            textColor: 'text-blue-500',
            bgColor: 'bg-blue-50 dark:bg-blue-900/20'
        },
        {
            id: 'proteomics',
            title: 'Proteomics Integration',
            description: 'Analyze correlation with protein levels and other biomarkers.',
            icon: FlaskConical,
            color: 'bg-purple-500',
            textColor: 'text-purple-500',
            bgColor: 'bg-purple-50 dark:bg-purple-900/20'
        },
        {
            id: 'ensemble',
            title: 'Create Ensemble',
            description: 'Combine this model with others to improve prediction accuracy.',
            icon: Share2,
            color: 'bg-green-500',
            textColor: 'text-green-500',
            bgColor: 'bg-green-50 dark:bg-green-900/20'
        }
    ];

    return (
        <div className="w-full mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            {options.map((opt, idx) => (
                <motion.div
                    key={opt.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md transition-all cursor-pointer group"
                    onClick={() => onAction(opt.id)}
                >
                    <div className={`w-10 h-10 rounded-lg ${opt.bgColor} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                        <opt.icon className={`w-5 h-5 ${opt.textColor}`} />
                    </div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 transition-colors">
                        {opt.title}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                        {opt.description}
                    </p>
                </motion.div>
            ))}
        </div>
    );
}
