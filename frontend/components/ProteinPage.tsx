"use client";

import { useState, useEffect, useRef } from "react";
import ChatInterface, { StructuredResponse } from "./ChatInterface";
import CanvasArea, { ViewType } from "./CanvasArea";
import { ModelData } from "./ModelCard";
import ProteinDetailModal from "./ProteinDetailModal";
import ProteinSearchSummary from "./ProteinSearchSummary";
import { Home, Dna, Bookmark, Search, Database, ArrowLeft, User, Users, Activity, SendHorizontal, Loader2, Download } from "lucide-react";
import TrainingConfigForm, { TrainingConfig } from "./TrainingConfigForm";
import MultiAncestryTrainingForm, { MultiAncestryTrainingConfig } from "./MultiAncestryTrainingForm";
import { AnimatePresence, motion } from "framer-motion";
import { ProgressBar } from "./ProgressBar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChatBubble } from "@/components/chat/ChatBubble";
import ProteinTargetGrid from "./ProteinTargetGrid";

interface ProteinPageProps {
    onBack: () => void;
}

// Extended ModelData for OmicsPred protein-specific fields
interface ProteinModelData extends ModelData {
    protein_name?: string;
    gene_name?: string;
    gene_ensembl_id?: string;
    uniprot_id?: string;
    protein_synonyms?: string[];
    protein_description?: string;
    platform?: string;
    dataset_name?: string;
    dataset_id?: string;
    dev_cohorts?: string;
    tissue?: string;
    dev_sample_size?: number;
    eval_sample_size?: number;
    ancestry_dev?: Record<string, unknown>;
    ancestry_eval?: Record<string, unknown>;
    performance_data?: Record<string, { estimate: number }>;
    genes?: Array<{
        name: string;
        external_id?: string;
        descriptions?: string[];
        external_id_source?: string;
        biotype?: string;
    }>;
    proteins?: Array<{
        name: string;
        external_id?: string;
        external_id_source?: string;
        synonyms?: string[];
        descriptions?: string[];
    }>;
}

