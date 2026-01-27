
import React from 'react';

interface ProgressBarProps {
    status: string;
    total: number;
    fetched: number;
    currentAction: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ status, total, fetched, currentAction }) => {
    // Calculate percentage, default to 5% to show something happening if 0
    const percentage = total > 0 ? Math.min(100, Math.max(5, (fetched / total) * 100)) : 0;

    return (
        <div className="w-full max-w-md p-4 bg-white dark:bg-gray-800 rounded-lg border border-blue-100 dark:border-blue-900 shadow-sm animate-in fade-in zoom-in duration-300">
            <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                    {status === 'completed' ? 'Initial Search Complete' : 'Searching Models...'}
                </span>
                <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                    {fetched} / {total > 0 ? total : '?'} Models
                </span>
            </div>

            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-2 overflow-hidden">
                <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>

            <div className="flex items-center gap-2">
                {status !== 'completed' && (
                    <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                <span className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {currentAction || "Initializing..."}
                </span>
            </div>
        </div>
    );
};
