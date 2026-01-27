import React, { useState, useEffect } from 'react';
import { X, Upload, Settings2, Info, Database, Search, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GWASSearchModal, { GWASEntry } from './GWASSearchModal';

export interface TrainingConfig {
    jobName: string;
    email: string; // New Required
    jobType: "single" | "multi"; // New Option
    trait: string;
    ancestry: string;
    methods: string[];
    ensemble: boolean;
    dataSourceType: "public" | "upload";
    database?: "GWAS Catalog" | "FinnGen"; // New Option
    gwasId?: string; // For public
    gwasEntry?: GWASEntry; // Selected GWAS entry
    uploadedFileName?: string; // For upload
    traitType: "Continuous" | "Case-Control";
    sampleSize: number;
    advanced?: {
        kb: number;
        r2: number;
        pval_thr: string;
        delta?: string;
        nlambda?: number;
        lambda_min_ratio?: number;
        alpha?: string;
        p_seq?: string;
        sparse?: boolean;
        Ll?: number;
        Lc?: number;
        ndelta?: number;
        phi?: string;
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
    const [email, setEmail] = useState(""); // New State
    const [jobType, setJobType] = useState<"single" | "multi">("single"); // New State
    const [trait, setTrait] = useState("");
    const [ancestry, setAncestry] = useState("EUR");
    const [methods, setMethods] = useState<string[]>(["Clumping+Thresholding"]);
    const [ensemble, setEnsemble] = useState(false);

    // Data Source
    const [dataSourceType, setDataSourceType] = useState<"public" | "upload">("public");
    const [database, setDatabase] = useState<"GWAS Catalog" | "FinnGen">("GWAS Catalog"); // New State
    const [gwasId, setGwasId] = useState("");
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);

    // GWAS Search Modal
    const [isGwasSearchOpen, setIsGwasSearchOpen] = useState(false);
    const [selectedGwasEntry, setSelectedGwasEntry] = useState<GWASEntry | null>(null);

    // Metadata
    // Metadata
    const [traitType, setTraitType] = useState<"Continuous" | "Case-Control">("Case-Control"); // Default for disease
    const [sampleSize, setSampleSize] = useState<number | "">("");

    // New State for Binary Sample Size
    const [binarySampleSizeType, setBinarySampleSizeType] = useState<"nCaseControl" | "nEff">("nCaseControl");
    const [nCase, setNCase] = useState<number | "">("");
    const [nControl, setNControl] = useState<number | "">("");

    // Advanced
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [kb, setKb] = useState(250);
    const [r2, setR2] = useState(0.1);
    const [pvalThr, setPvalThr] = useState("5e-8");
    // New Advanced States
    const [delta, setDelta] = useState("0.001,0.01,0.1,1.0");
    const [nlambda, setNlambda] = useState(30);
    const [lambdaMinRatio, setLambdaMinRatio] = useState(0.01);
    const [alpha, setAlpha] = useState("0.7, 1.0, 1.4");
    const [pSeq, setPSeq] = useState("1e-05,3.2e-05,0.0001,0.00032,0.001,0.0032,0.01,0.032,0.1,0.32,1.0");
    const [sparse, setSparse] = useState(false);
    const [Ll, setLl] = useState(5);
    const [Lc, setLc] = useState(5);
    const [ndelta, setNdelta] = useState(5);
    const [phi, setPhi] = useState("1e-2");

    // Initialize/Reset
    useEffect(() => {
        if (isOpen) {
            const initialTrait = defaultTrait || "Alzheimer's disease";
            setTrait(initialTrait);
            setJobName(`Train_${initialTrait.split(' ')[0].replace(/[^a-zA-Z0-9]/g, '')}_${new Date().toISOString().slice(0, 10)}`);
            setEmail("");
            setJobType("single");
            setAncestry("EUR");
            setMethods(["LDpred2-pseudo"]);
            setEnsemble(false);
            setDataSourceType("public");
            setDatabase("GWAS Catalog");
            setGwasId("");
            setUploadedFile(null);
            setTraitType("Case-Control");
            setSampleSize("");
            setSelectedGwasEntry(null);
            setIsGwasSearchOpen(false);
        }
    }, [isOpen, defaultTrait]);

    // Logic to handle FinnGen Ancestry Lock
    useEffect(() => {
        if (dataSourceType === 'public' && selectedGwasEntry?.database === 'finngen') {
            setAncestry('EUR');
        }
    }, [dataSourceType, selectedGwasEntry]);


    const handleSubmit = () => {
        let finalSampleSize = Number(sampleSize);

        // Calculate Sample Size for Binary if using Ncase/Ncontrol
        if (traitType === 'Case-Control' && binarySampleSizeType === 'nCaseControl') {
            if (!nCase || !nControl) {
                alert("Please calculate Ncase and NControl");
                return;
            }
            // Neff = 4 / (1/Ncase + 1/Ncontrol)
            finalSampleSize = 4 / ((1 / Number(nCase)) + (1 / Number(nControl)));
        }

        if (!jobName || !trait || !finalSampleSize || !email) {
            alert("Please fill in required fields (Job Name, Trait, Sample Size, Email)");
            return;
        }

        // Validate GWAS entry selection for public data source
        if (dataSourceType === 'public' && !selectedGwasEntry) {
            alert("Please select a GWAS study from the database");
            return;
        }

        const config: TrainingConfig = {
            jobName,
            email,
            jobType: "single", // Hardcoded
            trait,
            ancestry,
            methods,
            ensemble,
            dataSourceType,
            database: dataSourceType === 'public' && selectedGwasEntry
                ? (selectedGwasEntry.database === 'gwas_catalog' ? 'GWAS Catalog' : 'FinnGen')
                : undefined,
            gwasId: dataSourceType === 'public' && selectedGwasEntry ? selectedGwasEntry.id : undefined,
            gwasEntry: dataSourceType === 'public' ? selectedGwasEntry ?? undefined : undefined,
            uploadedFileName: uploadedFile?.name,
            traitType,
            sampleSize: Math.round(finalSampleSize),
            advanced: showAdvanced ? {
                kb,
                r2,
                pval_thr: pvalThr,
                delta,
                nlambda,
                lambda_min_ratio: lambdaMinRatio,
                alpha,
                p_seq: pSeq,
                sparse,
                Ll,
                Lc,
                ndelta,
                phi
            } : undefined
        };
        onSubmit(config);
    };


    const toggleMethod = (m: string) => {
        setMethods(prev => {
            let newMethods;
            if (prev.includes(m)) {
                if (prev.length === 1) return prev; // Must have at least one
                newMethods = prev.filter(item => item !== m);
            } else {
                newMethods = [...prev, m];
            }

            // Auto-disable ensemble if only 1 method
            if (newMethods.length <= 1) {
                setEnsemble(false);
            }
            return newMethods;
        });
    };

    return (
        <>
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
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Name <span className="text-red-500">*</span></label>
                                            <input
                                                type="text"
                                                value={jobName}
                                                onChange={(e) => setJobName(e.target.value)}
                                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                                placeholder="e.g. Alzheimer_EUR_001"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email Address <span className="text-red-500">*</span></label>
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                                placeholder="For notification"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Type</label>
                                            <div className="px-3 py-2 rounded-lg border border-gray-200 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 text-sm text-gray-500">
                                                Single Trait
                                            </div>
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

                                {/* 2. Data Source */}
                                <section>
                                    <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                                        <span className="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center text-xs">2</span>
                                        Data Source
                                    </h3>
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <button
                                                onClick={() => setDataSourceType("public")}
                                                className={`p-4 rounded-xl border text-left transition-all ${dataSourceType === 'public' ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'}`}
                                            >
                                                <div className="font-semibold text-sm mb-1 text-gray-900 dark:text-white">Query Data</div>
                                                <div className="text-xs text-gray-500">Query Public GWAS Catalog or FinnGen</div>
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
                                            <div className="space-y-3">
                                                {/* GWAS Search Button / Selected Entry Display */}
                                                {selectedGwasEntry ? (
                                                    <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-800">
                                                        <div className="flex items-start justify-between gap-3">
                                                            <div className="flex-1 min-w-0">
                                                                <div className="flex items-center gap-2 mb-1">
                                                                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${selectedGwasEntry.database === 'finngen'
                                                                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                                                                        : 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                                                                        }`}>
                                                                        {selectedGwasEntry.database === 'finngen' ? 'FinnGen' : 'GWAS Catalog'}
                                                                    </span>
                                                                    <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                                                                        {selectedGwasEntry.id}
                                                                    </span>
                                                                </div>
                                                                <h4 className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                                                                    {selectedGwasEntry.trait}
                                                                </h4>
                                                                {(selectedGwasEntry.nCases || selectedGwasEntry.sampleInfo) && (
                                                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                                                                        {selectedGwasEntry.database === 'finngen'
                                                                            ? `${selectedGwasEntry.nCases?.toLocaleString()} cases, ${selectedGwasEntry.nControls?.toLocaleString()} controls`
                                                                            : selectedGwasEntry.sampleInfo}
                                                                    </p>
                                                                )}
                                                            </div>
                                                            <button
                                                                onClick={() => setIsGwasSearchOpen(true)}
                                                                className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium shrink-0"
                                                            >
                                                                Change
                                                            </button>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <button
                                                        onClick={() => setIsGwasSearchOpen(true)}
                                                        className="w-full p-4 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all flex items-center justify-center gap-3 group"
                                                    >
                                                        <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors">
                                                            <Search className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                                        </div>
                                                        <div className="text-left">
                                                            <div className="text-sm font-medium text-gray-900 dark:text-white">Search GWAS Database</div>
                                                            <div className="text-xs text-gray-500">Browse GWAS Catalog and FinnGen studies</div>
                                                        </div>
                                                        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors ml-auto" />
                                                    </button>
                                                )}
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

                                        {/* Ancestry Selection - Moved here */}
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ancestry</label>
                                            <div className="flex flex-wrap gap-2">
                                                {selectedGwasEntry?.database === 'finngen' && dataSourceType === 'public' ? (
                                                    <button
                                                        className="px-4 py-2 rounded-lg text-sm font-medium border border-blue-50 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300 cursor-not-allowed opacity-80"
                                                    >
                                                        European (EUR)
                                                    </button>
                                                ) : (
                                                    ['EUR', 'AFR', 'EAS', 'SAS', 'AMR'].map(anc => (
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
                                                    ))
                                                )}
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Type</label>
                                                <div className="flex items-center gap-4">
                                                    <label className="flex items-center gap-2 cursor-pointer">
                                                        <input
                                                            type="radio"
                                                            name="modalTraitType"
                                                            value="Case-Control"
                                                            checked={traitType === "Case-Control"}
                                                            onChange={() => setTraitType("Case-Control")}
                                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                        />
                                                        <span className="text-sm text-gray-700 dark:text-gray-300">Binary</span>
                                                    </label>
                                                    <label className="flex items-center gap-2 cursor-pointer">
                                                        <input
                                                            type="radio"
                                                            name="modalTraitType"
                                                            value="Continuous"
                                                            checked={traitType === "Continuous"}
                                                            onChange={() => setTraitType("Continuous")}
                                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                        />
                                                        <span className="text-sm text-gray-700 dark:text-gray-300">Continuous</span>
                                                    </label>
                                                </div>
                                            </div>

                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sample Size</label>

                                                {traitType === 'Case-Control' ? (
                                                    <div className="space-y-2">
                                                        <div className="flex items-center gap-3 mb-2">
                                                            <label className="flex items-center gap-1.5 cursor-pointer">
                                                                <input
                                                                    type="radio"
                                                                    name="modalBinarySampleSizeType"
                                                                    value="nCaseControl"
                                                                    checked={binarySampleSizeType === "nCaseControl"}
                                                                    onChange={() => setBinarySampleSizeType("nCaseControl")}
                                                                    className="w-3 h-3 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                                />
                                                                <span className="text-xs text-gray-600 dark:text-gray-400">Ncase & Ncontrol</span>
                                                            </label>
                                                            <label className="flex items-center gap-1.5 cursor-pointer">
                                                                <input
                                                                    type="radio"
                                                                    name="modalBinarySampleSizeType"
                                                                    value="nEff"
                                                                    checked={binarySampleSizeType === "nEff"}
                                                                    onChange={() => setBinarySampleSizeType("nEff")}
                                                                    className="w-3 h-3 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                                />
                                                                <span className="text-xs text-gray-600 dark:text-gray-400">Neff</span>
                                                            </label>
                                                        </div>

                                                        {binarySampleSizeType === 'nCaseControl' ? (
                                                            <div className="grid grid-cols-2 gap-2">
                                                                <input
                                                                    type="number"
                                                                    value={nCase}
                                                                    onChange={(e) => setNCase(e.target.value === '' ? '' : Number(e.target.value))}
                                                                    placeholder="N Case"
                                                                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                                                />
                                                                <input
                                                                    type="number"
                                                                    value={nControl}
                                                                    onChange={(e) => setNControl(e.target.value === '' ? '' : Number(e.target.value))}
                                                                    placeholder="N Control"
                                                                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                                                />
                                                            </div>
                                                        ) : (
                                                            <input
                                                                type="number"
                                                                value={sampleSize}
                                                                onChange={(e) => setSampleSize(e.target.value === '' ? '' : Number(e.target.value))}
                                                                placeholder="Neff"
                                                                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                                            />
                                                        )}
                                                    </div>
                                                ) : (
                                                    <input
                                                        type="number"
                                                        value={sampleSize}
                                                        onChange={(e) => setSampleSize(e.target.value === '' ? '' : Number(e.target.value))}
                                                        placeholder="N"
                                                        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                                                    />
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </section>

                                {/* 3. Methodology */}
                                <section>
                                    <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                                        <span className="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center text-xs">3</span>
                                        Methodology
                                    </h3>
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Methods</label>
                                            <div className="flex flex-wrap gap-3">
                                                {['LDpred2-pseudo', 'Lassosum2-pseudo', 'C+T-pseudo'].map(method => (
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

                                        <div className={`flex items-center gap-4 pt-2 ${methods.length <= 1 ? 'opacity-50 cursor-not-allowed' : ''}`}>
                                            <label className={`flex items-center gap-3 ${methods.length <= 1 ? 'cursor-not-allowed' : 'cursor-pointer'}`}>
                                                <div
                                                    className={`w-12 h-7 rounded-full p-1 transition-colors ${ensemble ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}
                                                    onClick={() => methods.length > 1 && setEnsemble(!ensemble)}
                                                >
                                                    <div className={`w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform ${ensemble ? 'translate-x-5' : ''}`} />
                                                </div>
                                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    {ensemble ? "Ensemble Learning On" : "Ensemble Learning Off"}
                                                </span>
                                            </label>
                                            <div className="text-xs text-gray-500 flex items-center gap-1">
                                                <Info className="w-3 h-3" />
                                                Note: If multiple methods are selected, we provide an option to train an ensemble PRS based on the selected methods.
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
                                        <div className="mt-4 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">

                                            {/* C+T-pseudo */}
                                            {methods.includes('C+T-pseudo') && (
                                                <div className="border border-gray-100 dark:border-gray-800 rounded-lg p-4 bg-gray-50/50 dark:bg-gray-800/30">
                                                    <h4 className="text-xs font-semibold text-gray-900 dark:text-gray-100 mb-3">C+T-pseudo</h4>
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">kb</label>
                                                            <input type="number" value={kb} onChange={(e) => setKb(Number(e.target.value))} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">P-value threshold</label>
                                                            <input type="text" value={pvalThr} onChange={(e) => setPvalThr(e.target.value)} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">R2</label>
                                                            <input type="number" step="0.1" value={r2} onChange={(e) => setR2(Number(e.target.value))} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Lassosum2-pseudo */}
                                            {methods.includes('Lassosum2-pseudo') && (
                                                <div className="border border-gray-100 dark:border-gray-800 rounded-lg p-4 bg-gray-50/50 dark:bg-gray-800/30">
                                                    <h4 className="text-xs font-semibold text-gray-900 dark:text-gray-100 mb-3">Lassosum2-pseudo</h4>
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">delta</label>
                                                            <input type="text" value={delta} onChange={(e) => setDelta(e.target.value)} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">nlambda</label>
                                                            <input type="number" value={nlambda} onChange={(e) => setNlambda(Number(e.target.value))} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">lambda min ratio</label>
                                                            <input type="number" step="0.01" value={lambdaMinRatio} onChange={(e) => setLambdaMinRatio(Number(e.target.value))} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {/* LDpred2-pseudo */}
                                            {methods.includes('LDpred2-pseudo') && (
                                                <div className="border border-gray-100 dark:border-gray-800 rounded-lg p-4 bg-gray-50/50 dark:bg-gray-800/30">
                                                    <h4 className="text-xs font-semibold text-gray-900 dark:text-gray-100 mb-3">LDpred2-pseudo</h4>
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">alpha</label>
                                                            <input type="text" value={alpha} onChange={(e) => setAlpha(e.target.value)} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">P-seq</label>
                                                            <input type="text" value={pSeq} onChange={(e) => setPSeq(e.target.value)} className="w-full px-2 py-1.5 rounded border dark:bg-gray-800 dark:border-gray-700 text-xs" />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">Sparse</label>
                                                            <div className="flex bg-gray-100 dark:bg-gray-800 p-0.5 rounded-lg w-fit border border-gray-200 dark:border-gray-700">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => setSparse(true)}
                                                                    className={`px-3 py-1 rounded-md text-[10px] font-bold transition-all duration-200 ${sparse
                                                                        ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600 dark:text-blue-400'
                                                                        : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                                                                >
                                                                    TRUE
                                                                </button>
                                                                <button
                                                                    type="button"
                                                                    onClick={() => setSparse(false)}
                                                                    className={`px-3 py-1 rounded-md text-[10px] font-bold transition-all duration-200 ${!sparse
                                                                        ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600 dark:text-blue-400'
                                                                        : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                                                                >
                                                                    FALSE
                                                                </button>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
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

            {/* GWAS Search Modal */}
            <GWASSearchModal
                isOpen={isGwasSearchOpen}
                onClose={() => setIsGwasSearchOpen(false)}
                onSelect={(entry) => {
                    setSelectedGwasEntry(entry);
                    // Auto-populate sample size if available
                    if (entry.nCases && entry.nControls) {
                        setTraitType('Case-Control');
                        setBinarySampleSizeType('nCaseControl');
                        setNCase(entry.nCases);
                        setNControl(entry.nControls);
                    }
                }}
                initialSelection={selectedGwasEntry}
            />
        </>
    );
}
