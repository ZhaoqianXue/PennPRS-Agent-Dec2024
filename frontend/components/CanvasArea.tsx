import React from "react";
import DiseaseGrid from "./DiseaseGrid";
import ModelGrid from "./ModelGrid";
import DownstreamOptions from "./DownstreamOptions";
import ModelCard, { ModelData, getDisplayMetrics } from "./ModelCard";
import { Search, Database, ArrowLeft, ArrowRight, Construction, Users, User, Bookmark, Trash2, Download, Activity, Layers, CheckCircle2 } from "lucide-react";
import TrainingConfigForm, { TrainingConfig } from "./TrainingConfigForm";
import MultiAncestryTrainingForm, { MultiAncestryTrainingConfig } from "./MultiAncestryTrainingForm";

import AncestrySelection from "./AncestrySelection";

export type ViewType = 'mode_selection' | 'disease_selection' | 'model_grid' | 'downstream_options' | 'train_type_selection' | 'train_config' | 'train_multi_config' | 'ancestry_selection' | 'coming_soon' | 'protein_search' | 'protein_grid' | 'model_actions' | 'my_models';

interface CanvasAreaProps {
    view: ViewType;
    trait: string | null;
    models: ModelData[];
    downstreamOps: { modelId: string; trait: string; options: string[] } | null;
    onSelectDisease: (trait: string) => void;
    onSelectModel: (modelId: string) => void;
    onTrainNew: () => void;
    onViewDetails: (model: ModelData) => void;
    onDownstreamAction: (action: string) => void;
    onModeSelect: (mode: 'search' | 'train') => void;
    onBackToSelection: () => void;
    onTrainingSubmit: (config: TrainingConfig) => void;
    onMultiAncestrySubmit?: (config: MultiAncestryTrainingConfig) => void;
    onTrainTypeSelect?: (type: 'single' | 'multi') => void;
    // New Props for Ancestry & Concurrent Search
    searchProgress?: { status: string; total: number; fetched: number; current_action: string } | null;
    isSearchComplete?: boolean;
    onAncestrySubmit?: (ancestries: string[]) => void;
    activeAncestry?: string[];
    // Model Actions Page Props
    selectedActionModel?: ModelData | null;
    // My Models Page Props
    savedModels?: ModelData[];
    onRemoveSavedModel?: (modelId: string) => void;
    onSelectSavedModel?: (model: ModelData) => void;
    // Navigation Props
    onGoToModelGrid?: () => void;
    canGoForward?: boolean;
    onGoForward?: () => void;
}

