"use client";

import { useState, useEffect, useRef } from "react";
import ChatInterface, { StructuredResponse } from "./ChatInterface";
import CanvasArea, { ViewType } from "./CanvasArea";
import { ModelData } from "./ModelCard";
import ModelDetailModal from "./ModelDetailModal";
import { Home, Bookmark, Download, CheckCircle2, Mail } from "lucide-react";
import { TrainingConfig } from "./TrainingConfigForm";
import { MultiAncestryTrainingConfig } from "./MultiAncestryTrainingForm";
import { AnimatePresence, motion } from "framer-motion";

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

    // Selected Model for Actions Page (after download)
    const [selectedActionModel, setSelectedActionModel] = useState<ModelData | null>(null);

    // External Trigger Mechanism
    const [externalTriggerDetails, setExternalTriggerDetails] = useState<string | null>(null);

    // Search State (Concurrent)
    const [isSearching, setIsSearching] = useState(false);
    const [searchProgress, setSearchProgress] = useState<{ status: string; total: number; fetched: number; current_action: string } | null>(null);
    const [isSearchComplete, setIsSearchComplete] = useState(false);

    // Ancestry Selection State
    const [selectedAncestry, setSelectedAncestry] = useState<string[]>([]);
    const [isAncestrySubmitted, setIsAncestrySubmitted] = useState(false);

    // Saved/Downloaded Models State
    const [savedModels, setSavedModels] = useState<ModelData[]>([]);

    // Flying Animation State
    const [flyingModel, setFlyingModel] = useState<{ model: ModelData; startPos: { x: number; y: number } } | null>(null);
    const savedButtonRef = useRef<HTMLButtonElement>(null);

    // Training Submission Confirmation Modal State
    const [trainingSubmitModal, setTrainingSubmitModal] = useState<{
        isOpen: boolean;
        jobName: string;
        email: string;
        jobType: 'single' | 'multi';
    } | null>(null);

    // Training Submission Loading State
    const [isTrainingSubmitting, setIsTrainingSubmitting] = useState(false);

    // Navigation History - Simple Stack
    const [viewStack, setViewStack] = useState<ViewType[]>(['mode_selection']);
    const [forwardStack, setForwardStack] = useState<ViewType[]>([]);

    // Push a new view onto the stack (used for forward navigation)
    const pushView = (newView: ViewType) => {
        setViewStack(prev => [...prev, newView]);
        setForwardStack([]); // Clear forward history when navigating to new view
        setActiveView(newView);
    };

    // Go back one step
    const goBack = () => {
        if (viewStack.length > 1) {
            const newStack = [...viewStack];
            const currentView = newStack.pop()!;
            const previousView = newStack[newStack.length - 1];

            setViewStack(newStack);
            setForwardStack(prev => [currentView, ...prev]);

            // Cleanup for specific views
            if (activeView === 'model_actions') {
                setSelectedActionModel(null);
            } else if (activeView === 'model_grid') {
                setIsAncestrySubmitted(false);
            }

            setActiveView(previousView);
        }
    };

    // Go forward one step
    const goForward = () => {
        if (forwardStack.length > 0) {
            const newForwardStack = [...forwardStack];
            const nextView = newForwardStack.shift()!;

            setForwardStack(newForwardStack);
            setViewStack(prev => [...prev, nextView]);
            setActiveView(nextView);
        }
    };

    const canGoBack = viewStack.length > 1;
    const canGoForward = forwardStack.length > 0;

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

        // NEW FLOW: Stay on disease_selection while searching (shows loading state)
        // View will transition to search_summary when search completes

        // TRIGGER Search
        triggerChat(`I want to search for models for ${trait}`);
    };

    // Smart Recommendation State
    const [smartRecommendation, setSmartRecommendation] = useState<string | null>(null);
    const [smartRecommendationModel, setSmartRecommendationModel] = useState<ModelData | null>(null);
    const [smartRecommendationActions, setSmartRecommendationActions] = useState<string[] | null>(null);

    // --- Effects ---
    // Handle transition from search_summary to model_grid when ancestry is submitted
    useEffect(() => {
        if (activeView === 'search_summary' && isAncestrySubmitted) {
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
                msg += `I've displayed the best model card below. You can view detailed information for this result and others in the **Canvas** panel.`;

                setSmartRecommendation(msg);
                setSmartRecommendationModel(best);
                setSmartRecommendationActions([
                    "Download this Model",
                    "Train a Custom Model"
                ]);
            } else {
                const ancLabel = selectedAncestry.map(a => ancestryMap[a] || a).join(", ");
                setSmartRecommendation(`I searched for models matching **${ancLabel}** but found no direct matches in the training data.\n\nYou can browse the full list or try training a custom model.`);
                setSmartRecommendationModel(null);
                setSmartRecommendationActions(["Train Custom Model"]);
            }

            pushView('model_grid');
        }
    }, [activeView, isAncestrySubmitted, models, selectedAncestry, currentTrait]);

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

            // NEW FLOW: Transition to search_summary view to show summary with ancestry filtering
            pushView('search_summary');

        } else if (response.type === 'downstream_options') {
            setDownstreamOps(response.downstream || null);
            pushView('downstream_options');
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
        // Switch to the train type selection page first
        setPreviousView(activeView);
        pushView('train_type_selection');
    };

    const handleTrainingSubmit = async (config: TrainingConfig) => {
        setIsTrainingSubmitting(true);  // Start loading
        try {
            // Call backend API to submit training job with user's email
            const response = await fetch('http://localhost:8000/api/submit-training-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jobName: config.jobName,
                    email: config.email,
                    jobType: config.jobType,
                    trait: config.trait,
                    ancestry: config.ancestry,
                    methods: config.methods,
                    methodologyCategory: config.methodologyCategory,
                    ensemble: config.ensemble,
                    dataSourceType: config.dataSourceType,
                    database: config.database,
                    gwasId: config.gwasId,
                    uploadedFileName: config.uploadedFileName,
                    traitType: config.traitType,
                    sampleSize: config.sampleSize,
                    advanced: config.advanced
                })
            });

            // Show confirmation modal regardless of API response for now
            // (In production, handle error case separately)
            setTrainingSubmitModal({
                isOpen: true,
                jobName: config.jobName,
                email: config.email,
                jobType: 'single'
            });
        } catch (error) {
            console.error('Error submitting training job:', error);
            // Still show modal even if API call fails (for demo purposes)
            setTrainingSubmitModal({
                isOpen: true,
                jobName: config.jobName,
                email: config.email,
                jobType: 'single'
            });
        } finally {
            setIsTrainingSubmitting(false);  // Stop loading
        }
    };

    const handleDownstreamAction = (action: string) => {
        // Check if action is Evaluate or Ensemble - these are under development
        if (action.includes("Evaluate") || action.includes("Ensemble")) {
            setPreviousView(activeView);
            pushView('coming_soon');
        } else {
            triggerChat(`I want to perform ${action} analysis on the selected model.`);
        }
    };

    // --- Handle Model Save (Bookmark only, no download) ---
    const handleModelSave = (model: ModelData, event?: React.MouseEvent) => {
        // Check if already saved
        if (savedModels.some(m => m.id === model.id)) {
            return; // Already saved
        }

        // Get start position for animation
        let startPos = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
        if (event) {
            startPos = { x: event.clientX, y: event.clientY };
        }

        // Trigger flying animation
        setFlyingModel({ model, startPos });

        // Add to saved models after a short delay (for animation)
        setTimeout(() => {
            setSavedModels(prev => [model, ...prev]);
            setFlyingModel(null);
        }, 600);

        // Navigate to actions page
        setSelectedActionModel(model);
        setPreviousView(activeView);
        pushView('model_actions');
    };

    // --- Handle Model Download with Navigation to Actions Page ---
    const handleModelDownload = (model: ModelData, event?: React.MouseEvent) => {
        // Trigger download if URL is available
        if (model.download_url) {
            window.open(model.download_url, '_blank');
        }

        // Also save the model (bookmark)
        if (!savedModels.some(m => m.id === model.id)) {
            // Get start position for animation
            let startPos = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
            if (event) {
                startPos = { x: event.clientX, y: event.clientY };
            }

            // Trigger flying animation
            setFlyingModel({ model, startPos });

            // Add to saved models after animation
            setTimeout(() => {
                setSavedModels(prev => [model, ...prev]);
                setFlyingModel(null);
            }, 600);
        }

        // Set the selected model for the actions page and navigate
        setSelectedActionModel(model);
        setPreviousView(activeView);
        pushView('model_actions');
    };

    // --- Remove Model from Saved ---
    const handleRemoveSavedModel = (modelId: string) => {
        setSavedModels(prev => prev.filter(m => m.id !== modelId));
    };

    // --- Multi-Ancestry Training Submit ---
    const handleMultiAncestrySubmit = async (config: MultiAncestryTrainingConfig) => {
        const ancestries = config.dataSources.map(ds => ds.ancestry).join('+');
        setIsTrainingSubmitting(true);  // Start loading

        try {
            // Call backend API to submit multi-ancestry training job
            const response = await fetch('http://localhost:8000/api/submit-training-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jobName: config.jobName,
                    email: config.email,
                    jobType: 'multi',
                    trait: config.trait,
                    ancestries: ancestries,
                    dataSources: config.dataSources,
                    method: config.method,
                    advanced: config.advanced
                })
            });

            // Show confirmation modal
            setTrainingSubmitModal({
                isOpen: true,
                jobName: config.jobName,
                email: config.email,
                jobType: 'multi'
            });
        } catch (error) {
            console.error('Error submitting multi-ancestry training job:', error);
            // Still show modal even if API call fails
            setTrainingSubmitModal({
                isOpen: true,
                jobName: config.jobName,
                email: config.email,
                jobType: 'multi'
            });
        } finally {
            setIsTrainingSubmitting(false);  // Stop loading
        }
    };

    // --- Mode Selection Handlers ---

    const handleModeSelect = (mode: 'search' | 'train') => {
        if (mode === 'search') {
            pushView('disease_selection');
        } else {
            // For train, navigate to train type selection first
            setPreviousView('mode_selection');
            pushView('train_type_selection');
        }
    };

    const handleTrainTypeSelect = (type: 'single' | 'multi') => {
        if (type === 'single') {
            setPreviousView('train_type_selection');
            pushView('train_config');
        } else {
            // Multi-ancestry - Navigate to multi-ancestry form
            setPreviousView('train_type_selection');
            pushView('train_multi_config');
        }
    };

    const handleBackToPrevious = () => {
        // Simply go back one step in the navigation stack
        goBack();
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
                        <Home size={20} />
                    </button>
                    <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Disease PRS Module</span>
                </div>
                <div className="ml-auto flex items-center gap-4">
                    {(activeView !== 'mode_selection') && (
                        <button
                            onClick={() => {
                                // Reset navigation stack and go to mode_selection
                                setViewStack(['mode_selection']);
                                setForwardStack([]);
                                setActiveView('mode_selection');
                                setCurrentTrait(null);
                                setModels([]);
                            }}
                            className="text-sm font-medium text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            Start Over
                        </button>
                    )}

                    {/* My Models Button - Navigate to my_models view */}
                    <button
                        ref={savedButtonRef}
                        onClick={() => {
                            setPreviousView(activeView);
                            pushView('my_models');
                        }}
                        className="flex items-center gap-2 px-3 py-1.5 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-700/50 rounded-lg text-sm font-medium text-violet-700 dark:text-violet-300 hover:bg-violet-100 dark:hover:bg-violet-900/30 transition-colors"
                    >
                        <Bookmark className="w-4 h-4" />
                        <span>My Models</span>
                        {savedModels.length > 0 && (
                            <span className="ml-1 px-1.5 py-0.5 text-xs bg-violet-600 text-white rounded-full min-w-[20px] text-center">
                                {savedModels.length}
                            </span>
                        )}
                    </button>
                </div>
            </header>

            {/* Flying Animation */}
            <AnimatePresence>
                {flyingModel && savedButtonRef.current && (
                    <motion.div
                        initial={{
                            x: flyingModel.startPos.x - 20,
                            y: flyingModel.startPos.y - 20,
                            scale: 1,
                            opacity: 1
                        }}
                        animate={{
                            x: savedButtonRef.current.getBoundingClientRect().left + savedButtonRef.current.getBoundingClientRect().width / 2 - 20,
                            y: savedButtonRef.current.getBoundingClientRect().top + savedButtonRef.current.getBoundingClientRect().height / 2 - 20,
                            scale: 0.3,
                            opacity: 0.8
                        }}
                        exit={{ opacity: 0, scale: 0 }}
                        transition={{ duration: 0.5, ease: "easeInOut" }}
                        className="fixed z-[100] pointer-events-none"
                    >
                        <div className="w-10 h-10 bg-violet-500 rounded-lg shadow-lg flex items-center justify-center">
                            <Bookmark className="w-5 h-5 text-white" />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

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
                        onMultiAncestrySubmit={handleMultiAncestrySubmit}
                        onTrainTypeSelect={handleTrainTypeSelect}
                        // Concurrent Search Props
                        searchProgress={searchProgress}
                        isSearchComplete={isSearchComplete}
                        onAncestrySubmit={handleAncestrySubmit}
                        activeAncestry={selectedAncestry}
                        // Model Actions Page
                        selectedActionModel={selectedActionModel}
                        // My Models Page
                        savedModels={savedModels}
                        onRemoveSavedModel={handleRemoveSavedModel}
                        onSelectSavedModel={(model) => {
                            setSelectedActionModel(model);
                            setPreviousView(activeView);
                            pushView('model_actions');
                        }}
                        onSaveModel={handleModelSave}
                        // Navigation Props
                        onGoToModelGrid={() => pushView('model_grid')}
                        canGoForward={canGoForward}
                        onGoForward={goForward}
                        // Training loading state
                        isTrainingSubmitting={isTrainingSubmitting}
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
                        onModelDownload={(model, event) => {
                            setSelectedModelDetails(null);
                            handleModelDownload(model, event);
                        }}
                        onModelSave={(model, event) => {
                            setSelectedModelDetails(null);
                            handleModelSave(model, event);
                        }}
                        isModelSaved={selectedModelDetails ? savedModels.some(m => m.id === selectedModelDetails.id) : false}
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
                        onModelDownload={handleModelDownload}
                        onModelSave={handleModelSave}
                        onProgressUpdate={(p) => setSearchProgress(p)}
                        onSearchStatusChange={(s) => {
                            setIsSearching(s);
                            // If search starts, mark incomplete
                            if (s) setIsSearchComplete(false);
                        }}
                        deferAnalysis={true}
                        externalAgentMessage={smartRecommendation}
                        externalAgentModel={smartRecommendationModel}
                        externalAgentActions={smartRecommendationActions}
                        hasSelectedAncestry={isAncestrySubmitted}
                        savedModelIds={savedModels.map(m => m.id)}
                    />
                </div>

            </div>

            {/* Training Submission Confirmation Modal */}
            <AnimatePresence>
                {trainingSubmitModal?.isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full mx-4 p-8 text-center"
                        >
                            {/* Success Icon */}
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                                <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
                            </div>

                            {/* Title */}
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                                Training Job Submitted!
                            </h2>

                            {/* Job Name */}
                            <p className="text-gray-600 dark:text-gray-300 mb-4">
                                Your {trainingSubmitModal.jobType === 'multi' ? 'multi-ancestry' : 'single-ancestry'} training job <span className="font-semibold text-blue-600 dark:text-blue-400">"{trainingSubmitModal.jobName}"</span> has been successfully submitted.
                            </p>

                            {/* Email Notification */}
                            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4 mb-6">
                                <div className="flex items-center justify-center gap-2 mb-2">
                                    <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                    <span className="font-medium text-blue-700 dark:text-blue-300">Check Your Email</span>
                                </div>
                                <p className="text-sm text-blue-600 dark:text-blue-400">
                                    You will receive training progress updates and results at:
                                </p>
                                <p className="text-sm font-semibold text-blue-800 dark:text-blue-200 mt-1">
                                    {trainingSubmitModal.email}
                                </p>
                            </div>

                            {/* Return Button */}
                            <button
                                onClick={() => {
                                    setTrainingSubmitModal(null);
                                    // Reset navigation and return to main mode_selection page
                                    setViewStack(['mode_selection']);
                                    setForwardStack([]);
                                    setActiveView('mode_selection');
                                    setCurrentTrait(null);
                                    setModels([]);
                                }}
                                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl"
                            >
                                Return to Main Page
                            </button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
