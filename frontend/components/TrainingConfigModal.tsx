import React, { useState, useEffect } from 'react';
import { X, Upload, Settings2, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export interface TrainingConfig {
    jobName: string;
    trait: string;
    ancestry: string;
    methods: string[];
    ensemble: boolean;
    dataSourceType: "public" | "upload";
    gwasId?: string; // For public
    uploadedFileName?: string; // For upload
    traitType: "Continuous" | "Case-Control";
    sampleSize: number;
    advanced?: {
        kb: number;
        r2: number;
        pval_thr: string;
    };
}

interface TrainingConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (config: TrainingConfig) => void;
    defaultTrait?: string;
}

export default function TrainingConfigModal({ isOpen, onClose, onSubmit, defaultTrait }: TrainingConfigModalProps) {
    // Form State
    const [jobName, setJobName] = useState("");
    const [trait, setTrait] = useState("");
    const [ancestry, setAncestry] = useState("EUR");
    const [methods, setMethods] = useState<string[]>(["Clumping+Thresholding"]);
    const [ensemble, setEnsemble] = useState(false);

    // Data Source
    const [dataSourceType, setDataSourceType] = useState<"public" | "upload">("public");
    const [gwasId, setGwasId] = useState("");
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);

    // Metadata
    const [traitType, setTraitType] = useState<"Continuous" | "Case-Control">("Case-Control"); // Default for disease
    const [sampleSize, setSampleSize] = useState<number | "">("");

    // Advanced
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [kb, setKb] = useState(250);
    const [r2, setR2] = useState(0.1);
    const [pvalThr, setPvalThr] = useState("5e-8");

    // Initialize/Reset
    useEffect(() => {
        if (isOpen) {
            const initialTrait = defaultTrait || "Alzheimer's disease";
            setTrait(initialTrait);
            setJobName(`Train_${initialTrait.split(' ')[0].replace(/[^a-zA-Z0-9]/g, '')}_${new Date().toISOString().slice(0, 10)}`);
            setAncestry("EUR");
            setMethods(["Clumping+Thresholding"]);
            setEnsemble(false);
            setDataSourceType("public");
            setGwasId("");
            setUploadedFile(null);
            setTraitType("Case-Control");
            setSampleSize("");
        }
    }, [isOpen, defaultTrait]);

    const handleSubmit = () => {
        if (!jobName || !trait || !sampleSize) {
            alert("Please fill in required fields (Job Name, Trait, Sample Size)");
            return;
        }

        const config: TrainingConfig = {
            jobName,
            trait,
            ancestry,
            methods,
            ensemble,
            dataSourceType,
            gwasId: dataSourceType === 'public' ? gwasId : undefined,
            uploadedFileName: uploadedFile?.name,
            traitType,
            sampleSize: Number(sampleSize),
            advanced: showAdvanced ? {
                kb,
                r2,
                pval_thr: pvalThr
            } : undefined
        };
        onSubmit(config);
    };

    const toggleMethod = (m: string) => {
        setMethods(prev => {
            if (prev.includes(m)) {
                if (prev.length === 1) return prev; // Must have at least one
                return prev.filter(item => item !== m);
            } else {
                return [...prev, m];
            }
        });
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/40 backdrop-blur-[2px]"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 10 }}
                        className="relative w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 flex flex-col max-h-[90vh] overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-800 shrink-0">
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                    <span className="bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 p-1.5 rounded-lg">
                                        <Settings2 className="w-5 h-5" />
                                    </span>
                                    Train Custom Model
                                </h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Configure PRS calculation parameters</p>
                            </div>
                            <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Body - Scrollable */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-8">

                            {/* 1. Job Details */}
                            <section>
                                <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                                    <span className="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center text-xs">1</span>
                                    Job Details
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Name</label>
                                        <input
                                            type="text"
                                            value={jobName}
                                            onChange={(e) => setJobName(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g. Alzheimer_EUR_001"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Name</label>
                                        <input
                                            type="text"
                                            value={trait}
                                            onChange={(e) => !defaultTrait && setTrait(e.target.value)}
                                            readOnly={!!defaultTrait}
                                            className={`w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-sm outline-none ${defaultTrait
                                                ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-not-allowed'
                                                : 'bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500'
                                                }`}
                                        />
                                    </div>
                                </div>
                            </section>

                            {/* 2. Target Ancestry & Methods */}
                            <section>
                                <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                                    <span className="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center text-xs">2</span>
                                    Methodology
                                </h3>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Target Ancestry</label>
                                        <div className="flex flex-wrap gap-2">
                                            {['EUR', 'AFR', 'EAS', 'SAS', 'AMR', 'MIX'].map(anc => (
                                                <button
                                                    key={anc}
                                                    onClick={() => setAncestry(anc)}
                                                    className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${ancestry === anc
                                                        ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300'
                                                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700'
                                                        }`}
                                                >
                                                    {anc}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Methods</label>
                                        <div className="flex flex-wrap gap-3">
                                            {['Clumping+Thresholding', 'PRScs', 'Lassosum', 'LDpred2'].map(method => (
                                                <label key={method} className="flex items-center gap-2 px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800">
                                                    <input
                                                        type="checkbox"
                                                        checked={methods.includes(method)}
                                                        onChange={() => toggleMethod(method)}
                                                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                                    />
                                                    <span className="text-sm text-gray-700 dark:text-gray-300">{method}</span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4 pt-2">
                                        <label className="flex items-center gap-2 cursor-pointer">
                                            <div className={`w-10 h-6 rounded-full p-1 transition-colors ${ensemble ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`} onClick={() => setEnsemble(!ensemble)}>
                                                <div className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform ${ensemble ? 'translate-x-4' : ''}`} />
                                            </div>
                                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Enable Ensemble Learning</span>
                                        </label>
                                        <div className="text-xs text-gray-500 flex items-center gap-1">
                                            <Info className="w-3 h-3" />
                                            Combines selected methods for better accuracy
                                        </div>
                                    </div>
                                </div>
                            </section>

                            {/* 3. Data Source */}
                            <section>
                                <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                                    <span className="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center text-xs">3</span>
                                    Data Source
                                </h3>
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <button
                                            onClick={() => setDataSourceType("public")}
                                            className={`p-4 rounded-xl border text-left transition-all ${dataSourceType === 'public' ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'}`}
                                        >
                                            <div className="font-semibold text-sm mb-1 text-gray-900 dark:text-white">Public GWAS</div>
                                            <div className="text-xs text-gray-500">Use curated summary stats from Catalog</div>
                                        </button>
                                        <button
                                            onClick={() => setDataSourceType("upload")}
                                            className={`p-4 rounded-xl border text-left transition-all ${dataSourceType === 'upload' ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'}`}
                                        >
                                            <div className="font-semibold text-sm mb-1 text-gray-900 dark:text-white">Upload Data</div>
                                            <div className="text-xs text-gray-500">Use your own summary statistics file</div>
                                        </button>
                                    </div>

                                    {dataSourceType === 'public' ? (
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">GWAS ID (Optional)</label>
                                            <input
                                                type="text"
                                                value={gwasId}
                                                onChange={(e) => setGwasId(e.target.value)}
                                                placeholder="e.g. GCST001234 (Leave empty to auto-search)"
                                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>
                                    ) : (
                                        <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                            <input
                                                type="file"
                                                className="hidden"
                                                id="file-upload"
                                                onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
                                            />
                                            <label htmlFor="file-upload" className="cursor-pointer w-full h-full flex flex-col items-center">
                                                <Upload className="w-8 h-8 text-gray-400 mb-2" />
                                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{uploadedFile ? uploadedFile.name : "Click to Upload"}</p>
                                                <p className="text-xs text-gray-500 mt-1">.txt, .tsv, .gz supported (Max 500MB)</p>
                                            </label>
                                        </div>
                                    )}

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Type</label>
                                            <select
                                                value={traitType}
                                                onChange={(e) => setTraitType(e.target.value as any)}
                                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                            >
                                                <option value="Case-Control">Case-Control (Disease)</option>
                                                <option value="Continuous">Continuous (Quantitative)</option>
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sample Size</label>
                                            <input
                                                type="number"
                                                value={sampleSize}
                                                onChange={(e) => setSampleSize(e.target.value === '' ? '' : Number(e.target.value))}
                                                placeholder="e.g. 50000"
                                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </section>

                            {/* Advanced */}
                            <div className="pt-2">
                                <button
                                    onClick={() => setShowAdvanced(!showAdvanced)}
                                    className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                                >
                                    {showAdvanced ? "Hide Advanced Options" : "Show Advanced Options"}
                                </button>

                                {showAdvanced && (
                                    <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg grid grid-cols-1 md:grid-cols-3 gap-4 border border-gray-100 dark:border-gray-800">
                                        <div className="space-y-1">
                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">Clumping Window (kb)</label>
                                            <input type="number" value={kb} onChange={(e) => setKb(Number(e.target.value))} className="w-full px-2 py-1.5 rounded border text-sm" />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">LD r² Threshold</label>
                                            <input type="number" step="0.1" value={r2} onChange={(e) => setR2(Number(e.target.value))} className="w-full px-2 py-1.5 rounded border text-sm" />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">P-value Threshold</label>
                                            <input type="text" value={pvalThr} onChange={(e) => setPvalThr(e.target.value)} className="w-full px-2 py-1.5 rounded border text-sm" />
                                        </div>
                                    </div>
                                )}
                            </div>

                        </div>

                        {/* Footer */}
                        <div className="p-6 border-t border-gray-100 dark:border-gray-800 shrink-0 flex justify-end gap-3 bg-gray-50 dark:bg-gray-900/50">
                            <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors">
                                Cancel
                            </button>
                            <button onClick={handleSubmit} className="px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors flex items-center gap-2">
                                Start Training Job
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