export default function CanvasArea({
    view,
    trait,
    models,
    downstreamOps,
    onSelectDisease,
    onSelectModel,
    onTrainNew,
    onViewDetails,
    onDownstreamAction,
    onModeSelect,
    onBackToSelection,
    onTrainingSubmit,
    onMultiAncestrySubmit,
    onTrainTypeSelect,
    searchProgress,
    isSearchComplete,
    onAncestrySubmit,
    activeAncestry,
    selectedActionModel,
    savedModels,
    onRemoveSavedModel,
    onSelectSavedModel,
    onGoToModelGrid,
    canGoForward,
    onGoForward
}: CanvasAreaProps) {

    return (
        <div className="h-full w-full bg-gray-50/50 dark:bg-gray-900/50 overflow-y-auto p-4 sm:p-6 transition-all duration-300">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header / Context Info */}
                {view !== 'disease_selection' && view !== 'mode_selection' && trait && (
                    <div className="mb-6">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            {trait}
                            <span className="text-sm font-normal text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
                                Current Context
                            </span>
                        </h2>
                    </div>
                )}

                {/* View: Mode Selection (Start) */}
                {view === 'mode_selection' && (
                    <div className="flex flex-col items-center justify-center min-h-[70vh] animate-in fade-in zoom-in-95 duration-500">
                        <div className="text-center space-y-4 mb-12">
                            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-gray-900 dark:text-white">
                                Disease PRS Module
                            </h1>
                            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-lg mx-auto">
                                Choose how you want to proceed with your Polygenic Risk Score analysis.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl px-4">
                            {/* Search Card */}
                            <button
                                onClick={() => onModeSelect('search')}
                                className="group relative flex flex-col items-center p-10 bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 text-center"
                            >
                                <div className="mb-6 p-6 bg-blue-50 dark:bg-blue-900/30 rounded-full group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                                    <Search className="w-12 h-12 text-blue-600 dark:text-blue-400" />
                                </div>
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Search Existing Models</h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                                    Browse pre-trained models from PGS Catalog & PennPRS.
                                </p>
                            </button>

                            {/* Train Card */}
                            <button
                                onClick={() => onModeSelect('train')}
                                className="group relative flex flex-col items-center p-10 bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 text-center"
                            >
                                <div className="mb-6 p-6 bg-purple-50 dark:bg-purple-900/30 rounded-full group-hover:bg-purple-100 dark:group-hover:bg-purple-900/50 transition-colors">
                                    <Database className="w-12 h-12 text-purple-600 dark:text-purple-400" />
                                </div>
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Train Custom Model</h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                                    Upload GWAS summary statistics to train a new model.
                                </p>
                            </button>
                        </div>
                    </div>
                )}

                {/* View: Training Type Selection */}
                {view === 'train_type_selection' && (
                    <div className="animate-in fade-in zoom-in-95 duration-500 pb-8">
                        {/* Back Button */}
                        <div className="mb-6">
                            <button
                                onClick={onBackToSelection}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back</span>
                            </button>
                        </div>

                        <div className="text-center space-y-3 mb-8">
                            <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
                                Train Custom Model
                            </h1>
                            <p className="text-base text-gray-500 dark:text-gray-400 max-w-xl mx-auto">
                                Choose your analysis type based on your GWAS data and research goals.
                            </p>
                        </div>

                        <div className="flex flex-col gap-6 w-full max-w-5xl mx-auto">
                            {/* Single-Ancestry Card */}
                            <button
                                onClick={() => onTrainTypeSelect?.('single')}
                                className="group relative flex flex-col md:flex-row bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 hover:shadow-xl hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-300 overflow-hidden text-left"
                            >
                                {/* Left: Info */}
                                <div className="flex flex-col justify-center p-6 md:w-1/3 border-b md:border-b-0 md:border-r border-gray-100 dark:border-gray-700">
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                                            <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                        </div>
                                        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Single-Ancestry Analysis</h2>
                                    </div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Train PRS models for a single population</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                                        Supports <span className="font-semibold text-blue-600 dark:text-blue-400">Pseudo-Training</span> and
                                        <span className="font-semibold text-orange-600 dark:text-orange-400"> Tuning-Parameter-Free</span> methods.
                                    </p>
                                </div>

                                {/* Right: Workflow Image */}
                                <div className="relative flex-1 bg-gray-50 dark:bg-gray-900/50 p-4 flex items-center justify-center">
                                    <img
                                        src="/single_ancestry_workflow.png"
                                        alt="Single-Ancestry Workflow"
                                        className="w-full h-auto max-h-64 object-contain"
                                    />
                                </div>
                            </button>

                            {/* Multi-Ancestry Card */}
                            <button
                                onClick={() => onTrainTypeSelect?.('multi')}
                                className="group relative flex flex-col md:flex-row bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 hover:shadow-xl hover:border-purple-300 dark:hover:border-purple-600 transition-all duration-300 overflow-hidden text-left"
                            >
                                {/* Left: Info */}
                                <div className="flex flex-col justify-center p-6 md:w-1/3 border-b md:border-b-0 md:border-r border-gray-100 dark:border-gray-700">
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="p-3 bg-purple-50 dark:bg-purple-900/30 rounded-xl group-hover:bg-purple-100 dark:group-hover:bg-purple-900/50 transition-colors">
                                            <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                                        </div>
                                        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Multi-Ancestry Analysis</h2>
                                    </div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Train PRS models across multiple populations</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                                        Leverage GWAS data from multiple ancestries using the
                                        <span className="font-semibold text-purple-600 dark:text-purple-400"> PROSPER</span> method.
                                    </p>
                                </div>

                                {/* Right: Workflow Image */}
                                <div className="relative flex-1 bg-gray-50 dark:bg-gray-900/50 p-4 flex items-center justify-center">
                                    <img
                                        src="/multi_ancestry_workflow.png"
                                        alt="Multi-Ancestry Workflow"
                                        className="w-full h-auto max-h-64 object-contain"
                                    />
                                </div>
                            </button>
                        </div>
                    </div>
                )}

                {/* View: Training Config (Single-Ancestry) */}
                {view === 'train_config' && (
                    <div className="relative min-h-[60vh] animate-in fade-in slide-in-from-right-8 duration-500">
                        {/* Back Button */}
                        <div className="mb-6">
                            <button
                                onClick={onBackToSelection}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back to Selection</span>
                            </button>
                        </div>

                        {/* Title indicating Single-Ancestry */}
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                                <User className="w-6 h-6 text-blue-600" />
                                Single-Ancestry Analysis
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">Configure your single-ancestry PRS training job</p>
                        </div>

                        <TrainingConfigForm
                            onSubmit={onTrainingSubmit}
                            defaultTrait={trait || undefined}
                            onCancel={onBackToSelection}
                        />
                    </div>
                )}

                {/* View: Multi-Ancestry Training Config */}
                {view === 'train_multi_config' && (
                    <div className="relative min-h-[60vh] animate-in fade-in slide-in-from-right-8 duration-500">
                        {/* Back Button */}
                        <div className="mb-6">
                            <button
                                onClick={onBackToSelection}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back to Selection</span>
                            </button>
                        </div>

                        {/* Title indicating Multi-Ancestry */}
                        <div className="mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                                <Users className="w-6 h-6 text-purple-600" />
                                Multi-Ancestry Analysis
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">Configure your multi-ancestry PRS training job using PROSPER</p>
                        </div>

                        <MultiAncestryTrainingForm
                            onSubmit={onMultiAncestrySubmit!}
                            onCancel={onBackToSelection}
                        />
                    </div>
                )}
                {view === 'disease_selection' && (
                    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8 animate-in fade-in slide-in-from-right-8 duration-500 relative">
                        {/* Back Button */}
                        <div className="absolute top-0 left-0">
                            <button
                                onClick={onBackToSelection}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-4 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back</span>
                            </button>
                        </div>

                        <div className="text-center space-y-2 pt-12">
                            <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
                                Select a Target Disease
                            </h1>
                            <p className="text-gray-500 dark:text-gray-400">
                                Select a phenotype to view available models.
                            </p>
                        </div>
                        <div className="w-full max-w-4xl">
                            <DiseaseGrid onSelect={onSelectDisease} />
                        </div>
                    </div>
                )}

                {/* View: Ancestry Selection */}
                {view === 'ancestry_selection' && onAncestrySubmit && (
                    <div className="animate-in fade-in slide-in-from-right-8 duration-500 h-full">
                        <div className="mb-4">
                            <button
                                onClick={onBackToSelection}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back</span>
                            </button>
                        </div>
                        <AncestrySelection
                            onSelect={onAncestrySubmit}
                            searchProgress={searchProgress || null}
                            isSearchComplete={!!isSearchComplete}
                            activeAncestry={activeAncestry || []} // Pass activeAncestry to AncestrySelection
                        />
                    </div>
                )}

                {view === 'model_grid' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* Back Button */}
                        <div className="mb-4">
                            <button
                                onClick={onBackToSelection}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back to Disease List</span>
                            </button>
                        </div>
                        <ModelGrid
                            models={models}
                            onSelectModel={onSelectModel}
                            onTrainNew={onTrainNew}
                            onViewDetails={onViewDetails}
                            activeAncestry={activeAncestry}
                            onAncestryChange={onAncestrySubmit}
                        />
                    </div>
                )}

                {view === 'downstream_options' && downstreamOps && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-8">
                        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
                            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">Model Selected: {downstreamOps.modelId}</h3>
                            <p className="text-blue-700 dark:text-blue-300">
                                The model is ready for downstream analysis. Choose an option below to proceed.
                            </p>
                        </div>

                        <DownstreamOptions
                            modelId={downstreamOps.modelId}
                            trait={downstreamOps.trait}
                            onAction={onDownstreamAction}
                        />
                    </div>
                )}

                {/* View: Coming Soon (Under Development) */}
                {view === 'coming_soon' && (
                    <div className="flex flex-col items-center justify-center min-h-[60vh] animate-in fade-in zoom-in-95 duration-500">
                        <div className="text-center space-y-6 max-w-md">
                            <div className="w-24 h-24 mx-auto rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                                <Construction className="w-12 h-12 text-amber-600 dark:text-amber-400" />
                            </div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                Feature Under Development
                            </h1>
                            <p className="text-gray-500 dark:text-gray-400 leading-relaxed">
                                This feature is currently being developed and will be available in a future release.
                                Thank you for your patience!
                            </p>
                            <button
                                onClick={onBackToSelection}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Return to Previous Page
                            </button>
                        </div>
                    </div>
                )}

                {/* View: Model Actions (After Download/Save) - Using ModelDetailModal-style content */}
                {view === 'model_actions' && selectedActionModel && (() => {
                    const model = selectedActionModel;
                    const { displayAUC, displayR2, isMatched, isDerived, matchedAncestry } = getDisplayMetrics(model);

                    return (
                        <div className="animate-in fade-in duration-500 min-h-full">
                            {/* Gradient Background */}
                            <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-violet-50 dark:from-gray-900 dark:via-gray-900 dark:to-violet-950/30" />

                            <div className="relative z-10">
                                {/* Navigation Header */}
                                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={onBackToSelection}
                                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                                        >
                                            <ArrowLeft size={18} />
                                            <span className="text-sm font-medium">Back</span>
                                        </button>
                                        <button
                                            onClick={onGoForward}
                                            disabled={!canGoForward}
                                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"
                                        >
                                            <ArrowRight size={18} />
                                        </button>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm text-gray-500">Viewing:</span>
                                        <span className="text-sm font-mono font-medium text-violet-600 dark:text-violet-400">{model.id}</span>
                                    </div>
                                </div>

                                {/* Main Content - Two Column Layout */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 h-full">

                                    {/* Left Column - Full Model Details (Same as ModelDetailModal) */}
                                    <div className="border-r border-gray-200/50 dark:border-gray-700/50 overflow-y-auto max-h-[calc(100vh-180px)]">
                                        <div className="p-6 space-y-6">
                                            {/* Model Header */}
                                            <div className="flex items-center justify-between gap-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-2 bg-violet-100 dark:bg-violet-900/40 rounded-lg">
                                                        <Database className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                                                    </div>
                                                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">{model.name}</h2>
                                                </div>
                                                <span className="flex items-center gap-1.5 text-sm font-medium text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-full">
                                                    <CheckCircle2 className="w-3.5 h-3.5" /> Saved
                                                </span>
                                            </div>

                                            {/* Key Metrics - Same as ModelDetailModal */}
                                            <div className="grid grid-cols-3 gap-4">
                                                {/* 1. AUC */}
                                                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800 relative overflow-hidden">
                                                    <div className="flex justify-between items-start mb-1">
                                                        <div className="text-xs uppercase tracking-wider text-blue-600 dark:text-blue-400 font-semibold">AUC</div>
                                                        {isMatched && <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 rounded-full font-medium" title="Matched to Training Ancestry">Matched</span>}
                                                        {!isMatched && isDerived && <span className="text-[10px] bg-gray-100 text-gray-600 px-1.5 rounded-full font-medium" title={`Best Available (from ${matchedAncestry})`}>Best ({matchedAncestry})</span>}
                                                    </div>
                                                    <div className="text-2xl font-bold font-mono text-blue-700 dark:text-blue-300">
                                                        {displayAUC ? displayAUC.toFixed(3) : "N/A"}
                                                    </div>
                                                    <div className="text-[10px] text-blue-500 mt-1">Classification Accuracy</div>
                                                </div>

                                                {/* 2. R2 */}
                                                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-100 dark:border-purple-800">
                                                    <div className="text-xs uppercase tracking-wider text-purple-600 dark:text-purple-400 font-semibold mb-1">R²</div>
                                                    <div className="text-2xl font-bold font-mono text-purple-700 dark:text-purple-300">
                                                        {displayR2 ? displayR2.toFixed(4) : "N/A"}
                                                    </div>
                                                    <div className="text-[10px] text-purple-500 mt-1">Variance Explained</div>
                                                </div>

                                                {/* 3. Sample Size */}
                                                <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-100 dark:border-gray-800">
                                                    <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-1">Sample Size</div>
                                                    <div className="text-2xl font-bold font-mono text-gray-900 dark:text-white truncate">
                                                        {model.sample_size ? (model.sample_size / 1000).toFixed(1) + 'k' : '-'}
                                                    </div>
                                                    <div className="text-[10px] text-gray-500 mt-1 truncate" title={model.ancestry}>
                                                        {model.ancestry || "Unknown Ancestry"}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Secondary Metrics Row */}
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-100 dark:border-green-800 flex items-center justify-between">
                                                    <span className="text-xs font-semibold text-green-700 dark:text-green-400">
                                                        {model.metrics?.HR ? 'Hazard Ratio' : model.metrics?.OR ? 'Odds Ratio' : model.metrics?.Beta ? 'Beta' : 'Effect Size'}
                                                    </span>
                                                    <span className="text-lg font-mono font-bold text-green-700 dark:text-green-300">
                                                        {model.metrics?.HR ? model.metrics.HR.toFixed(2) :
                                                            model.metrics?.OR ? model.metrics.OR.toFixed(2) :
                                                                model.metrics?.Beta ? model.metrics.Beta.toFixed(2) : "N/A"}
                                                    </span>
                                                </div>

                                                <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-800 flex items-center justify-between">
                                                    <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">Variants</span>
                                                    <span className="text-lg font-mono font-bold text-gray-800 dark:text-gray-200">
                                                        {model.num_variants ? model.num_variants.toLocaleString() : "N/A"}
                                                    </span>
                                                </div>
                                            </div>

                                            {/* Introduction Description */}
                                            <div className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed border-b border-gray-100 dark:border-gray-800 pb-4">
                                                This Polygenic Risk Score model targets <strong>{model.trait}</strong> and was developed using the <strong>{model.method}</strong> method.
                                                {model.source === 'PGS Catalog'
                                                    ? " It is curated from the PGS Catalog."
                                                    : " It was trained via PennPRS."}
                                                <div className="flex items-center gap-2 mt-2 text-xs text-green-600 dark:text-green-400">
                                                    <CheckCircle2 className="w-3 h-3" />
                                                    <span>Ready for Scoring</span>
                                                </div>
                                            </div>

                                            {/* Detailed Info Section */}
                                            <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-800 text-sm space-y-4 font-mono text-xs">
                                                {/* Section A: Predicted Trait */}
                                                <div className="pb-4 border-b border-gray-200 dark:border-gray-700">
                                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-blue-500 pl-2">Predicted Trait</h5>
                                                    <div className="grid grid-cols-3 gap-2 mb-2">
                                                        <span className="text-gray-500">Reported Trait:</span>
                                                        <span className="col-span-2 text-gray-900 dark:text-gray-100 font-medium">{model.trait_reported || model.trait || "N/A"}</span>
                                                    </div>
                                                </div>

                                                {/* Section B: Score Construction */}
                                                <div className="pb-4 border-b border-gray-200 dark:border-gray-700">
                                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-purple-500 pl-2">Score Construction</h5>
                                                    <div className="grid grid-cols-1 gap-y-2">
                                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">PGS Name:</span><span className="col-span-2 font-medium text-gray-900 dark:text-gray-100">{model.pgs_name || model.id || "N/A"}</span></div>
                                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Genome Build:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.variants_genomebuild || "N/A"}</span></div>
                                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Variants:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.num_variants ? model.num_variants.toLocaleString() : "N/A"}</span></div>
                                                        <div className="grid grid-cols-3 gap-2"><span className="text-gray-500">Method:</span><span className="col-span-2 text-gray-900 dark:text-gray-100">{model.method || "N/A"}</span></div>
                                                    </div>
                                                </div>

                                                {/* Section C: Source */}
                                                <div>
                                                    <h5 className="font-bold text-gray-800 dark:text-gray-200 mb-3 font-sans text-sm border-l-4 border-yellow-500 pl-2">Source & Metadata</h5>
                                                    <div className="grid grid-cols-3 gap-2">
                                                        <span className="text-gray-500">PGS Catalog:</span>
                                                        <a href={`https://www.pgscatalog.org/score/${model.id}/`} target="_blank" rel="noreferrer" className="col-span-2 text-blue-600 hover:underline font-mono text-xs break-all">
                                                            https://www.pgscatalog.org/score/{model.id}/
                                                        </a>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Download Button */}
                                            {model.download_url && (
                                                <button
                                                    onClick={() => window.open(model.download_url, '_blank')}
                                                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
                                                >
                                                    <Download className="w-4 h-4" />
                                                    Download Model Files
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    {/* Right Column - Downstream Analysis Options */}
                                    <div className="p-8 overflow-y-auto max-h-[calc(100vh-180px)]">
                                        <div className="space-y-6">
                                            {/* Header */}
                                            <div>
                                                <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-2">
                                                    Downstream Analysis
                                                </h1>
                                                <p className="text-gray-500 dark:text-gray-400">
                                                    Choose how you want to use this model for further analysis
                                                </p>
                                            </div>

                                            {/* Action Cards */}
                                            <div className="grid grid-cols-1 gap-6">
                                                {/* Evaluate Card */}
                                                <button
                                                    onClick={() => onDownstreamAction("Evaluate this Model on Cohort(s)")}
                                                    className="group relative flex items-start gap-6 p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-2xl hover:border-teal-300 dark:hover:border-teal-600 transition-all duration-300 text-left overflow-hidden"
                                                >
                                                    <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-teal-400/20 to-transparent rounded-full blur-2xl group-hover:w-48 group-hover:h-48 transition-all duration-500" />

                                                    <div className="shrink-0 p-4 bg-gradient-to-br from-teal-400 to-teal-600 rounded-2xl shadow-lg shadow-teal-500/25 group-hover:scale-110 transition-transform duration-300">
                                                        <Activity className="w-8 h-8 text-white" />
                                                    </div>
                                                    <div className="flex-1 relative">
                                                        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2 group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">
                                                            Evaluate on Cohort(s)
                                                        </h2>
                                                        <p className="text-gray-500 dark:text-gray-400 leading-relaxed">
                                                            Validate the model's performance by evaluating it on your own cohorts or external datasets. Compare predictions across different populations.
                                                        </p>
                                                        <div className="mt-4 flex items-center gap-2 text-sm font-medium text-teal-600 dark:text-teal-400">
                                                            <span>Start Evaluation</span>
                                                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                                        </div>
                                                    </div>
                                                </button>

                                                {/* Ensemble Card */}
                                                <button
                                                    onClick={() => onDownstreamAction("Ensemble this Model Across Phenotypes")}
                                                    className="group relative flex items-start gap-6 p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-2xl hover:border-purple-300 dark:hover:border-purple-600 transition-all duration-300 text-left overflow-hidden"
                                                >
                                                    <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-400/20 to-transparent rounded-full blur-2xl group-hover:w-48 group-hover:h-48 transition-all duration-500" />

                                                    <div className="shrink-0 p-4 bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl shadow-lg shadow-purple-500/25 group-hover:scale-110 transition-transform duration-300">
                                                        <Layers className="w-8 h-8 text-white" />
                                                    </div>
                                                    <div className="flex-1 relative">
                                                        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                                                            Ensemble Across Phenotypes
                                                        </h2>
                                                        <p className="text-gray-500 dark:text-gray-400 leading-relaxed">
                                                            Combine this model with other PRS models to create a powerful ensemble. Leverage multi-trait genetic architecture for improved prediction accuracy.
                                                        </p>
                                                        <div className="mt-4 flex items-center gap-2 text-sm font-medium text-purple-600 dark:text-purple-400">
                                                            <span>Create Ensemble</span>
                                                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                                        </div>
                                                    </div>
                                                </button>
                                            </div>

                                            {/* Quick Actions */}
                                            <div className="flex items-center gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                                                <button
                                                    onClick={onGoToModelGrid || onBackToSelection}
                                                    className="flex-1 px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                                                >
                                                    Browse More Models
                                                </button>
                                                <button
                                                    onClick={onTrainNew}
                                                    className="flex-1 px-4 py-3 text-sm font-medium text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-900/20 rounded-xl hover:bg-violet-100 dark:hover:bg-violet-900/30 transition-colors"
                                                >
                                                    Train Custom Model
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })()}

                {/* View: My Models - Saved/Downloaded Models Library */}
                {view === 'my_models' && (
                    <div className="animate-in fade-in duration-500 min-h-full">
                        {/* Gradient Background */}
                        <div className="absolute inset-0 bg-gradient-to-br from-violet-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/30" />

                        <div className="relative z-10 p-8">
                            {/* Back Button */}
                            <button
                                onClick={() => onModeSelect('search')}
                                className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/50 dark:hover:bg-gray-800/50 backdrop-blur-sm mb-6"
                            >
                                <ArrowLeft size={18} />
                                <span className="text-sm font-medium">Back to Search</span>
                            </button>

                            {/* Header */}
                            <div className="text-center mb-10">
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/25 mb-6">
                                    <Bookmark className="w-8 h-8 text-white" />
                                </div>
                                <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-3">
                                    My Saved Models
                                </h1>
                                <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
                                    Access your downloaded and bookmarked PRS models. Click on a model to view details and perform downstream analysis.
                                </p>
                            </div>

                            {/* Models Grid - Using ModelCard component for consistency */}
                            {savedModels && savedModels.length > 0 ? (
                                <div className="max-w-6xl mx-auto">
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 mb-10">
                                        {savedModels.map((model) => (
                                            <div key={model.id} className="relative group">
                                                {/* Remove button overlay */}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onRemoveSavedModel?.(model.id);
                                                    }}
                                                    className="absolute top-2 right-2 z-10 p-1.5 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors opacity-0 group-hover:opacity-100 shadow-sm"
                                                    title="Remove from saved"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>

                                                {/* Use same ModelCard as search results */}
                                                <ModelCard
                                                    model={model}
                                                    onSelect={() => onSelectSavedModel?.(model)}
                                                    onViewDetails={() => onSelectSavedModel?.(model)}
                                                />
                                            </div>
                                        ))}
                                    </div>

                                    {/* Quick Actions */}
                                    <div className="flex justify-center gap-4">
                                        <button
                                            onClick={() => onModeSelect('search')}
                                            className="px-6 py-3 text-sm font-medium text-gray-600 dark:text-gray-400 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                                        >
                                            Search More Models
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                /* Empty State */
                                <div className="max-w-md mx-auto text-center py-16">
                                    <div className="w-24 h-24 mx-auto mb-6 rounded-3xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                                        <Bookmark className="w-12 h-12 text-gray-300 dark:text-gray-600" />
                                    </div>
                                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                                        No Saved Models Yet
                                    </h2>
                                    <p className="text-gray-500 dark:text-gray-400 mb-8">
                                        Start by searching for PRS models and save the ones you want to use for downstream analysis.
                                    </p>
                                    <button
                                        onClick={() => onModeSelect('search')}
                                        className="px-8 py-3 bg-gradient-to-r from-violet-500 to-indigo-600 text-white font-medium rounded-xl hover:from-violet-600 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl"
                                    >
                                        Search for Models
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
