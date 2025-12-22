import React, { useState, useEffect } from 'react';
import { Upload, Settings2, Info } from 'lucide-react';

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

interface TrainingConfigFormProps {
    onSubmit: (config: TrainingConfig) => void;
    defaultTrait?: string;
    onCancel?: () => void;
}

export default function TrainingConfigForm({ onSubmit, defaultTrait, onCancel }: TrainingConfigFormProps) {
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
    }, [defaultTrait]);

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
        <div className="w-full max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
            {/* Header */}
            <div className="flex items-center justify-between pb-6 border-b border-gray-100 dark:border-gray-800">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span className="bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 p-2 rounded-lg">
                            <Settings2 className="w-6 h-6" />
                        </span>
                        Train Custom Model
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">Configure parameters to train a new Polygenic Risk Score model.</p>
                </div>
            </div>

            {/* Body */}
            <div className="space-y-10">

                {/* 1. Job Details */}
                <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                        <span className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-bold">1</span>
                        Job Details
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Name</label>
                            <input
                                type="text"
                                value={jobName}
                                onChange={(e) => setJobName(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
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
                                className={`w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-sm outline-none transition-all ${defaultTrait
                                    ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-not-allowed'
                                    : 'bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500'
                                    }`}
                            />
                        </div>
                    </div>
                </section>

                {/* 2. Target Ancestry & Methods */}
                <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                        <span className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-bold">2</span>
                        Methodology
                    </h3>
                    <div className="space-y-6">
                        <div className="space-y-3">
                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Target Ancestry</label>
                            <div className="flex flex-wrap gap-2">
                                {['EUR', 'AFR', 'EAS', 'SAS', 'AMR', 'MIX'].map(anc => (
                                    <button
                                        key={anc}
                                        onClick={() => setAncestry(anc)}
                                        className={`px-5 py-2.5 rounded-lg text-sm font-medium border transition-all ${ancestry === anc
                                            ? 'bg-blue-600 border-blue-600 text-white shadow-md'
                                            : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800'
                                            }`}
                                    >
                                        {anc}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-3">
                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Statistical Methods</label>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {['Clumping+Thresholding', 'PRScs', 'Lassosum', 'LDpred2'].map(method => (
                                    <label key={method} className={`flex items-center gap-3 px-4 py-3 border rounded-xl cursor-pointer transition-all ${methods.includes(method)
                                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-500'
                                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                                        }`}>
                                        <input
                                            type="checkbox"
                                            checked={methods.includes(method)}
                                            onChange={() => toggleMethod(method)}
                                            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                                        />
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{method}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center gap-4 pt-2 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800">
                            <label className="flex items-center gap-3 cursor-pointer">
                                <div className={`w-12 h-7 rounded-full p-1 transition-colors ${ensemble ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`} onClick={() => setEnsemble(!ensemble)}>
                                    <div className={`w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform ${ensemble ? 'translate-x-5' : ''}`} />
                                </div>
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Enable Ensemble Learning</span>
                            </label>
                            <div className="h-4 w-px bg-gray-300 dark:bg-gray-700 mx-2"></div>
                            <div className="text-xs text-gray-500 flex items-center gap-1.5">
                                <Info className="w-4 h-4" />
                                Combines selected methods for improved prediction accuracy
                            </div>
                        </div>
                    </div>
                </section>

                {/* 3. Data Source */}
                <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                        <span className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-bold">3</span>
                        Data Source
                    </h3>
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <button
                                onClick={() => setDataSourceType("public")}
                                className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden ${dataSourceType === 'public' ? 'border-blue-500 ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                            >
                                <div className="font-bold text-base mb-1 text-gray-900 dark:text-white">Public GWAS Catalog</div>
                                <div className="text-sm text-gray-500">Use curated summary statistics from the PGS Catalog</div>
                            </button>
                            <button
                                onClick={() => setDataSourceType("upload")}
                                className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden ${dataSourceType === 'upload' ? 'border-blue-500 ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                            >
                                <div className="font-bold text-base mb-1 text-gray-900 dark:text-white">Upload Custom Data</div>
                                <div className="text-sm text-gray-500">Use your own GWAS summary statistics file</div>
                            </button>
                        </div>

                        {dataSourceType === 'public' ? (
                            <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">GWAS ID (Optional)</label>
                                <input
                                    type="text"
                                    value={gwasId}
                                    onChange={(e) => setGwasId(e.target.value)}
                                    placeholder="e.g. GCST001234 (Leave empty to auto-search)"
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                />
                            </div>
                        ) : (
                            <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:border-blue-400 dark:hover:border-blue-700 transition-all animate-in fade-in slide-in-from-top-2 duration-300 group">
                                <input
                                    type="file"
                                    className="hidden"
                                    id="file-upload"
                                    onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
                                />
                                <label htmlFor="file-upload" className="cursor-pointer w-full h-full flex flex-col items-center">
                                    <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-500 dark:text-blue-400 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                        <Upload className="w-6 h-6" />
                                    </div>
                                    <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">{uploadedFile ? uploadedFile.name : "Click to select file"}</p>
                                    <p className="text-xs text-gray-500 mt-1">Supported formats: .txt, .tsv, .gz (Max 500MB)</p>
                                </label>
                            </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Phenotype Type</label>
                                <select
                                    value={traitType}
                                    onChange={(e) => setTraitType(e.target.value as any)}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                >
                                    <option value="Case-Control">Case-Control (Disease)</option>
                                    <option value="Continuous">Continuous (Quantitative)</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sample Size (N)</label>
                                <input
                                    type="number"
                                    value={sampleSize}
                                    onChange={(e) => setSampleSize(e.target.value === '' ? '' : Number(e.target.value))}
                                    placeholder="e.g. 50000"
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                {/* Advanced */}
                <div className="pt-2 pb-8">
                    <button
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-2 transition-colors"
                    >
                        <Settings2 className="w-4 h-4" />
                        {showAdvanced ? "Hide Advanced Options" : "Show Advanced Options"}
                    </button>

                    {showAdvanced && (
                        <div className="mt-6 p-6 bg-gray-50 dark:bg-gray-800/50 rounded-xl grid grid-cols-1 md:grid-cols-3 gap-6 border border-gray-100 dark:border-gray-800 animate-in fade-in slide-in-from-top-2 duration-300">
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">Clumping Window (kb)</label>
                                <input type="number" value={kb} onChange={(e) => setKb(Number(e.target.value))} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">LD r² Threshold</label>
                                <input type="number" step="0.1" value={r2} onChange={(e) => setR2(Number(e.target.value))} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">P-value Threshold</label>
                                <input type="text" value={pvalThr} onChange={(e) => setPvalThr(e.target.value)} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer Actions */}
                <div className="flex items-center justify-end gap-4 pt-6 border-t border-gray-200 dark:border-gray-800">
                    {onCancel && (
                        <button
                            onClick={onCancel}
                            className="px-6 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                    )}
                    <button
                        onClick={handleSubmit}
                        className="px-8 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200"
                    >
                        Start Training Job
                    </button>
                </div>

            </div>
        </div>
    );
}
