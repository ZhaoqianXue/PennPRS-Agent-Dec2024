import React from "react";
import DiseaseGrid from "./DiseaseGrid";
import ModelGrid from "./ModelGrid";
import DownstreamOptions from "./DownstreamOptions";
import { ModelData } from "./ModelCard";
import { Search, Database, ArrowLeft, Construction } from "lucide-react";
import TrainingConfigForm, { TrainingConfig } from "./TrainingConfigForm";

import AncestrySelection from "./AncestrySelection";

export type ViewType = 'mode_selection' | 'disease_selection' | 'model_grid' | 'downstream_options' | 'train_config' | 'ancestry_selection' | 'coming_soon' | 'protein_search' | 'protein_grid';

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
    // New Props for Ancestry & Concurrent Search
    searchProgress?: { status: string; total: number; fetched: number; current_action: string } | null;
    isSearchComplete?: boolean;
    onAncestrySubmit?: (ancestries: string[]) => void;
    activeAncestry?: string[];
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
    searchProgress,
    isSearchComplete,
    onAncestrySubmit,
    activeAncestry
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

                {/* View: Training Config */}
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

                        <TrainingConfigForm
                            onSubmit={onTrainingSubmit}
                            defaultTrait={trait || undefined}
                            onCancel={onBackToSelection}
                        />
                    </div>
                )}

                {/* View Switching */}
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
            </div>
        </div>
    );
}
