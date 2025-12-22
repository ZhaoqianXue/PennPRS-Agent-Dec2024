"use client";

import { useState, useEffect } from "react";
import ChatInterface, { StructuredResponse } from "./ChatInterface";
import CanvasArea, { ViewType } from "./CanvasArea";
import { ModelData } from "./ModelCard";
import ModelDetailModal from "./ModelDetailModal";
import { ArrowLeft } from "lucide-react";
import { TrainingConfig } from "./TrainingConfigForm";

interface DiseasePageProps {
    onBack: () => void;
}

export default function DiseasePage({ onBack }: DiseasePageProps) {
    // Global State - INITIALIZED TO 'mode_selection'
    const [activeView, setActiveView] = useState<ViewType>('mode_selection');
    const [previousView, setPreviousView] = useState<ViewType>('mode_selection');
    const [currentTrait, setCurrentTrait] = useState<string | null>(null);

    // Data State
    const [models, setModels] = useState<ModelData[]>([]);
    const [downstreamOps, setDownstreamOps] = useState<{ modelId: string; trait: string; options: string[] } | null>(null);

    // Active Modals State
    const [selectedModelDetails, setSelectedModelDetails] = useState<ModelData | null>(null);

    // External Trigger Mechanism
    const [externalTriggerDetails, setExternalTriggerDetails] = useState<string | null>(null);

    // Search State (Concurrent)
    const [isSearching, setIsSearching] = useState(false);
    const [searchProgress, setSearchProgress] = useState<{ status: string; total: number; fetched: number; current_action: string } | null>(null);
    const [isSearchComplete, setIsSearchComplete] = useState(false);

    // Ancestry Selection State
    const [selectedAncestry, setSelectedAncestry] = useState<string[]>([]);
    const [isAncestrySubmitted, setIsAncestrySubmitted] = useState(false);

    const triggerChat = (msg: string) => {
        setExternalTriggerDetails(msg);
        setTimeout(() => setExternalTriggerDetails(null), 100);
    }

    // --- Handlers ---

    const handleDiseaseSelect = (trait: string) => {
        // RESET States
        setCurrentTrait(trait);
        setModels([]);
        setIsSearching(true);
        setIsSearchComplete(false);
        setIsAncestrySubmitted(false);
        setSearchProgress(null);
        setSelectedAncestry([]);
        setSmartRecommendation(null);
        setSmartRecommendationModel(null);
        setSmartRecommendationActions(null);

        // SWITCH to Ancestry Selection immediately
        setActiveView('ancestry_selection');

        // TRIGGER Search
        triggerChat(`I want to search for models for ${trait}`);
    };

    // Smart Recommendation State
    const [smartRecommendation, setSmartRecommendation] = useState<string | null>(null);
    const [smartRecommendationModel, setSmartRecommendationModel] = useState<ModelData | null>(null);
    const [smartRecommendationActions, setSmartRecommendationActions] = useState<string[] | null>(null);

    // --- Effects ---
    // Safety Net: Ensure we transition if both conditions are met
    useEffect(() => {
        if (activeView === 'ancestry_selection' && isSearchComplete && isAncestrySubmitted) {
            // GENERATE SMART RECOMMENDATION
            // 1. Filter models strictly by ancestry (re-using logic to match ModelGrid behavior)
            const ancestryMap: Record<string, string> = {
                'EUR': 'European', 'AFR': 'African', 'EAS': 'East Asian',
                'SAS': 'South Asian', 'AMR': 'Hispanic', 'MIX': 'Others'
            };

            const relevantModels = models.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload") return true;

                // If NO ancestry selected, show ALL models (Standard Logic)
                if (selectedAncestry.length === 0) return true;

                if (!m.ancestry) return false;

                // Strict Check
                const normalized = m.ancestry.toLowerCase();
                return selectedAncestry.some(t => {
                    const targetCode = t.toUpperCase();
                    const targetName = ancestryMap[targetCode] || t;
                    return normalized.includes(targetCode.toLowerCase()) || normalized.includes(targetName.toLowerCase());
                });
            });

            // 2. Find Best Model (Max AUC)
            if (relevantModels.length > 0) {
                // We utilize the helper from ModelCard if imported, or just check metrics directly roughly.
                // Since we need to be strictly consistent with the grid processing, we sort exactly as grid does (or simple AUC).
                const best = relevantModels.reduce((prev, current) => {
                    const prevAuc = prev.metrics?.AUC || 0;
                    const currAuc = current.metrics?.AUC || 0;
                    return prevAuc > currAuc ? prev : current;
                }, relevantModels[0]);

                let ancLabel = "All Ancestries";
                if (selectedAncestry.length > 0) {
                    ancLabel = selectedAncestry.map(a => ancestryMap[a] || a).join(", ");
                }

                // EXACT BACKEND FORMAT RESTORATION
                let msg = `I found **${relevantModels.length}** models for **'${currentTrait}'** `;
                if (selectedAncestry.length > 0) {
                    msg += `matching your ancestry criteria (**${ancLabel}**).\n\n`;
                } else {
                    msg += `across all ancestries.\n\n`;
                }

                msg += `The model with the highest AUC is **${best.name}** (ID: ${best.id}).\n`;
                msg += `I've displayed the best model card below. You can view detailed information for this result and others in the **Canvas** panel.\n\n`;
                msg += `How would you like to proceed?`;

                setSmartRecommendation(msg);
                setSmartRecommendationModel(best);
                setSmartRecommendationActions([
                    "Evaluate on Cohort",
                    "Build Ensemble Model",
                    "Download Model",
                    "Train Custom Model"
                ]);
            } else {
                const ancLabel = selectedAncestry.map(a => ancestryMap[a] || a).join(", ");
                setSmartRecommendation(`I searched for models matching **${ancLabel}** but found no direct matches in the training data.\n\nYou can browse the full list or try training a custom model.`);
                setSmartRecommendationModel(null);
                setSmartRecommendationActions(["Train Custom Model"]);
            }

            setActiveView('model_grid');
        }
    }, [activeView, isSearchComplete, isAncestrySubmitted, models, selectedAncestry, currentTrait]);

    const handleAncestrySubmit = (ancestries: string[]) => {
        setIsAncestrySubmitted(true);
        setSelectedAncestry(ancestries);
        // Effect will handle transition
    };

    const handleChatResponse = (response: StructuredResponse) => {
        if (response.type === 'model_grid') {
            setModels(response.models || []);
            setIsSearchComplete(true);
            setIsSearching(false);

            // If user has already submitted ancestry choice, move them to grid
            if (isAncestrySubmitted) {
                setActiveView('model_grid');
            }
            // Else: Do nothing, models are stored. User is still selecting.

        } else if (response.type === 'downstream_options') {
            setDownstreamOps(response.downstream || null);
            setActiveView('downstream_options');
        } else if (response.type === 'model_update' && response.model_update) {
            // ... (existing update logic)
            const { model_id, updates } = response.model_update;
            setModels(prev => prev.map(m => {
                if (m.id.toLowerCase() === model_id.toLowerCase()) {
                    const safeMetrics = m.metrics || {};
                    const updateMetrics = updates.metrics || {};
                    const newMetrics = { ...safeMetrics, ...updateMetrics };
                    return { ...m, ...updates, metrics: newMetrics };
                }
                return m;
            }));
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
        // Switch to the full-page training config view within the canvas
        setPreviousView(activeView);
        setActiveView('train_config');
    };

    const handleTrainingSubmit = (config: TrainingConfig) => {
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

        setModels(prev => [pendingModel, ...prev]);
        setActiveView('model_grid');

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

        triggerChat(prompt);
        // Training view handles its own post-submit actions or we can switch view here
        // For now, we go to model grid as per existing logic
    };

    const handleDownstreamAction = (action: string) => {
        triggerChat(`I want to perform ${action} analysis on the selected model.`);
    };

    // --- Mode Selection Handlers ---

    const handleModeSelect = (mode: 'search' | 'train') => {
        if (mode === 'search') {
            setActiveView('disease_selection');
        } else {
            // For train, we now switch to the full-page training config view within the canvas
            setPreviousView('mode_selection');
            setActiveView('train_config');
        }
    };

    const handleBackToPrevious = () => {
        if (activeView === 'train_config') {
            setActiveView(previousView);
        } else if (activeView === 'model_grid') {
            // Back from grid -> Go to ancestry selection to allow re-choice? Or Disease?
            // User requested: "Back to Disease List" for Model Grid previously.
            // But now flow is Disease -> Ancestry -> Grid.
            // Let's decide: Back should go to Ancestry Selection to refine.
            setActiveView('ancestry_selection');
            // BUT ensure we don't reset everything (isAncestrySubmitted=true maybe should be false if we go back?)
            setIsAncestrySubmitted(false); // Enable editing again
        } else if (activeView === 'ancestry_selection') {
            setActiveView('disease_selection');
        } else {
            // Default back behavior for other views
            setActiveView('mode_selection');
        }
    };

    // --- RENDER ---

    return (
        <div className="flex h-screen flex-col bg-background font-sans text-foreground overflow-hidden">
            {/* Header */}
            <header className="flex h-14 items-center border-b px-6 bg-white dark:bg-gray-900 z-10 shrink-0 shadow-sm">
                <div className="flex items-center gap-4 font-bold text-lg">
                    <button
                        onClick={onBack}
                        className="text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors"
                        title="Back to Modules"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Disease PRS Module</span>
                </div>
                <div className="ml-auto flex items-center gap-4">
                    {(activeView !== 'mode_selection') && (
                        <button
                            onClick={() => {
                                setActiveView('mode_selection');
                                setCurrentTrait(null);
                                setModels([]);
                            }}
                            className="text-sm font-medium text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            Start Over
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
                        onModeSelect={handleModeSelect}
                        onBackToSelection={handleBackToPrevious}
                        onTrainingSubmit={handleTrainingSubmit}
                        // Concurrent Search Props
                        searchProgress={searchProgress}
                        isSearchComplete={isSearchComplete}
                        onAncestrySubmit={handleAncestrySubmit}
                        activeAncestry={selectedAncestry}
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
                        onProgressUpdate={(p) => setSearchProgress(p)}
                        onSearchStatusChange={(s) => {
                            setIsSearching(s);
                            // If search starts, mark incomplete
                            if (s) setIsSearchComplete(false);
                        }}
                        deferAnalysis={true}
                        externalAgentMessage={smartRecommendation}
                        externalAgentMessage={smartRecommendation}
                        externalAgentModel={smartRecommendationModel}
                        externalAgentActions={smartRecommendationActions}
                        hasSelectedAncestry={isAncestrySubmitted}
                    />
                </div>

            </div>
        </div>
    );
}
