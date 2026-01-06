"use client";

import React, { useState } from "react";
import { Search, X, ChevronDown, ChevronUp, Plus, Trash2, HelpCircle, Info, Lock, ChevronRight, Upload, ExternalLink, Loader2 } from "lucide-react";
import GWASSearchModal, { GWASEntry } from "./GWASSearchModal";

// Type Definitions
export interface MultiAncestryTrainingConfig {
    jobName: string;
    email: string;
    jobType: "multi";
    trait: string;
    dataSources: Array<{
        ancestry: string;
        dataSourceType: "public" | "upload";
        database?: string;
        gwasId?: string;
        traitType?: string;
        sampleSize?: number;
        nCases?: number;
        nControls?: number;
        nEff?: number;
        uploadedFileName?: string;
    }>;
    method: string;
    advanced?: {
        nlambda?: string;
        ndelta?: string;
        lambda_min_ratio?: string;
        Ll?: string;
        Lc?: string;
    };
}

interface MultiAncestryTrainingFormProps {
    onSubmit: (config: MultiAncestryTrainingConfig) => void;
    onCancel?: () => void;
    isSubmitting?: boolean;  // New: loading state for submit button
}

const ANCESTRY_OPTIONS = [
    { code: "EUR", label: "European (EUR)" },
    { code: "AFR", label: "African (AFR)" },
    { code: "EAS", label: "East Asian (EAS)" },
    { code: "SAS", label: "South Asian (SAS)" },
    { code: "AMR", label: "Admixed American (AMR)" },
];

interface DataSourceState {
    id: string;
    ancestry: string;
    dataSourceType: "public" | "upload";
    database: string;
    selectedGwasEntry: GWASEntry | null;
    uploadedFile: File | null;
    traitType: "Case-Control" | "Continuous";
    binarySampleSizeType: "nCaseControl" | "nEff";
    nCase: number | "";
    nControl: number | "";
    sampleSize: number | "";
}

// Helper to infer ancestry from sample info text locally
const inferAncestryFromText = (text: string): string | null => {
    if (!text) return null;
    const t = text.toLowerCase();
    if (t.includes('european')) return 'EUR';
    if (t.includes('east asian')) return 'EAS';
    if (t.includes('south asian')) return 'SAS';
    if (t.includes('african') && !t.includes('european') && !t.includes('asian')) return 'AFR'; // Basic safeguard
    if (t.includes('hispanic') || t.includes('latino') || t.includes('admixed american')) return 'AMR';
    return null;
};

