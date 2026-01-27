import React, { useState, useEffect, useRef } from 'react';
import { Upload, Settings2, Info, Search, ChevronRight, ExternalLink, HelpCircle, Loader2 } from 'lucide-react';
import GWASSearchModal, { GWASEntry } from './GWASSearchModal';

export interface TrainingConfig {
    jobName: string;
    email: string; // New Required Field
    jobType: "single" | "multi"; // New Option
    trait: string;
    ancestry: string;
    methods: string[];
    methodologyCategory: "pseudo-training" | "tuning-free"; // NEW
    ensemble: boolean;
    dataSourceType: "public" | "upload";
    database?: "GWAS Catalog" | "FinnGen"; // New Option for public
    gwasId?: string; // For public
    gwasEntry?: GWASEntry; // Selected GWAS entry
    uploadedFileName?: string; // For upload
    traitType: "Continuous" | "Case-Control";
    sampleSize: number;
    // Expanded Advanced Options
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
        // PRS-CS-auto settings
        prscsPhiMode?: "fullyBayesian" | "fixedPhi";
        prscsPhiValue?: string;
    };
}

interface TrainingConfigFormProps {
    onSubmit: (config: TrainingConfig) => void;
    defaultTrait?: string;
    onCancel?: () => void;
    isSubmitting?: boolean;  // New: loading state for submit button
}

