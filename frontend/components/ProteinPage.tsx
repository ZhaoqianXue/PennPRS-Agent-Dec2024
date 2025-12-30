"use client";

import { useState, useEffect, useRef } from "react";
import ChatInterface, { StructuredResponse } from "./ChatInterface";
import CanvasArea, { ViewType } from "./CanvasArea";
import { ModelData } from "./ModelCard";
import ProteinDetailModal from "./ProteinDetailModal";
import SearchSummaryView from "./SearchSummaryView";
import { Home, Dna, Bookmark, Search, Database, ArrowLeft, User, Users, Activity, SendHorizontal, Loader2 } from "lucide-react";
import TrainingConfigForm, { TrainingConfig } from "./TrainingConfigForm";
import MultiAncestryTrainingForm, { MultiAncestryTrainingConfig } from "./MultiAncestryTrainingForm";
import { AnimatePresence, motion } from "framer-motion";
import { ProgressBar } from "./ProgressBar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChatBubble } from "@/components/chat/ChatBubble";

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

        // NEW FLOW: Stay on protein_search while searching (shows loading state)
        // View will transition to protein_search_summary when search completes

        // TRIGGER Search
        const searchMsg = `Search for protein scores for ${query}`;
        triggerChat(searchMsg);
    };

    // Handle ancestry submit (matching Disease flow)
    const handleAncestrySubmit = (ancestries: string[]) => {
        setIsAncestrySubmitted(true);
        setSelectedAncestry(ancestries);
        // Effect will handle transition to grid
    };

    // --- Effects ---

    // Effect 1: When search completes, transition to search_summary view
    useEffect(() => {
        if (isSearchComplete && models.length > 0 && activeView === 'protein_search') {
            // Transition to search summary view
            pushView('protein_search_summary');
        }
    }, [isSearchComplete, models.length, activeView]);

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
                    "View Score Details"
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
                        model={selectedModelDetails}
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
                                    Retrieving molecular data and PRS models for <span className="font-semibold text-violet-600">"{query || searchInput || "your selection"}"</span>
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
                            Choose a reference gene or protein to find associated models
                        </p>
                    </div>

                    {/* Search Bar */}
                    <div className="w-full max-w-2xl mb-10 shrink-0">
                        <div className="relative">
                            <input
                                type="text"
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && searchInput.trim()) {
                                        onSearch(searchInput.trim());
                                    }
                                }}
                                placeholder="Search any gene or protein (e.g., TNF, IL6)..."
                                className="w-full px-6 py-4 text-lg rounded-2xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 outline-none transition-all shadow-sm"
                            />
                            <button
                                onClick={() => searchInput.trim() && onSearch(searchInput.trim())}
                                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 rounded-xl hover:bg-violet-200 dark:hover:bg-violet-900/50 transition-all"
                            >
                                <Search size={24} />
                            </button>
                        </div>
                    </div>

                    {/* Selection Grids */}
                    <div className="w-full grid md:grid-cols-1 gap-10 pb-8">

                        {/* Reference Genes */}
                        <div className="space-y-4">
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                                <Dna className="w-5 h-5 text-violet-500" />
                                Reference Genes
                            </h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {["COL1A1", "APOE", "EGFR", "TP53"].map((gene) => (
                                    <button
                                        key={gene}
                                        onClick={() => onSearch(gene)}
                                        className="group p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-violet-400 dark:hover:border-violet-500 hover:shadow-md transition-all text-left"
                                    >
                                        <div className="font-bold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 mb-1">
                                            {gene}
                                        </div>
                                        <div className="text-xs text-gray-500 dark:text-gray-400">
                                            Gene Symbol
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Featured Proteins */}
                        <div className="space-y-4">
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                                <Activity className="w-5 h-5 text-purple-500" />
                                Featured Proteins
                            </h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {[
                                    { name: "P53", id: "P53" },
                                    { name: "Albumin", id: "Albumin" },
                                    { name: "C-Reactive Protein", id: "CRP" },
                                    { name: "Insulin", id: "Insulin" }
                                ].map((prot) => (
                                    <button
                                        key={prot.id}
                                        onClick={() => onSearch(prot.id)}
                                        className="group p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 hover:shadow-md transition-all text-left"
                                    >
                                        <div className="font-bold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 mb-1 truncate">
                                            {prot.name}
                                        </div>
                                        <div className="text-xs text-gray-500 dark:text-gray-400">
                                            Protein
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // View: Protein Search Summary (NEW - matching Disease flow)
    if (view === 'protein_search_summary') {
        return (
            <div className="h-full overflow-y-auto">
                <SearchSummaryView
                    trait={query || "Protein Search"}
                    models={models as ModelData[]}
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
                                        onSelect={() => onSelectModel(model.id)}
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
    onSelect: () => void;
}

function ProteinScoreCard({ model, onViewDetails, onSelect }: ProteinScoreCardProps) {
    const metrics = model.metrics || {};

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg hover:border-violet-400/50 transition-all group">
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <h3 className="font-bold text-gray-800 dark:text-gray-100 group-hover:text-violet-600 transition-colors line-clamp-2">
                        {model.protein_name || model.gene_name || model.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">{model.id}</span>
                        {model.gene_name && model.gene_name !== model.protein_name && (
                            <span className="text-xs px-1.5 py-0.5 bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400 rounded">
                                {model.gene_name}
                            </span>
                        )}
                    </div>
                </div>
                {model.platform && (
                    <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full ${model.platform.includes('Olink') || model.platform === 'Target'
                        ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400'
                        : 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
                        }`}>
                        {model.platform}
                    </span>
                )}
            </div>

            {/* Info */}
            <div className="space-y-1 text-sm mb-4">
                {model.dataset_name && (
                    <p className="text-gray-600 dark:text-gray-400">
                        <span className="text-gray-500">Dataset:</span> {model.dataset_name}
                    </p>
                )}
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                    <span><span className="text-gray-500">Variants:</span> {model.num_variants?.toLocaleString() || 'N/A'}</span>
                    <span><span className="text-gray-500">Samples:</span> {model.sample_size?.toLocaleString() || 'N/A'}</span>
                </div>
            </div>

            {/* Metrics */}
            <div className="flex gap-2 mb-4">
                <div className="flex-1 px-3 py-2 bg-violet-50 dark:bg-violet-900/20 rounded-lg text-center border border-violet-100 dark:border-violet-800">
                    <p className="text-[10px] text-gray-500 uppercase tracking-wide">R²</p>
                    <p className="font-bold text-violet-600 dark:text-violet-400 font-mono">
                        {metrics.R2 ? (typeof metrics.R2 === 'number' ? metrics.R2.toFixed(4) : metrics.R2) : 'N/A'}
                    </p>
                </div>
                {metrics.Rho && (
                    <div className="flex-1 px-3 py-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-center border border-purple-100 dark:border-purple-800">
                        <p className="text-[10px] text-gray-500 uppercase tracking-wide">ρ</p>
                        <p className="font-bold text-purple-600 dark:text-purple-400 font-mono">
                            {typeof metrics.Rho === 'number' ? metrics.Rho.toFixed(3) : metrics.Rho}
                        </p>
                    </div>
                )}
            </div>

            {/* Actions */}
            <div className="flex gap-2">
                <button
                    onClick={onViewDetails}
                    className="flex-1 px-4 py-2 text-sm font-medium text-violet-600 border border-violet-300 dark:border-violet-600 rounded-lg hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors"
                >
                    View Details
                </button>
                <button
                    onClick={onSelect}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-violet-500 to-purple-500 rounded-lg hover:from-violet-600 hover:to-purple-600 transition-colors"
                >
                    Select
                </button>
            </div>
        </div>
    );
}

// === Protein Chat Card Component (Compact for Chat Interface) ===

interface ProteinChatCardProps {
    model: ProteinModelData;
    onViewDetails: () => void;
}

function ProteinChatCard({ model, onViewDetails }: ProteinChatCardProps) {
    const metrics = model.metrics || {};

    return (
        <div className="w-full max-w-[320px] bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-all">
            {/* Header */}
            <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-gray-800 dark:text-gray-100 text-sm line-clamp-2">
                        {model.protein_name || model.gene_name || model.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-[11px] text-gray-500 dark:text-gray-400 font-mono">{model.id}</span>
                        {model.platform && (
                            <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-400">
                                {model.platform}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Gene Name Badge */}
            {model.gene_name && model.gene_name !== model.protein_name && (
                <div className="mb-2">
                    <span className="text-xs px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded">
                        Gene: {model.gene_name}
                    </span>
                </div>
            )}

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="text-center p-2 bg-violet-50 dark:bg-violet-900/20 rounded-lg border border-violet-100 dark:border-violet-800">
                    <p className="text-[9px] text-gray-500 uppercase">R²</p>
                    <p className="font-bold text-violet-600 dark:text-violet-400 text-sm font-mono">
                        {metrics.R2 ? metrics.R2.toFixed(3) : 'N/A'}
                    </p>
                </div>
                <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-800">
                    <p className="text-[9px] text-gray-500 uppercase">ρ (Rho)</p>
                    <p className="font-bold text-purple-600 dark:text-purple-400 text-sm font-mono">
                        {metrics.Rho ? metrics.Rho.toFixed(3) : 'N/A'}
                    </p>
                </div>
                <div className="text-center p-2 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
                    <p className="text-[9px] text-gray-500 uppercase">Variants</p>
                    <p className="font-bold text-slate-700 dark:text-slate-300 text-sm font-mono">
                        {model.num_variants ? (model.num_variants > 1000 ? (model.num_variants / 1000).toFixed(1) + 'k' : model.num_variants) : 'N/A'}
                    </p>
                </div>
            </div>

            {/* Dataset Info */}
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                <span>{model.dataset_name || 'Unknown'}</span>
                <span className="mx-1">•</span>
                <span>{model.ancestry} ancestry</span>
                {model.sample_size && (
                    <>
                        <span className="mx-1">•</span>
                        <span>{model.sample_size.toLocaleString()} samples</span>
                    </>
                )}
            </div>

            {/* View Details Button */}
            <button
                onClick={onViewDetails}
                className="w-full px-3 py-2 text-sm font-medium text-violet-600 border border-violet-300 dark:border-violet-600 rounded-lg hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors"
            >
                View Details
            </button>
        </div>
    );
}

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
            content: "Welcome to **PennPRS-Protein**! 🧬\n\nI can help you search for genetic prediction models for protein expression levels from OmicsPred.\n\nTry asking: *\"Find scores for APOE\"* or *\"Browse Olink proteins\"*",
            id: 'welcome'
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
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

    const handleSend = async (text: string = input) => {
        if (!text.trim() || isLoading) return;

        const userMsg: Message = { role: 'user', content: text, id: `user-${Date.now()}` };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);
        onSearchStatusChange(true);

        const requestId = `protein-${Date.now()}`;

        // Add progress message
        setMessages(prev => [...prev, {
            role: 'agent',
            content: "Searching OmicsPred...",
            id: `progress-${requestId}`,
            isProgress: true,
            progressData: { status: "starting", total: 0, fetched: 0, current_action: "Initializing..." }
        }]);

        // Start polling for progress
        const pollInterval = setInterval(async () => {
            try {
                const progressRes = await fetch(`http://localhost:8000/agent/search_progress/${requestId}`);
                const progressData = await progressRes.json();

                if (progressData.status !== "unknown") {
                    onProgressUpdate(progressData);

                    setMessages(prev => prev.map(m =>
                        m.id === `progress-${requestId}`
                            ? { ...m, progressData }
                            : m
                    ));

                    if (progressData.status === "completed") {
                        clearInterval(pollInterval);
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

            const data = await res.json();
            const structuredResponse = data.full_state?.structured_response;

            // Remove progress message and add final response
            setMessages(prev => {
                const filtered = prev.filter(m => m.id !== `progress-${requestId}`);
                const agentMsg: Message = {
                    role: 'agent',
                    content: data.response,
                    id: `agent-${Date.now()}`,
                    modelCard: structuredResponse?.best_model,
                    actions: structuredResponse?.actions
                };
                return [...filtered, agentMsg];
            });

            if (structuredResponse) {
                onResponse(structuredResponse as StructuredResponse);
            }

        } catch (error) {
            clearInterval(pollInterval);
            console.error("Protein agent error:", error);

            setMessages(prev => {
                const filtered = prev.filter(m => !m.isProgress);
                return [...filtered, {
                    role: 'agent',
                    content: "Sorry, I encountered an error connecting to the backend. Please make sure the server is running.",
                    id: `error-${Date.now()}`
                }];
            });
        }

        setIsLoading(false);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Chat Header */}
            <div className="p-4 border-b bg-white dark:bg-gray-900">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <Dna className="text-violet-500" size={20} />
                    Protein Agent
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    Powered by OmicsPred
                </p>
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
                            {msg.isProgress ? (
                                <div className="flex flex-col items-center gap-2 py-4">
                                    <div className="w-full max-w-sm">
                                        <ProgressBar
                                            status={msg.progressData?.status || "starting"}
                                            total={msg.progressData?.total || 0}
                                            fetched={msg.progressData?.fetched || 0}
                                            currentAction={msg.progressData?.current_action || "Initializing..."}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <ChatBubble
                                        role={msg.role}
                                        content={msg.content}
                                        actions={msg.actions}
                                        onViewDetails={onViewDetails}
                                        onDownstreamAction={onDownstreamAction}
                                        onTrainNew={() => { }}
                                    />
                                    {/* Use ProteinChatCard instead of ModelCard for protein data */}
                                    {msg.role === 'agent' && msg.modelCard && (
                                        <div className="ml-12 mt-2">
                                            <ProteinChatCard
                                                model={msg.modelCard as ProteinModelData}
                                                onViewDetails={() => onViewDetails(msg.modelCard!)}
                                            />
                                        </div>
                                    )}
                                </>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t bg-white dark:bg-gray-900">
                <div className="flex gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
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
            </div>
        </div>
    );
}