export default function MultiAncestryTrainingForm({ onSubmit, onCancel, isSubmitting = false }: MultiAncestryTrainingFormProps) {
    // Job Details
    const [jobName, setJobName] = useState("");
    const [email, setEmail] = useState("");
    const [trait, setTrait] = useState("");

    // Data Sources (2-5)
    // Initial state: 2 empty sources, no ancestry selected yet
    const [dataSources, setDataSources] = useState<DataSourceState[]>([
        { id: crypto.randomUUID(), ancestry: "", dataSourceType: "public", database: "gwas", selectedGwasEntry: null, uploadedFile: null, traitType: "Case-Control", binarySampleSizeType: "nCaseControl", nCase: "", nControl: "", sampleSize: "" },
        { id: crypto.randomUUID(), ancestry: "", dataSourceType: "public", database: "gwas", selectedGwasEntry: null, uploadedFile: null, traitType: "Case-Control", binarySampleSizeType: "nCaseControl", nCase: "", nControl: "", sampleSize: "" },
    ]);

    // Advanced Options
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [nlambda, setNlambda] = useState("30");
    const [ndelta, setNdelta] = useState("5");
    const [lambdaMinRatio, setLambdaMinRatio] = useState("0.01");
    const [Ll, setLl] = useState("5");
    const [Lc, setLc] = useState("5");

    // GWAS Search Modal State
    const [activeSearchIndex, setActiveSearchIndex] = useState<number | null>(null);

    // Get used ancestries (to prevent duplicate selection)
    const usedAncestries = dataSources.map(ds => ds.ancestry).filter(a => a !== "");

    // Add new data source
    const addDataSource = () => {
        if (dataSources.length >= 5) return;
        setDataSources([...dataSources, {
            id: crypto.randomUUID(),
            ancestry: "", // Start empty
            dataSourceType: "public",
            database: "gwas",
            selectedGwasEntry: null,
            uploadedFile: null,
            traitType: "Case-Control",
            binarySampleSizeType: "nCaseControl",
            nCase: "",
            nControl: "",
            sampleSize: ""
        }]);
    };

    // Remove data source
    const removeDataSource = (id: string) => {
        if (dataSources.length <= 2) return;
        setDataSources(dataSources.filter(ds => ds.id !== id));
    };

    // Update data source field
    const updateDataSource = (index: number, field: keyof DataSourceState, value: any) => {
        const updated = [...dataSources];
        (updated[index] as any)[field] = value;

        // Reset related fields when changing data source type
        if (field === 'dataSourceType') {
            updated[index].selectedGwasEntry = null;
            updated[index].uploadedFile = null;
        }
        // Reset sample size inputs when changing trait type
        if (field === 'traitType') {
            updated[index].nCase = "";
            updated[index].nControl = "";
            updated[index].sampleSize = "";
        }

        setDataSources(updated);
    };

    // Handle GWAS selection for a specific data source
    const handleGwasSelect = async (entry: GWASEntry) => {
        if (activeSearchIndex === null) return;

        const updated = [...dataSources];
        const targetIndex = activeSearchIndex;
        // Clone the target data source object
        const ds = { ...updated[targetIndex] };

        // Helper to check if ancestry already exists in OTHER data sources
        const isAncestryTaken = (anc: string) => updated.some((d, i) => i !== targetIndex && d.ancestry === anc);

        ds.selectedGwasEntry = entry;
        ds.database = entry.database === 'finngen' ? 'finngen' : 'gwas';

        // Auto-fill trait name from first selection if empty
        if (!trait && entry.trait) {
            setTrait(entry.trait);
        }

        // --- Logic to Determine Ancestry & Trait Type (Optimized to match Single) ---

        // 1. Ancestry Inference (Database specific or Local Regex or API)
        let determinedAncestry: string | null = null;

        if (entry.database === 'finngen') {
            determinedAncestry = "EUR";
        } else if (entry.nCases && entry.nControls) {
            // fast path: try local inference
            determinedAncestry = inferAncestryFromText(entry.sampleInfo || "");
        }
        // Note: For nTotal case, we rely on API below to set determinedAncestry

        // 2. Trait Type & Sample Size Logic (Priority: Explicit > API > Fallback)
        if (entry.nCases && entry.nControls) { // Matches Single Logic: No API Call here
            ds.traitType = "Case-Control";
            ds.binarySampleSizeType = "nCaseControl";
            ds.nCase = entry.nCases;
            ds.nControl = entry.nControls;

            // Apply locally inferred ancestry if available
            if (determinedAncestry) {
                if (isAncestryTaken(determinedAncestry)) {
                    throw new Error(`Selection Failed: The ancestry '${determinedAncestry}' is already selected in another data source.`);
                }
                ds.ancestry = determinedAncestry;
            }
        } else if (entry.nTotal) {
            // Ambiguous case: Call API (Matches Single Logic)
            try {
                const response = await fetch('http://localhost:8000/agent/classify_trait', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        trait_name: entry.trait,
                        sample_info: entry.sampleInfo || ""
                    })
                });

                if (!response.ok) throw new Error("Trait classification failed");
                const result = await response.json();

                // Ancestry from API
                if (result.ancestry) {
                    const code = result.ancestry;
                    if (ANCESTRY_OPTIONS.some(a => a.code === code)) {
                        if (isAncestryTaken(code)) {
                            throw new Error(`Selection Failed: The ancestry '${code}' inferred for this study is already selected.`);
                        }
                        ds.ancestry = code;
                    }
                }

                if (result.trait_type === 'Binary') {
                    ds.traitType = "Case-Control";
                    ds.binarySampleSizeType = "nEff";
                    ds.sampleSize = entry.nTotal;
                } else {
                    ds.traitType = "Continuous";
                    ds.sampleSize = entry.nTotal;
                }
            } catch (e: any) {
                if (e.message && e.message.includes("Selection Failed")) {
                    throw e;
                }
                // Fallback
                ds.traitType = "Continuous";
                ds.sampleSize = entry.nTotal;
            }
        } else {
            // Fallback (matches Single)
            ds.traitType = "Continuous";
            // No sample size
        }

        updated[targetIndex] = ds;
        setDataSources(updated);
        setActiveSearchIndex(null);
    };

    // Calculate sample size for a data source
    const getEffectiveSampleSize = (ds: DataSourceState): number => {
        if (ds.traitType === "Case-Control") {
            if (ds.binarySampleSizeType === "nCaseControl") {
                return (Number(ds.nCase) || 0) + (Number(ds.nControl) || 0);
            } else {
                return Number(ds.sampleSize) || 0;
            }
        }
        return Number(ds.sampleSize) || 0;
    };

    // Form validation
    const isValid = () => {
        if (!jobName.trim() || !email.trim() || !trait.trim()) return false;
        // Check for duplicate ancestries or empty ancestries
        const ancestries = dataSources.map(ds => ds.ancestry);
        if (ancestries.some(a => a === "")) return false; // All must have ancestry selected
        if (new Set(ancestries).size !== ancestries.length) return false; // Must be unique

        for (const ds of dataSources) {
            if (ds.dataSourceType === "public" && !ds.selectedGwasEntry) return false;
            if (ds.dataSourceType === "upload" && !ds.uploadedFile) return false;
        }
        return true;
    };

    // Submit handler
    const handleSubmit = () => {
        if (!isValid()) return;

        const config: MultiAncestryTrainingConfig = {
            jobName,
            email,
            jobType: "multi",
            trait,
            dataSources: dataSources.map(ds => ({
                ancestry: ds.ancestry,
                dataSourceType: ds.dataSourceType,
                database: ds.database,
                gwasId: ds.selectedGwasEntry?.id,
                traitType: ds.traitType === "Case-Control" ? "Binary" : "Continuous",
                sampleSize: getEffectiveSampleSize(ds),
                nCases: ds.traitType === "Case-Control" && ds.binarySampleSizeType === "nCaseControl" ? Number(ds.nCase) || undefined : undefined,
                nControls: ds.traitType === "Case-Control" && ds.binarySampleSizeType === "nCaseControl" ? Number(ds.nControl) || undefined : undefined,
                nEff: ds.traitType === "Case-Control" && ds.binarySampleSizeType === "nEff" ? Number(ds.sampleSize) || undefined : undefined,
                uploadedFileName: ds.uploadedFile?.name,
            })),
            method: "PROSPER-pseudo",
            advanced: showAdvanced ? {
                nlambda,
                ndelta,
                lambda_min_ratio: lambdaMinRatio,
                Ll,
                Lc
            } : undefined
        };
        onSubmit(config);
    };

    return (
        <>
            <div className="w-full max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
                <div className="space-y-10">

                    {/* 1. Job Details */}
                    <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm font-bold">1</span>
                            Job Details
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Name <span className="text-red-500">*</span></label>
                                <input
                                    type="text"
                                    value={jobName}
                                    onChange={(e) => setJobName(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                    placeholder="e.g. Alzheimer_MultiAncestry_001"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email Address <span className="text-red-500">*</span></label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                    placeholder="For results notification"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Type</label>
                                <div className="px-4 py-2 rounded-lg border border-gray-200 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 text-sm text-gray-500">
                                    Multi-Ancestry
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Name <span className="text-red-500">*</span></label>
                                <input
                                    type="text"
                                    value={trait}
                                    onChange={(e) => setTrait(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                    placeholder="e.g. Alzheimer's Disease"
                                />
                            </div>
                        </div>
                    </section>

                    {/* 2. Data Sources (Multi-Ancestry) */}
                    <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm font-bold">2</span>
                            Data Sources
                            <span className="text-xs font-normal text-gray-500 ml-2 px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-full">{dataSources.length}/5</span>
                        </h3>

                        {/* Note - EXACT TEXT, smaller font */}
                        <div className="flex items-start gap-2 px-3 py-2 mb-5 bg-purple-50/70 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800/50 rounded-lg">
                            <Info className="w-3.5 h-3.5 text-purple-500 shrink-0 mt-0.5" />
                            <p className="text-[11px] text-purple-700 dark:text-purple-300 leading-relaxed">
                                For multi-ancestry analysis on 2 ≤ K ≤ 5 distinct ancestries, we require ancestry-stratified GWAS summary statistics from the K ancestry groups. We support analyses on any subset of the five super populations with ancestry-stratified GWAS summary statistics from the corresponding ancestry populations. For analyses on more complex ancestry populations, please <a href="mailto:support@pennprs.org" className="underline hover:text-purple-600">contact us</a>.
                            </p>
                        </div>

                        {/* Ancestry Cards */}
                        <div className="space-y-5">
                            {dataSources.map((ds, index) => (
                                <div key={ds.id} className="p-5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30">
                                    {/* Header */}
                                    <div className="flex items-center justify-between mb-5">
                                        <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                                            Ancestry {index + 1}
                                        </h4>
                                        {dataSources.length > 2 && (
                                            <button
                                                onClick={() => removeDataSource(ds.id)}
                                                className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                                                title="Remove this ancestry"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>

                                    {/* Query Data / Upload Data Toggle */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
                                        <button
                                            onClick={() => updateDataSource(index, 'dataSourceType', 'public')}
                                            className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden ${ds.dataSourceType === 'public'
                                                ? 'border-purple-500 ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/20'
                                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                                                }`}
                                        >
                                            <div className="font-bold text-base mb-1 text-gray-900 dark:text-white">Query Data</div>
                                            <div className="text-sm text-gray-500">Query Public GWAS Catalog or FinnGen</div>
                                        </button>
                                        <button
                                            onClick={() => updateDataSource(index, 'dataSourceType', 'upload')}
                                            className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden ${ds.dataSourceType === 'upload'
                                                ? 'border-purple-500 ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/20'
                                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                                                }`}
                                        >
                                            <div className="font-bold text-base mb-1 text-gray-900 dark:text-white">Upload Data</div>
                                            <div className="text-sm text-gray-500">Use your own GWAS summary statistics file</div>
                                        </button>
                                    </div>

                                    {/* Search GWAS Database Button */}
                                    {ds.dataSourceType === "public" && (
                                        <div className="mb-5">
                                            {ds.selectedGwasEntry ? (
                                                <div className="p-5 rounded-2xl border border-blue-200 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-800">
                                                    <div className="flex items-start justify-between gap-3">
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <span className={`text-xs px-2 py-1 rounded-full font-medium ${ds.selectedGwasEntry.database === 'finngen'
                                                                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                                                                    : 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                                                                    }`}>
                                                                    {ds.selectedGwasEntry.database === 'finngen' ? 'FinnGen' : 'GWAS Catalog'}
                                                                </span>
                                                                <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
                                                                    {ds.selectedGwasEntry.id}
                                                                </span>
                                                            </div>
                                                            <h4 className="text-base font-semibold text-gray-900 dark:text-white line-clamp-2">
                                                                {ds.selectedGwasEntry.trait}
                                                            </h4>
                                                            {(ds.selectedGwasEntry.nCases || ds.selectedGwasEntry.sampleInfo) && (
                                                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-1">
                                                                    {ds.selectedGwasEntry.database === 'finngen'
                                                                        ? `${ds.selectedGwasEntry.nCases?.toLocaleString()} cases, ${ds.selectedGwasEntry.nControls?.toLocaleString()} controls`
                                                                        : ds.selectedGwasEntry.sampleInfo}
                                                                </p>
                                                            )}
                                                            {/* Show Date and PubMed for GWAS Catalog */}
                                                            {ds.selectedGwasEntry.database === 'gwas_catalog' && (ds.selectedGwasEntry.date || ds.selectedGwasEntry.pubmedId) && (
                                                                <div className="flex items-center gap-3 mt-1 text-xs text-gray-400 dark:text-gray-500">
                                                                    {ds.selectedGwasEntry.date && (
                                                                        <span>Date: {ds.selectedGwasEntry.date}</span>
                                                                    )}
                                                                    {ds.selectedGwasEntry.pubmedId && (
                                                                        <span>PMID: {ds.selectedGwasEntry.pubmedId}</span>
                                                                    )}
                                                                </div>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-2 shrink-0">
                                                            <a
                                                                href={ds.selectedGwasEntry.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                                                                title="View in database"
                                                            >
                                                                <ExternalLink className="w-4 h-4" />
                                                            </a>
                                                            <button
                                                                onClick={() => setActiveSearchIndex(index)}
                                                                className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                                                            >
                                                                Change
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => setActiveSearchIndex(index)}
                                                    className="w-full p-4 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500 transition-all flex items-center justify-between group"
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-10 h-10 rounded-full bg-purple-50 dark:bg-purple-900/30 flex items-center justify-center">
                                                            <Search className="w-5 h-5 text-purple-500" />
                                                        </div>
                                                        <div className="text-left">
                                                            <div className="font-semibold text-gray-900 dark:text-white">Search GWAS Database</div>
                                                            <div className="text-sm text-gray-500">Browse GWAS Catalog and FinnGen studies</div>
                                                        </div>
                                                    </div>
                                                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-purple-500 transition-colors" />
                                                </button>
                                            )}
                                        </div>
                                    )}

                                    {/* Upload File Area - SAME AS SINGLE */}
                                    {ds.dataSourceType === "upload" && (
                                        <div className="mb-5">
                                            {ds.uploadedFile ? (
                                                <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-2xl">
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-500 flex items-center justify-center">
                                                            <Upload className="w-5 h-5" />
                                                        </div>
                                                        <span className="text-sm font-medium text-purple-700 dark:text-purple-300 truncate">{ds.uploadedFile.name}</span>
                                                    </div>
                                                    <button
                                                        onClick={() => updateDataSource(index, 'uploadedFile', null)}
                                                        className="p-1.5 text-gray-400 hover:text-red-500"
                                                    >
                                                        <X className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            ) : (
                                                <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:border-purple-400 dark:hover:border-purple-700 transition-all group">
                                                    <input
                                                        type="file"
                                                        className="hidden"
                                                        id={`file-upload-${ds.id}`}
                                                        onChange={(e) => updateDataSource(index, 'uploadedFile', e.target.files?.[0] || null)}
                                                    />
                                                    <label htmlFor={`file-upload-${ds.id}`} className="cursor-pointer w-full h-full flex flex-col items-center">
                                                        <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-500 dark:text-blue-400 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                                            <Upload className="w-6 h-6" />
                                                        </div>
                                                        <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">Click to select file</p>
                                                        <p className="text-xs text-gray-500 mt-1">Supported formats: .txt, .tsv, .gz (Max 500MB)</p>
                                                    </label>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Ancestry Selection */}
                                    <div className="space-y-3 mb-5">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ancestry</label>
                                        <div className="flex flex-wrap gap-2 w-full">
                                            {ANCESTRY_OPTIONS.map(opt => {
                                                const isUsedElsewhere = usedAncestries.includes(opt.code) && ds.ancestry !== opt.code;
                                                const isSelected = ds.ancestry === opt.code;

                                                // Shorten label for better fit if needed, but flex-wrap handles it.
                                                // Trying to make them fit in one line: reduced padding, smaller font? 
                                                // Single uses: px-5 py-2.5 text-sm.
                                                // Here we might need: px-3 py-2 text-xs or sm.
                                                return (
                                                    <button
                                                        key={opt.code}
                                                        onClick={() => !isUsedElsewhere && updateDataSource(index, 'ancestry', opt.code)}
                                                        disabled={isUsedElsewhere}
                                                        title={isUsedElsewhere ? "Already selected in another data source" : ""}
                                                        className={`flex-1 min-w-[120px] px-3 py-2 rounded-lg text-xs font-medium border transition-all text-center whitespace-nowrap ${isSelected
                                                            ? 'bg-purple-600 border-purple-600 text-white shadow-md'
                                                            : isUsedElsewhere
                                                                ? 'bg-gray-100 border-gray-200 text-gray-300 cursor-not-allowed dark:bg-gray-800 dark:border-gray-700 dark:text-gray-600'
                                                                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800'
                                                            }`}
                                                    >
                                                        {opt.label}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                        {/* Error message if user tries to select same ancestry */}
                                        {/* Since buttons are disabled, user can't select. Added title for tooltip. */}
                                    </div>

                                    {/* Trait Type & Sample Size - SAME AS SINGLE */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {/* Trait Type */}
                                        <div className="space-y-3">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Trait Type</label>
                                            <div className="flex items-center gap-6 p-1">
                                                <label className="flex items-center gap-2 cursor-pointer">
                                                    <input
                                                        type="radio"
                                                        name={`traitType-${ds.id}`}
                                                        checked={ds.traitType === "Case-Control"}
                                                        onChange={() => updateDataSource(index, 'traitType', 'Case-Control')}
                                                        className="w-5 h-5 text-purple-600 focus:ring-purple-500 border-gray-300"
                                                    />
                                                    <span className="text-sm text-gray-700 dark:text-gray-300">Binary</span>
                                                </label>
                                                <label className="flex items-center gap-2 cursor-pointer">
                                                    <input
                                                        type="radio"
                                                        name={`traitType-${ds.id}`}
                                                        checked={ds.traitType === "Continuous"}
                                                        onChange={() => updateDataSource(index, 'traitType', 'Continuous')}
                                                        className="w-5 h-5 text-purple-600 focus:ring-purple-500 border-gray-300"
                                                    />
                                                    <span className="text-sm text-gray-700 dark:text-gray-300">Continuous</span>
                                                </label>
                                            </div>
                                        </div>

                                        {/* Sample Size */}
                                        <div className="space-y-3">
                                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sample Size</label>
                                            {ds.traitType === 'Case-Control' ? (
                                                <div className="space-y-3">
                                                    <div className="flex items-center gap-4">
                                                        <label className="flex items-center gap-2 cursor-pointer">
                                                            <input
                                                                type="radio"
                                                                name={`binarySampleSizeType-${ds.id}`}
                                                                checked={ds.binarySampleSizeType === "nCaseControl"}
                                                                onChange={() => updateDataSource(index, 'binarySampleSizeType', 'nCaseControl')}
                                                                className="w-4 h-4 text-purple-600 focus:ring-purple-500 border-gray-300"
                                                            />
                                                            <span className="text-sm text-gray-700 dark:text-gray-300">Ncase & Ncontrol</span>
                                                        </label>
                                                        <label className="flex items-center gap-2 cursor-pointer">
                                                            <input
                                                                type="radio"
                                                                name={`binarySampleSizeType-${ds.id}`}
                                                                checked={ds.binarySampleSizeType === "nEff"}
                                                                onChange={() => updateDataSource(index, 'binarySampleSizeType', 'nEff')}
                                                                className="w-4 h-4 text-purple-600 focus:ring-purple-500 border-gray-300"
                                                            />
                                                            <span className="text-sm text-gray-700 dark:text-gray-300">Neff</span>
                                                        </label>
                                                    </div>
                                                    {ds.binarySampleSizeType === 'nCaseControl' ? (
                                                        <div className="grid grid-cols-2 gap-3">
                                                            <input
                                                                type="number"
                                                                value={ds.nCase}
                                                                onChange={(e) => updateDataSource(index, 'nCase', e.target.value === '' ? '' : Number(e.target.value))}
                                                                placeholder="N Case"
                                                                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                                            />
                                                            <input
                                                                type="number"
                                                                value={ds.nControl}
                                                                onChange={(e) => updateDataSource(index, 'nControl', e.target.value === '' ? '' : Number(e.target.value))}
                                                                placeholder="N Control"
                                                                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                                            />
                                                        </div>
                                                    ) : (
                                                        <input
                                                            type="number"
                                                            value={ds.sampleSize}
                                                            onChange={(e) => updateDataSource(index, 'sampleSize', e.target.value === '' ? '' : Number(e.target.value))}
                                                            placeholder="Neff"
                                                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                                        />
                                                    )}
                                                </div>
                                            ) : (
                                                <input
                                                    type="number"
                                                    value={ds.sampleSize}
                                                    onChange={(e) => updateDataSource(index, 'sampleSize', e.target.value === '' ? '' : Number(e.target.value))}
                                                    placeholder="N"
                                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                                />
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Add Ancestry Button */}
                        {dataSources.length < 5 && (
                            <button
                                onClick={addDataSource}
                                className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2.5 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-400 hover:border-purple-400 hover:text-purple-600 dark:hover:border-purple-500 dark:hover:text-purple-400 transition-all"
                            >
                                <Plus className="w-4 h-4" />
                                Add Ancestry ({5 - dataSources.length} remaining)
                            </button>
                        )}
                    </section>

                    {/* 3. Methodology - Fixed PROSPER-pseudo */}
                    <section className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-sm font-bold">3</span>
                            Methodology
                        </h3>

                        {/* Locked Method Display */}
                        <div className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-5 h-5 rounded bg-purple-500 flex items-center justify-center">
                                        <Lock className="w-3 h-3 text-white" />
                                    </div>
                                    <span className="font-semibold text-gray-900 dark:text-white">PROSPER-pseudo</span>
                                    <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400 rounded font-medium">
                                        Required
                                    </span>
                                </div>
                                <div className="relative group/tooltip">
                                    <HelpCircle className="w-5 h-5 text-gray-400 hover:text-purple-500 cursor-help" />
                                    <div className="absolute z-50 bottom-full right-0 mb-2 w-80 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 pointer-events-none">
                                        The pseudo-training version of PROSPER, an ensemble penalized regression method for multi-ancestry PRS development using a combination of L1 and L2 penalty functions and an ensemble step to combine PRS generated across different penalty parameters.
                                        <div className="absolute bottom-0 right-3 transform translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
                                    </div>
                                </div>
                            </div>
                            <p className="text-xs text-gray-500 mt-2 ml-8">
                                Multi-ancestry analysis currently only supports PROSPER-pseudo method.
                            </p>
                        </div>
                    </section>

                    {/* Advanced Options Toggle */}
                    <div className="pt-2 pb-8">
                        <button
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="text-sm font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 flex items-center gap-2 transition-colors"
                        >
                            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            {showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
                        </button>

                        {showAdvanced && (
                            <div className="mt-6 p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 animate-in fade-in slide-in-from-top-2 duration-300">
                                <h4 className="text-base font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                                    <span className="text-purple-600">⚙️</span>
                                    PROSPER-pseudo Parameters
                                </h4>
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">nlambda</label>
                                        <input
                                            type="text"
                                            value={nlambda}
                                            onChange={(e) => setNlambda(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">ndelta</label>
                                        <input
                                            type="text"
                                            value={ndelta}
                                            onChange={(e) => setNdelta(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">lambda min ratio</label>
                                        <input
                                            type="text"
                                            value={lambdaMinRatio}
                                            onChange={(e) => setLambdaMinRatio(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ll</label>
                                        <input
                                            type="text"
                                            value={Ll}
                                            onChange={(e) => setLl(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Lc</label>
                                        <input
                                            type="text"
                                            value={Lc}
                                            onChange={(e) => setLc(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm"
                                        />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="flex items-center justify-end gap-4 pt-6 border-t border-gray-100 dark:border-gray-800">
                    <button
                        onClick={onCancel}
                        className="px-6 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={!isValid() || isSubmitting}
                        className={`px-8 py-2.5 text-sm font-semibold rounded-xl transition-all shadow-lg flex items-center gap-2 ${isValid() && !isSubmitting
                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 hover:shadow-xl'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                            }`}
                    >
                        {isSubmitting ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Submitting...
                            </>
                        ) : (
                            'Submit Training Job'
                        )}
                    </button>
                </div>
            </div>

            {/* GWAS Search Modal */}
            {activeSearchIndex !== null && (
                <GWASSearchModal
                    isOpen={true}
                    onClose={() => setActiveSearchIndex(null)}
                    onSelect={handleGwasSelect}
                />
            )}
        </>
    );
}