export default function ProteinPage({ onBack }: ProteinPageProps) {
    // Global State - INITIALIZED TO 'protein_mode_selection'
    const [activeView, setActiveView] = useState<ViewType>('protein_mode_selection');
    const [previousView, setPreviousView] = useState<ViewType>('protein_mode_selection');
    const [currentQuery, setCurrentQuery] = useState<string | null>(null);
    const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);

    // Navigation History - Simple Stack
    const [viewStack, setViewStack] = useState<ViewType[]>(['protein_mode_selection']);
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
            if (activeView === 'protein_grid') {
                setIsAncestrySubmitted(false);
            } else if (activeView === 'protein_search_summary') {
                setIsSearchComplete(false);
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

    // Data State
    const [models, setModels] = useState<ProteinModelData[]>([]);

    // Active Modals State
    const [selectedModelDetails, setSelectedModelDetails] = useState<ProteinModelData | null>(null);

    // External Trigger Mechanism
    const [externalTriggerDetails, setExternalTriggerDetails] = useState<string | null>(null);

    // Search State
    const [isSearching, setIsSearching] = useState(false);
    const [searchProgress, setSearchProgress] = useState<{ status: string; total: number; fetched: number; current_action: string } | null>(null);
    const [isSearchComplete, setIsSearchComplete] = useState(false);

    // Ancestry Selection State (matching Disease flow)
    const [selectedAncestry, setSelectedAncestry] = useState<string[]>([]);
    const [isAncestrySubmitted, setIsAncestrySubmitted] = useState(false);

    // Smart Recommendation State
    const [smartRecommendation, setSmartRecommendation] = useState<string | null>(null);
    const [smartRecommendationModel, setSmartRecommendationModel] = useState<ProteinModelData | null>(null);
    const [smartRecommendationActions, setSmartRecommendationActions] = useState<string[] | null>(null);

    const triggerChat = (msg: string) => {
        setExternalTriggerDetails(msg);
        setTimeout(() => setExternalTriggerDetails(null), 100);
    }

    // --- Handlers ---

    // --- Mode Selection Handler ---
    const handleModeSelect = (mode: 'search' | 'train') => {
        if (mode === 'search') {
            pushView('protein_search');
        } else {
            // For train, navigate to train type selection first
            setPreviousView('protein_mode_selection');
            pushView('protein_train_type_selection');
        }
    };

    // --- Training Handlers ---
    const handleTrainTypeSelect = (type: 'single' | 'multi') => {
        if (type === 'single') {
            setPreviousView('protein_train_type_selection');
            pushView('protein_train_config');
        } else {
            // Multi-ancestry - Navigate to multi-ancestry form
            setPreviousView('protein_train_type_selection');
            pushView('protein_train_multi_config');
        }
    };

    const handleTrainingSubmit = (config: TrainingConfig) => {
        // Build prompt for agent to submit to PennPRS API (same as disease training)
        let prompt = `I want to train a new model for ${config.trait} (Ancestry: ${config.ancestry}) named '${config.jobName}'.`;
        prompt += `\nEmail: ${config.email}`;
        prompt += `\nJob Type: ${config.jobType}`;
        prompt += `\nMethodology Category: ${config.methodologyCategory}`;
        prompt += `\nMethods: ${config.methods.join(', ')}`;
        if (config.ensemble) prompt += `\nEnsemble: Enabled`;
        if (config.dataSourceType === 'public') {
            prompt += `\nData Source: Public ${config.database || "GWAS Catalog"} (ID: ${config.gwasId || "Auto"})`;
        } else {
            prompt += `\nData Source: User Upload (${config.uploadedFileName})`;
            prompt += `\n[SYSTEM NOTE: File content handling simulated for agent prototype]`;
        }
        prompt += `\nTrait Type: ${config.traitType}, Sample Size: ${config.sampleSize}`;
        if (config.advanced) {
            prompt += `\nHyperparams: kb=${config.advanced.kb}, r2=${config.advanced.r2}, pval_thr=${config.advanced.pval_thr}`;
        }

        triggerChat(prompt);
        // Navigate back to mode selection after submit
        setViewStack(['protein_mode_selection']);
        setForwardStack([]);
        setActiveView('protein_mode_selection');
    };

    const handleMultiAncestrySubmit = (config: MultiAncestryTrainingConfig) => {
        // Build prompt for agent to submit to PennPRS API (same as disease multi-ancestry)
        const ancestries = config.dataSources.map(ds => ds.ancestry).join('+');
        let prompt = `I want to train a Multi-Ancestry PRS model named '${config.jobName}' for trait '${config.trait}'.`;
        prompt += `\nEmail: ${config.email}`;
        prompt += `\nJob Type: multi`;
        prompt += `\nMethodology: PROSPER-pseudo`;
        prompt += `\nAncestries: ${ancestries} (${config.dataSources.length} populations)`;

        config.dataSources.forEach((ds, idx) => {
            prompt += `\n\nAncestry ${idx + 1} (${ds.ancestry}):`;
            if (ds.dataSourceType === 'public') {
                prompt += `\n  Data Source: Public ${ds.database === 'finngen' ? 'FinnGen' : 'GWAS Catalog'} (ID: ${ds.gwasId})`;
            } else {
                prompt += `\n  Data Source: User Upload (${ds.uploadedFileName})`;
            }
            prompt += `\n  Trait Type: ${ds.traitType}, Sample Size: ${ds.sampleSize}`;
        });

        if (config.advanced) {
            prompt += `\n\nAdvanced PROSPER Parameters:`;
            prompt += ` nlambda=${config.advanced.nlambda}`;
            prompt += `, ndelta=${config.advanced.ndelta}`;
            prompt += `, lambda_min_ratio=${config.advanced.lambda_min_ratio}`;
        }

        triggerChat(prompt);
        // Navigate back to mode selection after submit
        setViewStack(['protein_mode_selection']);
        setForwardStack([]);
        setActiveView('protein_mode_selection');
    };

    const handleProteinSearch = (query: string) => {
        // RESET States (matching Disease flow)
        setCurrentQuery(query);
        setSelectedPlatform(null);
        setModels([]);
        setIsSearching(true);
        setIsSearchComplete(false);
        setIsAncestrySubmitted(false);
        setSearchProgress(null);
        setSelectedAncestry([]);
        setSmartRecommendation(null);
        setSmartRecommendationModel(null);
        setSmartRecommendationActions(null);

        // TRIGGER Search
        const searchMsg = `I want to search for genetic scores for ${query}`;
        triggerChat(searchMsg);
    };

    // Handle ancestry submit (matching Disease flow)
    const handleAncestrySubmit = (ancestries: string[]) => {
        setIsAncestrySubmitted(true);
        setSelectedAncestry(ancestries);
        // Effect will handle transition to grid
    };

    // --- Effects ---

    // --- Effects (Empty - transitions handled manually in handleChatResponse or ancestry submit) ---


    // Effect 2: Handle transition from search_summary to grid when ancestry is submitted
    useEffect(() => {
        if (activeView === 'protein_search_summary' && isAncestrySubmitted) {
            // GENERATE SMART RECOMMENDATION (matching Disease flow exactly)
            const ancestryMap: Record<string, string> = {
                'EUR': 'European', 'AFR': 'African', 'EAS': 'East Asian',
                'SAS': 'South Asian', 'AMR': 'Hispanic', 'MIX': 'Others'
            };

            const relevantModels = models.filter(m => {
                if (m.source === "User Trained" || m.source === "PennPRS (Custom)" || m.source === "User Upload") return true;

                // If NO ancestry selected, show ALL models
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

            // Find Best Model (Max R2 for protein models)
            if (relevantModels.length > 0) {
                const best = relevantModels.reduce((prev, current) => {
                    const prevR2 = prev.metrics?.R2 || 0;
                    const currR2 = current.metrics?.R2 || 0;
                    return prevR2 > currR2 ? prev : current;
                }, relevantModels[0]);

                let ancLabel = "All Ancestries";
                if (selectedAncestry.length > 0) {
                    ancLabel = selectedAncestry.map(a => ancestryMap[a] || a).join(", ");
                }

                // EXACT BACKEND FORMAT RESTORATION
                let msg = `I found **${relevantModels.length}** proteomics scores for **'${currentQuery}'** `;
                if (selectedAncestry.length > 0) {
                    msg += `matching your ancestry criteria (**${ancLabel}**).\n\n`;
                } else {
                    msg += `across all ancestries.\n\n`;
                }

                msg += `The score with the highest R² is **${best.name}** (ID: ${best.id}).\n`;
                msg += `I've displayed the best score card below. You can view detailed information for this result and others in the **Canvas** panel.`;

                setSmartRecommendation(msg);
                setSmartRecommendationModel(best);
                setSmartRecommendationActions([
                    "Download this Score",
                    "Train Custom Model"
                ]);
            } else {
                const ancLabel = selectedAncestry.map(a => ancestryMap[a] || a).join(", ");
                setSmartRecommendation(`I searched for scores matching **${ancLabel}** but found no direct matches in the training data.\n\nYou can browse the full list or try searching for a different gene/protein.`);
                setSmartRecommendationModel(null);
                setSmartRecommendationActions(["Search Another Gene/Protein"]);
            }

            pushView('protein_grid');
        }
    }, [activeView, isAncestrySubmitted, models, selectedAncestry, currentQuery]);

    const handleChatResponse = (response: StructuredResponse) => {
        if (response.type === 'protein_grid' || response.type === 'model_grid') {
            setModels((response.models || []) as ProteinModelData[]);
            setIsSearchComplete(true);
            setIsSearching(false);
            // Transition to search summary view to show summary with ancestry filtering
            pushView('protein_search_summary');
        } else if (response.type === 'protein_detail') {
            // Handle detail view response
            if (response.best_model) {
                setSelectedModelDetails(response.best_model as ProteinModelData);
            }
        }
    };

    const handleSelectModel = (modelId: string) => {
        const model = models.find(m => m.id === modelId);
        if (model) {
            setSelectedModelDetails(model);
        }
    };

    const handleViewDetails = (model: ModelData) => {
        // Model data is now fully pre-fetched by the backend workflow
        setSelectedModelDetails(model as ProteinModelData);
    };

    const handleDownstreamAction = (action: string) => {
        if (action.includes("Download")) {
            // Trigger download
            const model = selectedModelDetails;
            if (model?.download_url) {
                window.open(model.download_url, '_blank');
            } else {
                triggerChat(`Download score ${model?.id || 'unknown'}`);
            }
        } else if (action.includes("Browse")) {
            // Go back to protein search view
            goBack();
        } else {
            triggerChat(`I want to ${action.toLowerCase()}`);
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
                    <Dna className="text-violet-500" size={24} />
                    <span className="bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">Proteomics PRS Models</span>
                </div>
                <div className="ml-auto flex items-center gap-4">
                    {(activeView !== 'protein_mode_selection') && (
                        <button
                            onClick={() => {
                                // Reset navigation stack and go to mode_selection
                                setViewStack(['protein_mode_selection']);
                                setForwardStack([]);
                                setActiveView('protein_mode_selection');
                                setCurrentQuery(null);
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
                    <ProteinCanvasArea
                        view={activeView}
                        query={currentQuery}
                        models={models}
                        onSearch={handleProteinSearch}
                        onSelectModel={handleSelectModel}
                        onViewDetails={handleViewDetails}
                        onBackToSelection={handleBackToPrevious}
                        searchProgress={searchProgress}
                        isSearching={isSearching}
                        isSearchComplete={isSearchComplete}
                        onModeSelect={handleModeSelect}
                        onTrainTypeSelect={handleTrainTypeSelect}
                        onTrainingSubmit={handleTrainingSubmit}
                        onMultiAncestrySubmit={handleMultiAncestrySubmit}
                        onAncestrySubmit={handleAncestrySubmit}
                        activeAncestry={selectedAncestry}
                    />

                    {/* Protein Detail Modal */}
                    <ProteinDetailModal
                        model={selectedModelDetails as any}
                        isOpen={!!selectedModelDetails}
                        onClose={() => setSelectedModelDetails(null)}
                    />
                </div>

                {/* Right: Chat Interface (1/3) */}
                <div className="flex-1 min-w-[320px] bg-white dark:bg-gray-900 border-l border-gray-100 dark:border-gray-800 shadow-xl z-20">
                    <ProteinChatInterface
                        onResponse={handleChatResponse}
                        currentQuery={currentQuery}
                        externalTrigger={externalTriggerDetails}
                        onViewDetails={handleViewDetails}
                        onDownstreamAction={handleDownstreamAction}
                        onProgressUpdate={(p) => setSearchProgress(p)}
                        onSearchStatusChange={(s) => {
                            setIsSearching(s);
                            if (s) setIsSearchComplete(false);
                        }}
                        externalAgentMessage={smartRecommendation}
                        externalAgentModel={smartRecommendationModel}
                        externalAgentActions={smartRecommendationActions}
                    />
                </div>

            </div>
        </div>
    );
}

// === Protein Canvas Area Component ===

interface ProteinCanvasAreaProps {
    view: ViewType;
    query: string | null;
    models: ProteinModelData[];
    onSearch: (query: string) => void;
    onSelectModel: (modelId: string) => void;
    onViewDetails: (model: ModelData) => void;
    onBackToSelection: () => void;
    searchProgress: { status: string; total: number; fetched: number; current_action: string } | null;
    isSearching: boolean;
    isSearchComplete: boolean;
    onModeSelect: (mode: 'search' | 'train') => void;
    onTrainTypeSelect: (type: 'single' | 'multi') => void;
    onTrainingSubmit: (config: TrainingConfig) => void;
    onMultiAncestrySubmit: (config: MultiAncestryTrainingConfig) => void;
    onAncestrySubmit: (ancestries: string[]) => void;
    activeAncestry: string[];
}

function ProteinCanvasArea({
    view,
    query,
    models,
    onSearch,
    onSelectModel,
    onViewDetails,
    onBackToSelection,
    searchProgress,
    isSearching,
    isSearchComplete,
    onModeSelect,
    onTrainTypeSelect,
    onTrainingSubmit,
    onMultiAncestrySubmit,
    onAncestrySubmit,
    activeAncestry
}: ProteinCanvasAreaProps) {
    const [searchInput, setSearchInput] = useState("");

    // Platform cards data
    const platforms = [
        {
            id: "Olink",
            name: "Olink Explore",
            description: "High-throughput proximity extension assay (PEA) for protein quantification",
            proteins: "~3000 proteins",
            color: "from-blue-500 to-blue-600"
        },
        {
            id: "Somalogic",
            name: "SomaScan",
            description: "Aptamer-based proteomic platform for broad protein coverage",
            proteins: "~7000 proteins",
            color: "from-purple-500 to-purple-600"
        }
    ];

    // View: Mode Selection (Start)
    if (view === 'protein_mode_selection') {
        return (
            <div className="h-full w-full bg-gray-50/50 dark:bg-gray-900/50 overflow-y-auto p-4 sm:p-6">
                <div className="flex flex-col items-center justify-center min-h-[70vh] animate-in fade-in zoom-in-95 duration-500">
                    <div className="text-center space-y-4 mb-12">
                        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-gray-900 dark:text-white">
                            Proteomics PRS Module
                        </h1>
                        <p className="text-lg text-gray-500 dark:text-gray-400 max-w-lg mx-auto">
                            Choose how you want to proceed with your Proteomics Polygenic Risk Score analysis.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl px-4">
                        {/* Search Card */}
                        <button
                            onClick={() => onModeSelect('search')}
                            className="group relative flex flex-col items-center p-10 bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 text-center"
                        >
                            <div className="mb-6 p-6 bg-violet-50 dark:bg-violet-900/30 rounded-full group-hover:bg-violet-100 dark:group-hover:bg-violet-900/50 transition-colors">
                                <Search className="w-12 h-12 text-violet-600 dark:text-violet-400" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Search Existing Models</h2>
                            <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                                Browse pre-trained proteomics scores from OmicsPred.
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
            </div>
        );
    }

    // View: Training Type Selection
    if (view === 'protein_train_type_selection') {
        return (
            <div className="h-full w-full bg-gray-50/50 dark:bg-gray-900/50 overflow-y-auto p-4 sm:p-6">
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
                            onClick={() => onTrainTypeSelect('single')}
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
                            onClick={() => onTrainTypeSelect('multi')}
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
            </div>
        );
    }

    // View: Training Config (Single-Ancestry)
    if (view === 'protein_train_config') {
        return (
            <div className="h-full w-full bg-gray-50/50 dark:bg-gray-900/50 overflow-y-auto p-4 sm:p-6">
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
                        onCancel={onBackToSelection}
                    />
                </div>
            </div>
        );
    }

    // View: Multi-Ancestry Training Config
    if (view === 'protein_train_multi_config') {
        return (
            <div className="h-full w-full bg-gray-50/50 dark:bg-gray-900/50 overflow-y-auto p-4 sm:p-6">
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
                        onSubmit={onMultiAncestrySubmit}
                        onCancel={onBackToSelection}
                    />
                </div>
            </div>
        );
    }

    // View: Protein Search
    if (view === 'protein_search') {
        return (
            <div className="h-full flex flex-col p-8 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 overflow-hidden relative">

                {/* Loading Overlay (Disease-style) */}
                {isSearching && !isSearchComplete && (
                    <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center animate-in fade-in duration-300">
                        <div className="text-center space-y-6 max-w-md">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Searching OmicsPred...</h2>
                                <p className="text-gray-500 dark:text-gray-400">
                                    Retrieving molecular data and PRS models for <span className="font-semibold text-violet-600">"{query || "your selection"}"</span>
                                </p>
                            </div>
                            {searchProgress ? (
                                <ProgressBar
                                    status={searchProgress.status}
                                    total={searchProgress.total}
                                    fetched={searchProgress.fetched}
                                    currentAction={searchProgress.current_action}
                                />
                            ) : (
                                <div className="flex justify-center py-4">
                                    <div className="animate-spin rounded-full h-10 w-10 border-4 border-violet-500 border-t-transparent"></div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Back Button */}
                <div className="mb-4 shrink-0">
                    <button
                        onClick={onBackToSelection}
                        className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/50 dark:hover:bg-gray-800"
                    >
                        <ArrowLeft size={18} />
                        <span className="text-sm font-medium">Back</span>
                    </button>
                </div>

                <div className="flex-1 flex flex-col items-center max-w-5xl mx-auto w-full overflow-y-auto">
                    {/* Search Header */}
                    <div className="text-center mb-8 shrink-0">
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent mb-2">
                            Select Target Biomarker
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400">
                            Search for any gene or protein using Open Targets Platform
                        </p>
                    </div>

                    {/* Open Targets Search Grid */}
                    <ProteinTargetGrid onSelect={onSearch} />
                </div>
            </div>
        );
    }

    // View: Protein Search Summary (NEW - matching Disease flow)
    if (view === 'protein_search_summary') {
        return (
            <div className="h-full overflow-y-auto bg-gray-50/50 dark:bg-gray-900/50 p-6">
                <div className="max-w-4xl mx-auto">
                    {/* Back Button */}
                    <div className="mb-4">
                        <button
                            onClick={onBackToSelection}
                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/50 dark:hover:bg-gray-800"
                        >
                            <ArrowLeft size={18} />
                            <span className="text-sm font-medium">Back to Search</span>
                        </button>
                    </div>
                </div>
                <ProteinSearchSummary
                    trait={query || "Protein Search"}
                    models={models as ProteinModelData[]}
                    onAncestrySubmit={onAncestrySubmit}
                    activeAncestry={activeAncestry}
                />
            </div>
        );
    }

    if (view === 'protein_grid') {
        return (
            <div className="h-full flex flex-col overflow-hidden">
                {/* Header Bar */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={onBackToSelection}
                            className="text-sm text-gray-500 hover:text-gray-800 dark:hover:text-white"
                        >
                            ← Back to Search
                        </button>
                        <span className="text-gray-300 dark:text-gray-600">|</span>
                        <span className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                            {query ? `Results for "${query}"` : "Protein Scores"}
                        </span>
                        <span className="px-3 py-1 bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-400 rounded-full text-sm">
                            {models.length} scores
                        </span>
                    </div>
                </div>

                {/* Loading State */}
                {!isSearchComplete && (
                    <div className="flex-1 flex flex-col items-center justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-violet-500 border-t-transparent mb-4"></div>
                        <p className="text-gray-600 dark:text-gray-400">
                            {searchProgress?.current_action || "Searching OmicsPred..."}
                        </p>
                        {searchProgress && searchProgress.total > 0 && (
                            <p className="text-sm text-gray-500 mt-2">
                                Fetched {searchProgress.fetched} of {searchProgress.total}
                            </p>
                        )}
                    </div>
                )}

                {/* Grid */}
                {isSearchComplete && (
                    <div className="flex-1 overflow-auto p-6">
                        {models.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center">
                                <Dna className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
                                <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">No Scores Found</h3>
                                <p className="text-gray-500 dark:text-gray-400 max-w-md">
                                    Try a different protein name or browse by platform to find genetic scores.
                                </p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {models.map((model) => (
                                    <ProteinScoreCard
                                        key={model.id}
                                        model={model}
                                        onViewDetails={() => onViewDetails(model)}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    }

    // Default fallback
    return (
        <div className="h-full flex items-center justify-center">
            <p className="text-gray-500">View not implemented: {view}</p>
        </div>
    );
}

// === Protein Score Card Component ===

interface ProteinScoreCardProps {
    model: ProteinModelData;
    onViewDetails: () => void;
}

function ProteinScoreCard({ model, onViewDetails }: ProteinScoreCardProps) {
    const metrics = model.metrics || {};

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all p-4 flex flex-col h-[320px] w-full group overflow-hidden">
            {/* Header: ID & Platform */}
            <div className="flex justify-between items-start mb-2">
                <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-violet-600 dark:text-violet-400">
                            {model.id}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded border bg-violet-50 text-violet-600 border-violet-100 dark:bg-violet-900/20 dark:text-violet-300 dark:border-violet-800">
                            OmicsPred
                        </span>
                    </div>
                </div>
                {model.platform && (
                    <span className={`px-2 py-0.5 text-[10px] font-semibold rounded-full border ${model.platform.includes('Olink')
                        ? 'bg-indigo-50 text-indigo-700 border-indigo-100 dark:bg-indigo-900/30 dark:text-indigo-400'
                        : 'bg-purple-50 text-purple-700 border-purple-100 dark:bg-purple-900/30 dark:text-purple-400'
                        }`}>
                        {model.platform}
                    </span>
                )}
            </div>

            {/* Title & Protein Info */}
            <div className="mb-3 cursor-pointer" onClick={onViewDetails}>
                <h3 className="font-bold text-gray-900 dark:text-white line-clamp-1 group-hover:text-violet-600 transition-colors" title={model.protein_name || model.name}>
                    {model.protein_name || model.name}
                </h3>
                <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    <Dna className="w-3.5 h-3.5 text-violet-400" />
                    <span className="truncate">{model.gene_name || "N/A"}</span>
                    {model.uniprot_id && (
                        <span className="text-[10px] text-gray-400 font-mono">({model.uniprot_id})</span>
                    )}
                </div>
            </div>

            {/* Detail Metadata Grid */}
            <div className="flex-1 space-y-1.5 mb-4 overflow-hidden">
                <div className="flex flex-col gap-1">
                    {/* Method */}
                    <div className="flex items-center gap-2 text-[11px]">
                        <span className="text-gray-400 font-medium min-w-[55px]">Method:</span>
                        <span className="px-1.5 py-0.5 rounded bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-100 dark:border-gray-700 truncate flex-1">
                            {model.method || "N/A"}
                        </span>
                    </div>
                    {/* Ancestry */}
                    <div className="flex items-center gap-2 text-[11px]">
                        <span className="text-gray-400 font-medium min-w-[55px]">Ancestry:</span>
                        <span className="px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-800 truncate flex-1">
                            {model.ancestry || "EUR"}
                        </span>
                    </div>
                    {/* Samples */}
                    <div className="flex items-center gap-2 text-[11px]">
                        <span className="text-gray-400 font-medium min-w-[55px]">Samples:</span>
                        <span className="px-1.5 py-0.5 rounded bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-100 dark:border-green-800 truncate flex-1">
                            {model.sample_size ? model.sample_size.toLocaleString() : "N/A"}
                        </span>
                    </div>
                    {/* Tissue */}
                    <div className="flex items-center gap-2 text-[11px]">
                        <span className="text-gray-400 font-medium min-w-[55px]">Tissue:</span>
                        <span className="px-1.5 py-0.5 rounded bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border border-amber-100 dark:border-amber-800 truncate flex-1" title={model.tissue}>
                            {model.tissue || "N/A"}
                        </span>
                    </div>
                </div>
            </div>

            {/* Performance Metrics Stats */}
            <div className="grid grid-cols-3 gap-1 py-2 border-t border-gray-100 dark:border-gray-800 mb-3">
                <div className="text-center border-r border-gray-100 dark:border-gray-800">
                    <div className="text-[8px] text-gray-400 font-medium uppercase tracking-wider">R²</div>
                    <div className="font-mono font-bold text-sm text-violet-600 dark:text-violet-400">
                        {metrics.R2 && typeof metrics.R2 === 'number' ? metrics.R2.toFixed(3) : "N/A"}
                    </div>
                </div>
                <div className="text-center border-r border-gray-100 dark:border-gray-800">
                    <div className="text-[8px] text-gray-400 font-medium uppercase tracking-wider">Rho</div>
                    <div className="font-mono font-bold text-sm text-indigo-600 dark:text-indigo-400">
                        {metrics.Rho && typeof metrics.Rho === 'number' ? metrics.Rho.toFixed(3) : "0.000"}
                    </div>
                </div>
                <div className="text-center">
                    <div className="text-[8px] text-gray-400 font-medium uppercase tracking-wider">Variants</div>
                    <div className="font-mono font-bold text-sm text-gray-700 dark:text-gray-300">
                        {model.num_variants ? (model.num_variants > 1000 ? (model.num_variants / 1000).toFixed(1) + 'k' : model.num_variants) : 'N/A'}
                    </div>
                </div>
            </div>

            {/* Actions Buttons */}
            <div className="flex gap-2">
                <button
                    onClick={onViewDetails}
                    className="flex-1 px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                    View Details
                </button>
            </div>
        </div>
    );
}
// ProteinChatCard definition removed as it is no longer used

// === Protein Chat Interface ===

interface ProteinChatInterfaceProps {
    onResponse: (response: StructuredResponse) => void;
    currentQuery: string | null;
    externalTrigger: string | null;
    onViewDetails: (model: ModelData) => void;
    onDownstreamAction: (action: string) => void;
    onProgressUpdate: (progress: { status: string; total: number; fetched: number; current_action: string } | null) => void;
    onSearchStatusChange: (isSearching: boolean) => void;
    externalAgentMessage: string | null;
    externalAgentModel: ModelData | null;
    externalAgentActions: string[] | null;
}



interface Message {
    role: 'user' | 'agent';
    content: string;
    id: string;
    modelCard?: ModelData;
    actions?: string[];
    isProgress?: boolean;
    progressData?: { status: string; total: number; fetched: number; current_action: string } | null;
    footer?: string;
    isWaitingForAncestry?: boolean;
}

function ProteinChatInterface({
    onResponse,
    currentQuery,
    externalTrigger,
    onViewDetails,
    onDownstreamAction,
    onProgressUpdate,
    onSearchStatusChange,
    externalAgentMessage,
    externalAgentModel,
    externalAgentActions
}: ProteinChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'agent',
            content: "Welcome to PennPRS Lab! I'm your research assistant — here to help you navigate and leverage this platform. I can answer questions, design research workflows, and analyze results. Let me know what you need help with! To begin, you can type in the chat box or select a protein of interest from the canvas, and I'll recommend the most suitable proteomics PRS models for you.",
            id: 'welcome'
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Handle external triggers
    useEffect(() => {
        if (externalTrigger) {
            handleSend(externalTrigger);
        }
    }, [externalTrigger]);

    // Handle external agent message (for smart recommendations)
    useEffect(() => {
        if (externalAgentMessage) {
            const newMsg: Message = {
                role: 'agent',
                content: externalAgentMessage,
                id: `agent-${Date.now()}`,
                modelCard: externalAgentModel || undefined,
                actions: externalAgentActions || undefined
            };
            setMessages(prev => [...prev, newMsg]);
        }
    }, [externalAgentMessage, externalAgentModel, externalAgentActions]);

    const currentProgressMsgId = useRef<string | null>(null);

    const handleSend = async (text: string = input) => {
        if (!text.trim() || isLoading) return;

        const userMsg: Message = { role: 'user', content: text, id: `user-${Date.now()}` };

        // Add progress message (Disease-style)
        const progressId = `progress-${Date.now()}`;
        const progressMsg: Message = {
            role: 'agent',
            content: "Searching for proteomics PRS models...",
            id: progressId,
            isProgress: true,
            // progressData remove from here
        };
        currentProgressMsgId.current = progressId;

        setMessages(prev => [...prev, userMsg, progressMsg]);
        setInput("");
        setIsLoading(true);
        onSearchStatusChange(true);

        const requestId = crypto.randomUUID();

        // Start polling for progress
        const pollInterval = setInterval(async () => {
            try {
                const progressRes = await fetch(`http://localhost:8000/agent/search_progress/${requestId}`);
                if (progressRes.ok) {
                    const progressData = await progressRes.json();
                    if (progressData.status !== "unknown") {
                        onProgressUpdate(progressData); // Keep updating Canvas progress bar
                        // Note: We do NOT update the Chat message with progress data anymore
                    }
                }
            } catch (e) {
                // Ignore polling errors
            }
        }, 500);

        try {
            const res = await fetch("http://localhost:8000/protein/invoke", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, request_id: requestId })
            });

            clearInterval(pollInterval);
            onSearchStatusChange(false);
            onProgressUpdate(null);

            if (!res.ok) throw new Error("API Error");

            const data = await res.json();
            const sr = data.full_state?.structured_response;

            // Prepare Summary (Disease-style summary in Chat)
            if (sr && (sr.type === 'protein_grid' || sr.type === 'model_grid')) {
                const resultsCount = sr.models?.length || 0;
                const ancestries = new Set();
                const cohorts = new Set();
                const models = sr.models || [];

                models.forEach((m: any) => {
                    if (m.ancestry) m.ancestry.split(',').forEach((a: string) => ancestries.add(a.trim().toLowerCase()));
                    if (m.dev_cohorts) m.dev_cohorts.split(',').forEach((c: string) => cohorts.add(c.trim()));
                });

                const summaryContent = `### 🔍 Analysis Complete

I have analyzed the available PRS landscape for **${currentQuery || text}**. Here are the key findings from OmicsPred:

*   **Total Models Found**: \`${resultsCount}\` proteomics clinical scores
*   **Population Diversity**: \`${ancestries.size}\` distinct ancestry groups
*   **Research Depth**: Evaluated across \`${cohorts.size}\` unique cohorts

---

**Guidance**: To refine these results for your specific study, please **select a target ancestry** from the filter panel on the left. This will allow me to recommend the most accurate model for your population.`;

                const finalProgress = {
                    status: 'completed',
                    total: resultsCount,
                    fetched: resultsCount,
                    current_action: 'Search Complete'
                };

                setMessages(prev => prev.map(m => {
                    if (m.id === progressId) {
                        return {
                            ...m,
                            content: summaryContent,
                            isProgress: true
                        };
                    }
                    return m;
                }));

                onResponse(sr);
            } else {
                // Handle non-grid responses
                setMessages(prev => {
                    const filtered = prev.filter(m => m.id !== progressId);
                    const agentMsg: Message = {
                        role: 'agent',
                        content: data.response || "Task completed successfully.",
                        id: `agent-${Date.now()}`,
                        modelCard: sr?.best_model,
                        actions: sr?.actions
                    };
                    return [...filtered, agentMsg];
                });

                if (sr) onResponse(sr);
            }

        } catch (error) {
            clearInterval(pollInterval);
            onSearchStatusChange(false);
            console.error("Protein agent error:", error);

            setMessages(prev => prev.map(m => {
                if (m.id === progressId) {
                    return { ...m, content: "Sorry, I encountered an error during the search. Please try again." };
                }
                return m;
            }));
        }

        setIsLoading(false);
        currentProgressMsgId.current = null;
    };

    return (
        <div className="flex flex-col h-full">
            {/* Chat Header */}
            <div className="p-4 border-b bg-white dark:bg-gray-900">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <Dna className="text-violet-500" size={20} />
                    PennPRS Agent
                </h2>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <ChatBubble
                                role={msg.role}
                                content={msg.content}
                                actions={msg.actions}
                                // Pass ProteinScoreCard as customCard for consistent styling in chat
                                customCard={
                                    msg.role === 'agent' && msg.modelCard && !msg.isProgress ? (
                                        <ProteinScoreCard
                                            model={msg.modelCard as ProteinModelData}
                                            onViewDetails={() => onViewDetails(msg.modelCard!)}
                                        />
                                    ) : undefined
                                }
                                // No progress passed to ChatBubble to avoid rendering it
                                footer={msg.footer}
                                onViewDetails={onViewDetails}
                                onDownstreamAction={onDownstreamAction}
                                onTrainNew={() => { }}
                                isLoading={msg.id === currentProgressMsgId.current && isLoading}
                            />
                            {/* Previous external card rendering block removed */}
                        </motion.div>
                    ))}
                </AnimatePresence>
                {/* Removed static suggestions in favor of onFocus popup */}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t bg-white dark:bg-gray-900 shrink-0">
                <div className="flex gap-2 relative">
                    <AnimatePresence>
                        {showSuggestions && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 10 }}
                                className="absolute bottom-full left-0 w-full mb-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-30"
                            >
                                <div className="p-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                    Suggested Queries
                                </div>
                                {["I want to search for genetic scores for COL1A1", "I want to search for genetic scores for APOE", "I want to search for genetic scores for EGFR", "I want to search for genetic scores for TP53"].map((suggestion, idx) => (
                                    <button
                                        key={idx}
                                        className="w-full text-left px-4 py-3 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 text-gray-700 dark:text-gray-200"
                                        onMouseDown={(e) => {
                                            e.preventDefault();
                                            handleSend(suggestion);
                                            setShowSuggestions(false);
                                        }}
                                    >
                                        <span className="bg-violet-100 dark:bg-violet-900 text-violet-600 dark:text-violet-300 p-1 rounded">
                                            <SendHorizontal className="h-3 w-3" />
                                        </span>
                                        {suggestion}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        onFocus={() => setShowSuggestions(true)}
                        onBlur={() => setShowSuggestions(false)}
                        placeholder="Ask about proteins..."
                        disabled={isLoading}
                        className="flex-1"
                    />
                    <Button
                        onClick={() => handleSend()}
                        disabled={isLoading || !input.trim()}
                        className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600"
                    >
                        {isLoading ? <Loader2 className="animate-spin" size={18} /> : <SendHorizontal size={18} />}
                    </Button>
                </div>
                {/* Attribution Footer */}
                <div className="text-center text-[10px] text-gray-400 mt-2 flex flex-col gap-0.5 select-none shrink-0">
                    <div>PennPRS Lab &copy; 2025</div>
                    <div className="flex items-center justify-center gap-1 opacity-60">
                        <span>Data:</span>
                        <a href="https://www.omicspred.org/" target="_blank" rel="noopener noreferrer" className="hover:text-violet-500 hover:underline transition-colors text-[9px]">OmicsPred</a>
                        <span className="mx-0.5">•</span>
                        <span>Training:</span>
                        <a href="https://pennprs.org/" target="_blank" rel="noopener noreferrer" className="hover:text-violet-500 hover:underline transition-colors text-[9px]">PennPRS</a>
                    </div>
                </div>
            </div>
        </div >
    );
}
