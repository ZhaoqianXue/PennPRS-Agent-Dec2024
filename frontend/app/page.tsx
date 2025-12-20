"use client";

import { useState } from "react";
import ChatInterface, { StructuredResponse } from "../components/ChatInterface";
import CanvasArea, { ViewType } from "../components/CanvasArea";
import { ModelData } from "../components/ModelCard";
import ModelDetailModal from "../components/ModelDetailModal";
import TrainingConfigModal, { TrainingConfig } from "../components/TrainingConfigModal";

export default function Home() {
  // Global State
  const [activeView, setActiveView] = useState<ViewType>('disease_selection');
  const [currentTrait, setCurrentTrait] = useState<string | null>(null);

  // Data State
  const [models, setModels] = useState<ModelData[]>([]);
  const [downstreamOps, setDownstreamOps] = useState<{ modelId: string; trait: string; options: string[] } | null>(null);

  // Active Modals State
  const [selectedModelDetails, setSelectedModelDetails] = useState<ModelData | null>(null);
  const [isTrainingModalOpen, setIsTrainingModalOpen] = useState(false);

  // External Trigger Mechanism (to send messages from Canvas)
  const [externalTriggerDetails, setExternalTriggerDetails] = useState<string | null>(null);

  const triggerChat = (msg: string) => {
    setExternalTriggerDetails(msg);
    // Reset after a tick to allow re-triggering same message if needed (though unlikely)
    setTimeout(() => setExternalTriggerDetails(null), 100);
  }

  // --- Handlers ---

  const handleDiseaseSelect = (trait: string) => {
    setCurrentTrait(trait);
    triggerChat(`I want to search for models for ${trait}`);
    // Note: We don't switch view yet, we wait for the agent to return the models
  };

  const handleChatResponse = (response: StructuredResponse) => {
    if (response.type === 'model_grid') {
      setModels(response.models || []);
      setActiveView('model_grid');
    } else if (response.type === 'downstream_options') {
      setDownstreamOps(response.downstream || null);
      setActiveView('downstream_options');
    } else if (response.type === 'model_update' && response.model_update) {
      // Handle partial update
      const { model_id, updates } = response.model_update;

      setModels(prev => prev.map(m => {
        if (m.id.toLowerCase() === model_id.toLowerCase()) {
          // Deep merge metrics
          const safeMetrics = m.metrics || {};
          const updateMetrics = updates.metrics || {};
          const newMetrics = { ...safeMetrics, ...updateMetrics };
          return { ...m, ...updates, metrics: newMetrics };
        }
        return m;
      }));

      // Also update selected details if open
      setSelectedModelDetails(prev => {
        if (!prev) return null;
        if (prev.id.toLowerCase() === model_id.toLowerCase()) {
          const safeMetrics = prev.metrics || {};
          const updateMetrics = updates.metrics || {};
          const newMetrics = { ...safeMetrics, ...updateMetrics };
          return { ...prev, ...updates, metrics: newMetrics };
        }
        return prev;
      });
    }
  };

  const handleSelectModel = (modelId: string) => {
    triggerChat(`I want to use existing model ${modelId} `);
  };

  const handleDeepScan = (modelId: string) => {
    triggerChat(`Deep fetch metadata for ${modelId}`);
  };

  const handleTrainNew = () => {
    setIsTrainingModalOpen(true);
  };

  const handleTrainingSubmit = (config: TrainingConfig) => {
    // 1. Optimistic Update: Add "Loading" card immediately
    const optimisticSource = config.dataSourceType === 'upload' ? "User Upload" : "User Trained";

    const pendingModel: ModelData = {
      id: `JOB-${Date.now()}`,
      name: config.jobName || `Custom Model (${config.trait})`,
      trait: config.trait,
      ancestry: config.ancestry,
      method: config.methods.join(", "),
      source: optimisticSource as ModelData['source'],
      isLoading: true,
      status: "running",
      metrics: { AUC: 0, R2: 0 },
      sample_size: config.sampleSize || 0
    };

    // Prepend to models list. ModelGrid sort will keep it at top.
    setModels(prev => [pendingModel, ...prev]);
    setActiveView('model_grid');

    // 2. Construct Rich Prompt for Backend
    let prompt = `I want to train a new model for ${config.trait} (Ancestry: ${config.ancestry}) named '${config.jobName}'.`;
    prompt += `\nMethods: ${config.methods.join(', ')}`;

    if (config.ensemble) prompt += `\nEnsemble: Enabled`;

    if (config.dataSourceType === 'public') {
      prompt += `\nData Source: Public GWAS (ID: ${config.gwasId || "Auto"})`;
    } else {
      prompt += `\nData Source: User Upload (${config.uploadedFileName})`;
      prompt += `\n[SYSTEM NOTE: File content handling simulated for agent prototype]`;
    }

    prompt += `\nTrait Type: ${config.traitType}, Sample Size: ${config.sampleSize}`;

    if (config.advanced) {
      prompt += `\nHyperparams: kb=${config.advanced.kb}, r2=${config.advanced.r2}, pval_thr=${config.advanced.pval_thr}`;
    }

    // Trigger Backend
    triggerChat(prompt);
    setIsTrainingModalOpen(false);
  };

  const handleDownstreamAction = (action: string) => {
    triggerChat(`I want to perform ${action} analysis on the selected model.`);
  };

  return (
    <div className="flex h-screen flex-col bg-background font-sans text-foreground overflow-hidden">
      {/* Header */}
      <header className="flex h-14 items-center border-b px-6 bg-white dark:bg-gray-900 z-10 shrink-0 shadow-sm">
        <div className="flex items-center gap-2 font-bold text-lg">
          <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">PennPRS Agent</span>
        </div>
        <div className="ml-auto flex items-center gap-4">
          {activeView !== 'disease_selection' && (
            <button
              onClick={() => {
                setActiveView('disease_selection');
                setCurrentTrait(null);
                setModels([]);
              }}
              className="text-sm font-medium text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white transition-colors"
            >
              Reset / Home
            </button>
          )}
        </div>
      </header>

      {/* Split Layout */}
      <div className="flex-1 flex overflow-hidden">

        {/* Left: Canvas Area (2/3) */}
        <div className="flex-[2] border-r border-gray-200 dark:border-gray-800 relative">
          <CanvasArea
            view={activeView}
            trait={currentTrait}
            models={models}
            downstreamOps={downstreamOps}
            onSelectDisease={handleDiseaseSelect}
            onSelectModel={handleSelectModel}
            onTrainNew={handleTrainNew}
            onViewDetails={setSelectedModelDetails}
            onDownstreamAction={handleDownstreamAction}
          />

          {/* Modals placed here to be relative to the App or Global */}
          <ModelDetailModal
            model={selectedModelDetails}
            isOpen={!!selectedModelDetails}
            onClose={() => setSelectedModelDetails(null)}
            onSelect={(id) => {
              handleSelectModel(id);
              setSelectedModelDetails(null);
            }}
            onDeepScan={handleDeepScan}
            onTrainNew={handleTrainNew}
            onDownstreamAction={handleDownstreamAction}
          />

          <TrainingConfigModal
            isOpen={isTrainingModalOpen}
            onClose={() => setIsTrainingModalOpen(false)}
            onSubmit={handleTrainingSubmit}
            defaultTrait={currentTrait || "Alzheimer's disease"}
          />
        </div>

        {/* Right: Chat Interface (1/3) */}
        <div className="flex-1 min-w-[320px] bg-white dark:bg-gray-900 border-l border-gray-100 dark:border-gray-800 shadow-xl z-20">
          <ChatInterface
            onResponse={handleChatResponse}
            currentTrait={currentTrait}
            externalTrigger={externalTriggerDetails}
            onViewDetails={setSelectedModelDetails}
            onTrainNew={handleTrainNew}
            onDownstreamAction={handleDownstreamAction}
          />
        </div>

      </div>
    </div>
  );
}
