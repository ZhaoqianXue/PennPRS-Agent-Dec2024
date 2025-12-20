import React from "react";
import DiseaseGrid from "./DiseaseGrid";
import ModelGrid from "./ModelGrid";
import DownstreamOptions from "./DownstreamOptions";
import { ModelData } from "./ModelCard";
import { TrainingConfig } from "./TrainingConfigModal";

export type ViewType = 'disease_selection' | 'model_grid' | 'downstream_options';

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
    onDownstreamAction
}: CanvasAreaProps) {

    return (
        <div className="h-full w-full bg-gray-50/50 dark:bg-gray-900/50 overflow-y-auto p-4 sm:p-6 transition-all duration-300">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header / Context Info */}
                {view !== 'disease_selection' && trait && (
                    <div className="mb-6">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            {trait}
                            <span className="text-sm font-normal text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
                                Current Context
                            </span>
                        </h2>
                    </div>
                )}

                {/* View Switching */}
                {view === 'disease_selection' && (
                    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8">
                        <div className="text-center space-y-2">
                            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-gray-900 dark:text-white">
                                PennPRS Agent
                            </h1>
                            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-lg mx-auto">
                                Start by selecting a disease to explore existing PRS models or train your own.
                            </p>
                        </div>
                        <div className="w-full max-w-4xl">
                            <DiseaseGrid onSelect={onSelectDisease} />
                        </div>
                    </div>
                )}

                {view === 'model_grid' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <ModelGrid
                            models={models}
                            onSelectModel={onSelectModel}
                            onTrainNew={onTrainNew}
                            onViewDetails={onViewDetails}
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

                        {/* Back button or Breadcrumbs could go here */}
                    </div>
                )}
            </div>
        </div>
    );
}