export default function TrainingConfigForm({ onSubmit, defaultTrait, onCancel, isSubmitting = false }: TrainingConfigFormProps) {
    // Form State
    const [jobName, setJobName] = useState("");
    const [email, setEmail] = useState(""); // New State
    const [jobType, setJobType] = useState<"single" | "multi">("single"); // New State
    const [trait, setTrait] = useState("");
    const [ancestry, setAncestry] = useState("EUR");
    const [methods, setMethods] = useState<string[]>(["LDpred2-pseudo"]);
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
    const [traitType, setTraitType] = useState<"Continuous" | "Case-Control">("Case-Control"); // Default for disease
    const [sampleSize, setSampleSize] = useState<number | "">("");

    // New State for Binary Sample Size
    const [binarySampleSizeType, setBinarySampleSizeType] = useState<"nCaseControl" | "nEff">("nCaseControl");
    const [nCase, setNCase] = useState<number | "">("");
    const [nControl, setNControl] = useState<number | "">("");

    // Methodology Category State
    const [methodologyCategory, setMethodologyCategory] = useState<"pseudo-training" | "tuning-free">("pseudo-training");

    // PRS-CS-auto Settings
    const [prscsPhiMode, setPrscsPhiMode] = useState<"fullyBayesian" | "fixedPhi">("fullyBayesian");
    const [prscsPhiValue, setPrscsPhiValue] = useState("1e-2");

    const [showAdvanced, setShowAdvanced] = useState(false);
    // C+T-pseudo
    const [kb, setKb] = useState(500);
    const [pvalThr, setPvalThr] = useState("5e-08,5e-07,5e-06,5e-05,0.0005,0.005,0.05,0.5");
    const [r2, setR2] = useState(0.1);

    // Lassosum2-pseudo
    const [delta, setDelta] = useState("0.001,0.01,0.1,1.0");
    const [nlambda, setNlambda] = useState(30);
    const [lambdaMinRatio, setLambdaMinRatio] = useState(0.01);

    // LDpred2-pseudo
    const [alpha, setAlpha] = useState("0.7, 1.0, 1.4");
    const [pSeq, setPSeq] = useState("1e-05,3.2e-05,0.0001,0.00032,0.001,0.0032,0.01,0.032,0.1,0.32,1.0");
    const [sparse, setSparse] = useState(false);

    // Initialize/Reset

    // Initialize/Reset
    useEffect(() => {
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
        // Advanced Defaults Resets could be added here if needed
    }, [defaultTrait]);

    // Logic to handle FinnGen Ancestry Lock
    useEffect(() => {
        if (dataSourceType === 'public' && selectedGwasEntry?.database === 'finngen') {
            setAncestry('EUR');
        }
    }, [dataSourceType, selectedGwasEntry]);

    // Form Validation - All required fields except Ensemble Learning
    const isFormValid = (() => {
        // Job Details
        if (!jobName.trim()) return false;
        if (!email.trim() || !email.includes('@')) return false;
        if (!trait.trim()) return false;

        // Data Source
        if (dataSourceType === 'public') {
            if (!selectedGwasEntry) return false;
        } else {
            if (!uploadedFile) return false;
        }

        // Ancestry
        if (!ancestry) return false;

        // Methodology - at least one method required
        if (methods.length === 0) return false;

        // Sample Size
        if (traitType === 'Case-Control' && binarySampleSizeType === 'nCaseControl') {
            if (!nCase || Number(nCase) <= 0) return false;
            if (!nControl || Number(nControl) <= 0) return false;
        } else {
            if (!sampleSize || Number(sampleSize) <= 0) return false;
        }

        return true;
    })();


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
            jobType: "single", // Hardcoded as per request
            trait,
            ancestry,
            methods,
            methodologyCategory, // NEW
            ensemble,
            dataSourceType,
            database: dataSourceType === 'public' && selectedGwasEntry
                ? (selectedGwasEntry.database === 'gwas_catalog' ? 'GWAS Catalog' : 'FinnGen')
                : undefined,
            gwasId: dataSourceType === 'public' && selectedGwasEntry ? selectedGwasEntry.id : undefined,
            gwasEntry: dataSourceType === 'public' ? selectedGwasEntry ?? undefined : undefined,
            uploadedFileName: uploadedFile?.name,
            traitType,
            sampleSize: Math.round(finalSampleSize), // Round to integer
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
                // PRS-CS-auto settings
                prscsPhiMode: methods.includes('PRS-CS-auto') ? prscsPhiMode : undefined,
                prscsPhiValue: methods.includes('PRS-CS-auto') && prscsPhiMode === 'fixedPhi' ? prscsPhiValue : undefined
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
            <div className="w-full max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
                {/* Body */}
                <div className="space-y-10">

                    {/* 1. Job Details */}
                    <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-bold">1</span>
                            Job Details
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Job Name */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Name <span className="text-red-500">*</span></label>
                                <input
                                    type="text"
                                    value={jobName}
                                    onChange={(e) => setJobName(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    placeholder="e.g. Alzheimer_EUR_001"
                                />
                            </div>
                            {/* Email */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email Address <span className="text-red-500">*</span></label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    placeholder="For results notification"
                                />
                            </div>
                            {/* Job Type */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Type</label>
                                <div className="px-4 py-2 rounded-lg border border-gray-200 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 text-sm text-gray-500">
                                    Single Trait
                                </div>
                            </div>
                            {/* Trait Name */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Name <span className="text-red-500">*</span></label>
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

                    {/* 2. Data Source */}
                    <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-bold">2</span>
                            Data Source
                        </h3>
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <button
                                    onClick={() => setDataSourceType("public")}
                                    className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden ${dataSourceType === 'public' ? 'border-blue-500 ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                                >
                                    <div className="font-bold text-base mb-1 text-gray-900 dark:text-white">Query Data</div>
                                    <div className="text-sm text-gray-500">Query Public GWAS Catalog or FinnGen</div>
                                </button>
                                <button
                                    onClick={() => setDataSourceType("upload")}
                                    className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden ${dataSourceType === 'upload' ? 'border-blue-500 ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                                >
                                    <div className="font-bold text-base mb-1 text-gray-900 dark:text-white">Upload Data</div>
                                    <div className="text-sm text-gray-500">Use your own GWAS summary statistics file</div>
                                </button>
                            </div>

                            {dataSourceType === 'public' ? (
                                <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                                    {/* GWAS Search Button / Selected Entry Display */}
                                    {selectedGwasEntry ? (
                                        <div className="p-5 rounded-2xl border border-blue-200 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-800">
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${selectedGwasEntry.database === 'finngen'
                                                            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                                                            : 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                                                            }`}>
                                                            {selectedGwasEntry.database === 'finngen' ? 'FinnGen' : 'GWAS Catalog'}
                                                        </span>
                                                        <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
                                                            {selectedGwasEntry.id}
                                                        </span>
                                                    </div>
                                                    <h4 className="text-base font-semibold text-gray-900 dark:text-white line-clamp-2">
                                                        {selectedGwasEntry.trait}
                                                    </h4>
                                                    {(selectedGwasEntry.nCases || selectedGwasEntry.sampleInfo) && (
                                                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-1">
                                                            {selectedGwasEntry.database === 'finngen'
                                                                ? `${selectedGwasEntry.nCases?.toLocaleString()} cases, ${selectedGwasEntry.nControls?.toLocaleString()} controls`
                                                                : selectedGwasEntry.sampleInfo}
                                                        </p>
                                                    )}
                                                    {/* Show Date and PubMed for GWAS Catalog */}
                                                    {selectedGwasEntry.database === 'gwas_catalog' && (selectedGwasEntry.date || selectedGwasEntry.pubmedId) && (
                                                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-400 dark:text-gray-500">
                                                            {selectedGwasEntry.date && (
                                                                <span>Date: {selectedGwasEntry.date}</span>
                                                            )}
                                                            {selectedGwasEntry.pubmedId && (
                                                                <span>PMID: {selectedGwasEntry.pubmedId}</span>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="flex items-center gap-2 shrink-0">
                                                    <a
                                                        href={selectedGwasEntry.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                                                        title="View in database"
                                                    >
                                                        <ExternalLink className="w-4 h-4" />
                                                    </a>
                                                    <button
                                                        onClick={() => setIsGwasSearchOpen(true)}
                                                        className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                                                    >
                                                        Change
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => setIsGwasSearchOpen(true)}
                                            className="w-full p-5 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all flex items-center gap-4 group"
                                        >
                                            <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors shrink-0">
                                                <Search className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                            </div>
                                            <div className="text-left flex-1">
                                                <div className="text-base font-semibold text-gray-900 dark:text-white">Search GWAS Database</div>
                                                <div className="text-sm text-gray-500 mt-0.5">Browse GWAS Catalog and FinnGen studies</div>
                                            </div>
                                            <ChevronRight className="w-6 h-6 text-gray-400 group-hover:text-blue-500 transition-colors" />
                                        </button>
                                    )}
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

                            {/* Ancestry Selection - Moved here */}
                            <div className="space-y-3 pt-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ancestry</label>
                                <div className="flex flex-wrap gap-2">
                                    {selectedGwasEntry?.database === 'finngen' && dataSourceType === 'public' ? (
                                        <button
                                            className="px-5 py-2.5 rounded-lg text-sm font-medium border border-blue-600 bg-blue-600 text-white shadow-md cursor-not-allowed opacity-80"
                                        >
                                            European (EUR)
                                        </button>
                                    ) : (
                                        ['EUR', 'AFR', 'EAS', 'SAS', 'AMR'].map(anc => (
                                            <button
                                                key={anc}
                                                onClick={() => setAncestry(anc)}
                                                className={`px-5 py-2.5 rounded-lg text-sm font-medium border transition-all ${ancestry === anc
                                                    ? 'bg-blue-600 border-blue-600 text-white shadow-md'
                                                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800'
                                                    }`}
                                            >
                                                {anc === 'AFR' ? 'African (AFR)' :
                                                    anc === 'AMR' ? 'Admixed American (AMR)' :
                                                        anc === 'EAS' ? 'East Asian (EAS)' :
                                                            anc === 'SAS' ? 'South Asian (SAS)' :
                                                                'European (EUR)'}
                                            </button>
                                        ))
                                    )}
                                </div>
                            </div>


                            {/* Extra Metadata */}
                            <div className="grid grid-cols-1 gap-6 pt-2">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-3">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Type</label>
                                        <div className="flex items-center gap-6 p-1">
                                            <label className="flex items-center gap-2 cursor-pointer">
                                                <input
                                                    type="radio"
                                                    name="traitType"
                                                    value="Case-Control"
                                                    checked={traitType === "Case-Control"}
                                                    onChange={() => setTraitType("Case-Control")}
                                                    className="w-5 h-5 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <span className="text-sm text-gray-700 dark:text-gray-300">Binary</span>
                                            </label>
                                            <label className="flex items-center gap-2 cursor-pointer">
                                                <input
                                                    type="radio"
                                                    name="traitType"
                                                    value="Continuous"
                                                    checked={traitType === "Continuous"}
                                                    onChange={() => setTraitType("Continuous")}
                                                    className="w-5 h-5 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <span className="text-sm text-gray-700 dark:text-gray-300">Continuous</span>
                                            </label>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sample Size</label>

                                        {traitType === 'Case-Control' ? (
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-4">
                                                    <label className="flex items-center gap-2 cursor-pointer">
                                                        <input
                                                            type="radio"
                                                            name="binarySampleSizeType"
                                                            value="nCaseControl"
                                                            checked={binarySampleSizeType === "nCaseControl"}
                                                            onChange={() => setBinarySampleSizeType("nCaseControl")}
                                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                        />
                                                        <span className="text-sm text-gray-700 dark:text-gray-300">Ncase & Ncontrol</span>
                                                    </label>
                                                    <label className="flex items-center gap-2 cursor-pointer">
                                                        <input
                                                            type="radio"
                                                            name="binarySampleSizeType"
                                                            value="nEff"
                                                            checked={binarySampleSizeType === "nEff"}
                                                            onChange={() => setBinarySampleSizeType("nEff")}
                                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                        />
                                                        <span className="text-sm text-gray-700 dark:text-gray-300">Neff</span>
                                                    </label>
                                                </div>

                                                {binarySampleSizeType === 'nCaseControl' ? (
                                                    <div className="grid grid-cols-2 gap-3">
                                                        <input
                                                            type="number"
                                                            value={nCase}
                                                            onChange={(e) => setNCase(e.target.value === '' ? '' : Number(e.target.value))}
                                                            placeholder="N Case"
                                                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                                        />
                                                        <input
                                                            type="number"
                                                            value={nControl}
                                                            onChange={(e) => setNControl(e.target.value === '' ? '' : Number(e.target.value))}
                                                            placeholder="N Control"
                                                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                                        />
                                                    </div>
                                                ) : (
                                                    <input
                                                        type="number"
                                                        value={sampleSize}
                                                        onChange={(e) => setSampleSize(e.target.value === '' ? '' : Number(e.target.value))}
                                                        placeholder="Neff"
                                                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                                    />
                                                )}
                                            </div>
                                        ) : (
                                            <input
                                                type="number"
                                                value={sampleSize}
                                                onChange={(e) => setSampleSize(e.target.value === '' ? '' : Number(e.target.value))}
                                                placeholder="N"
                                                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                            />
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* 3. Methodology */}
                    <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-bold">3</span>
                            Methodology
                        </h3>
                        <div className="space-y-6">
                            {/* Two Category Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                                {/* Pseudo-Training (Recommended) */}
                                <div
                                    className={`p-5 rounded-2xl border-2 transition-all cursor-pointer ${methodologyCategory === 'pseudo-training'
                                        ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20'
                                        : methodologyCategory === 'tuning-free'
                                            ? 'border-gray-200 dark:border-gray-700 opacity-40 cursor-not-allowed'
                                            : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                                        }`}
                                    onClick={() => {
                                        setMethodologyCategory('pseudo-training');
                                        if (methodologyCategory !== 'pseudo-training') {
                                            setMethods(['LDpred2-pseudo']);
                                            setEnsemble(false);
                                        }
                                    }}
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${methodologyCategory === 'pseudo-training'
                                            ? 'border-blue-500 bg-blue-500'
                                            : 'border-gray-300 dark:border-gray-600'
                                            }`}>
                                            {methodologyCategory === 'pseudo-training' && (
                                                <div className="w-2 h-2 bg-white rounded-full" />
                                            )}
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-gray-900 dark:text-white">Pseudo-Training</h4>
                                            <span className="text-xs text-green-600 dark:text-green-400 font-medium">Recommended</span>
                                        </div>
                                    </div>
                                    <p className="text-xs text-gray-500 mb-4">Methods that utilize pseudo-validation for optimal parameter tuning.</p>

                                    {/* Methods in this category */}
                                    <div className={`space-y-2 ${methodologyCategory !== 'pseudo-training' ? 'pointer-events-none' : ''}`}>
                                        {[
                                            { id: 'LDpred2-pseudo', tooltip: 'The pseudo-training version of LDpred2, a Bayesian approach that constructs PRS by leveraging information from GWAS summary statistics and LD inferred based on external reference genotype data assuming a spike-and-slab prior on SNP effect sizes.' },
                                            { id: 'lassosum2-pseudo', tooltip: 'The pseudo-training version of Lassosum2, a method for constructing PGS using summary statistics and a reference panel under a penalized regression framework.' },
                                            { id: 'C+T-pseudo', tooltip: 'The pseudo-training version of C + T, a model-free method that first constructs a series of PRSs with independent (selected by LD clumping) and significant SNPs based on varying p-value thresholds and then selects the best performing PRS on the tuning dataset.' }
                                        ].map(method => (
                                            <label
                                                key={method.id}
                                                className={`flex items-center gap-3 px-3 py-2 rounded-lg border transition-all ${methods.includes(method.id)
                                                    ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/30'
                                                    : 'border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                                                    }`}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={methods.includes(method.id)}
                                                    onChange={() => methodologyCategory === 'pseudo-training' && toggleMethod(method.id)}
                                                    disabled={methodologyCategory !== 'pseudo-training'}
                                                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                                />
                                                <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">{method.id}</span>
                                                <div className="relative group/tooltip">
                                                    <HelpCircle className="w-4 h-4 text-gray-400 hover:text-blue-500 cursor-help" />
                                                    <div className="absolute z-50 bottom-full right-0 mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 pointer-events-none">
                                                        {method.tooltip}
                                                        <div className="absolute bottom-0 right-3 transform translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
                                                    </div>
                                                </div>
                                            </label>
                                        ))}
                                    </div>
                                </div>

                                {/* Tuning-Parameter-Free Methods */}
                                <div
                                    className={`p-5 rounded-2xl border-2 transition-all cursor-pointer ${methodologyCategory === 'tuning-free'
                                        ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20'
                                        : methodologyCategory === 'pseudo-training'
                                            ? 'border-gray-200 dark:border-gray-700 opacity-40 cursor-not-allowed'
                                            : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                                        }`}
                                    onClick={() => {
                                        setMethodologyCategory('tuning-free');
                                        if (methodologyCategory !== 'tuning-free') {
                                            setMethods(['LDpred2-auto']);
                                            setEnsemble(false);
                                        }
                                    }}
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${methodologyCategory === 'tuning-free'
                                            ? 'border-blue-500 bg-blue-500'
                                            : 'border-gray-300 dark:border-gray-600'
                                            }`}>
                                            {methodologyCategory === 'tuning-free' && (
                                                <div className="w-2 h-2 bg-white rounded-full" />
                                            )}
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-gray-900 dark:text-white">Tuning-Parameter-Free Methods</h4>
                                            <span className="text-xs text-gray-500">No validation required</span>
                                        </div>
                                    </div>
                                    <p className="text-xs text-gray-500 mb-4">Methods that automatically determine optimal parameters without tuning.</p>

                                    {/* Methods in this category */}
                                    <div className={`space-y-2 ${methodologyCategory !== 'tuning-free' ? 'pointer-events-none' : ''}`}>
                                        {[
                                            { id: 'LDpred2-auto', recommended: true, tooltip: 'LDpred2-auto is a fully Bayesian, tuning-parameter-free version approach that constructs PRS by leveraging information from GWAS summary statistics and LD inferred based on external reference genotype data assuming a spike-and-slab prior on SNP effect size distribution.' },
                                            { id: 'DBSLMM', recommended: false, tooltip: 'Deterministic Bayesian Sparse Linear Mixed Model (DBSLMM) is a fully Bayesian approach assuming a flexible modeling assumption on the effect size distribution to achieve robust and accurate prediction performance across a range of genetic architectures.' },
                                            { id: 'PRS-CS-auto', recommended: false, tooltip: 'PRS-CS-auto is a fully Bayesian approach that utilizes a continuous shrinkage prior on SNP effect sizes.' }
                                        ].map(method => (
                                            <label
                                                key={method.id}
                                                className={`flex items-center gap-3 px-3 py-2 rounded-lg border transition-all ${methods.includes(method.id)
                                                    ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/30'
                                                    : 'border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                                                    }`}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={methods.includes(method.id)}
                                                    onChange={() => methodologyCategory === 'tuning-free' && toggleMethod(method.id)}
                                                    disabled={methodologyCategory !== 'tuning-free'}
                                                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                                />
                                                <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">{method.id}</span>
                                                {method.recommended && (
                                                    <span className="text-[10px] px-1.5 py-0.5 bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400 rounded-full font-medium shrink-0">
                                                        Recommended
                                                    </span>
                                                )}
                                                <div className="relative group/tooltip">
                                                    <HelpCircle className="w-4 h-4 text-gray-400 hover:text-blue-500 cursor-help" />
                                                    <div className="absolute z-50 bottom-full right-0 mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 pointer-events-none">
                                                        {method.tooltip}
                                                        <div className="absolute bottom-0 right-3 transform translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
                                                    </div>
                                                </div>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Ensemble Learning Toggle - Only show for pseudo-training */}
                            {methodologyCategory === 'pseudo-training' && (
                                <div className={`flex flex-wrap items-center gap-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800 ${methods.length <= 1 ? 'opacity-50 cursor-not-allowed' : ''}`}>
                                    <label className={`flex items-center gap-3 shrink-0 ${methods.length <= 1 ? 'cursor-not-allowed' : 'cursor-pointer'}`}>
                                        <div
                                            className={`w-12 h-7 rounded-full p-1 transition-colors ${ensemble ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}
                                            onClick={() => methods.length > 1 && setEnsemble(!ensemble)}
                                        >
                                            <div className={`w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform ${ensemble ? 'translate-x-5' : ''}`} />
                                        </div>
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                                            {ensemble ? "Ensemble Learning On" : "Ensemble Learning Off"}
                                        </span>
                                    </label>
                                    <div className="h-5 w-px bg-gray-300 dark:bg-gray-700 hidden sm:block"></div>
                                    <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                                        <Info className="w-4 h-4 shrink-0" />
                                        <span>Note: If multiple methods are selected, we provide an option to train an ensemble PRS based on the selected methods.</span>
                                    </div>
                                </div>
                            )}
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
                            <div className="mt-6 space-y-8 animate-in fade-in slide-in-from-top-2 duration-300">

                                {/* C+T-pseudo */}
                                {methods.includes('C+T-pseudo') && (
                                    <div className="space-y-4 p-4 border border-gray-100 dark:border-gray-800 rounded-xl bg-gray-50/50 dark:bg-gray-800/30">
                                        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">C+T-pseudo</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">kb</label>
                                                <input type="number" value={kb} onChange={(e) => setKb(Number(e.target.value))} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">P-value threshold</label>
                                                <input type="text" value={pvalThr} onChange={(e) => setPvalThr(e.target.value)} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">R2</label>
                                                <input type="number" step="0.1" value={r2} onChange={(e) => setR2(Number(e.target.value))} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Lassosum2-pseudo */}
                                {methods.includes('Lassosum2-pseudo') && (
                                    <div className="space-y-4 p-4 border border-gray-100 dark:border-gray-800 rounded-xl bg-gray-50/50 dark:bg-gray-800/30">
                                        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Lassosum2-pseudo</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">delta</label>
                                                <input type="text" value={delta} onChange={(e) => setDelta(e.target.value)} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">nlambda</label>
                                                <input type="number" value={nlambda} onChange={(e) => setNlambda(Number(e.target.value))} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">lambda min ratio</label>
                                                <input type="number" step="0.01" value={lambdaMinRatio} onChange={(e) => setLambdaMinRatio(Number(e.target.value))} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* LDpred2-pseudo */}
                                {methods.includes('LDpred2-pseudo') && (
                                    <div className="space-y-4 p-4 border border-gray-100 dark:border-gray-800 rounded-xl bg-gray-50/50 dark:bg-gray-800/30">
                                        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">LDpred2-pseudo</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">alpha</label>
                                                <input type="text" value={alpha} onChange={(e) => setAlpha(e.target.value)} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">P-seq</label>
                                                <input type="text" value={pSeq} onChange={(e) => setPSeq(e.target.value)} className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 outline-none focus:border-blue-500" />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">Sparse</label>
                                                <div className="flex bg-gray-100 dark:bg-gray-800 p-1 rounded-xl w-fit border border-gray-200 dark:border-gray-700">
                                                    <button
                                                        type="button"
                                                        onClick={() => setSparse(true)}
                                                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 ${sparse
                                                            ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600 dark:text-blue-400'
                                                            : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                                                    >
                                                        TRUE
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => setSparse(false)}
                                                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 ${!sparse
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

                                {/* PRS-CS-auto */}
                                {methods.includes('PRS-CS-auto') && (
                                    <div className="space-y-4 p-4 border border-gray-100 dark:border-gray-800 rounded-xl bg-gray-50/50 dark:bg-gray-800/30">
                                        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">PRS-CS-auto</h4>

                                        {/* Mode Toggle */}
                                        <div className="space-y-3">
                                            <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">Mode</label>
                                            <div className="flex items-center gap-4">
                                                <span className={`text-sm ${prscsPhiMode === 'fullyBayesian' ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-400'}`}>
                                                    fully Bayesian
                                                </span>
                                                <div
                                                    className={`w-14 h-8 rounded-full p-1 cursor-pointer transition-colors ${prscsPhiMode === 'fixedPhi' ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                                                        }`}
                                                    onClick={() => setPrscsPhiMode(prscsPhiMode === 'fullyBayesian' ? 'fixedPhi' : 'fullyBayesian')}
                                                >
                                                    <div className={`w-6 h-6 bg-white rounded-full shadow-sm transform transition-transform ${prscsPhiMode === 'fixedPhi' ? 'translate-x-6' : ''
                                                        }`} />
                                                </div>
                                                <span className={`text-sm ${prscsPhiMode === 'fixedPhi' ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-400'}`}>
                                                    fixed phi
                                                </span>
                                            </div>
                                        </div>

                                        {/* Phi Dropdown - Only shown when fixed phi is selected */}
                                        {prscsPhiMode === 'fixedPhi' && (
                                            <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-200">
                                                <label className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">phi</label>
                                                <select
                                                    value={prscsPhiValue}
                                                    onChange={(e) => setPrscsPhiValue(e.target.value)}
                                                    className="w-full md:w-48 px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                                                >
                                                    <option value="1e-2">1e-2</option>
                                                    <option value="1e-4">1e-4</option>
                                                    <option value="1e-6">1e-6</option>
                                                    <option value="1">1</option>
                                                </select>
                                            </div>
                                        )}
                                    </div>
                                )}

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
                            disabled={!isFormValid || isSubmitting}
                            className={`px-8 py-2.5 text-sm font-bold rounded-xl shadow-lg transition-all duration-200 flex items-center gap-2 ${isFormValid && !isSubmitting
                                ? 'text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl hover:-translate-y-0.5'
                                : 'text-gray-400 bg-gray-200 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed'
                                }`}
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Submitting...
                                </>
                            ) : (
                                'Start Training Job'
                            )}
                        </button>
                    </div>

                </div>
            </div>

            {/* GWAS Search Modal */}
            <GWASSearchModal
                isOpen={isGwasSearchOpen}
                onClose={() => setIsGwasSearchOpen(false)}
                onSelect={async (entry) => {
                    setSelectedGwasEntry(entry);

                    // Auto-populate based on available data
                    if (entry.nCases && entry.nControls) {
                        // Clear case: Case-Control (Binary) with explicit case/control counts
                        setTraitType('Case-Control');
                        setBinarySampleSizeType('nCaseControl');
                        setNCase(entry.nCases);
                        setNControl(entry.nControls);
                    } else if (entry.nTotal) {
                        // Ambiguous: Could be Continuous OR Binary with Neff
                        // Use LLM Agent to classify
                        try {
                            const response = await fetch('http://localhost:8000/agent/classify_trait', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    trait_name: entry.trait,
                                    sample_info: entry.sampleInfo
                                })
                            });
                            const result = await response.json();

                            // Set ancestry from LLM classification
                            if (result.ancestry) {
                                setAncestry(result.ancestry);
                            }

                            if (result.trait_type === 'Binary') {
                                // Binary with Neff (effective sample size)
                                setTraitType('Case-Control');
                                setBinarySampleSizeType('nEff');
                                setSampleSize(entry.nTotal);
                            } else {
                                // Continuous trait
                                setTraitType('Continuous');
                                setSampleSize(entry.nTotal);
                            }
                        } catch (error) {
                            console.error('Failed to classify trait:', error);
                            // Fallback: Set as Continuous but leave for manual adjustment
                            setTraitType('Continuous');
                            setSampleSize(entry.nTotal);
                        }
                    }
                    // If neither available, leave fields for manual input
                }}
                initialSelection={selectedGwasEntry}
            />
        </>
    );
}
