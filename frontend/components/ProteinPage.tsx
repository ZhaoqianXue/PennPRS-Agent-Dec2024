"use client";

import { useState, useEffect } from "react";
import ChatInterface, { StructuredResponse } from "./ChatInterface";
import CanvasArea, { ViewType } from "./CanvasArea";
import { ModelData } from "./ModelCard";
import ProteinDetailModal from "./ProteinDetailModal";
import { Home, Dna } from "lucide-react";

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
    // Global State
    const [activeView, setActiveView] = useState<ViewType>('protein_search');
    const [previousView, setPreviousView] = useState<ViewType>('protein_search');
    const [currentQuery, setCurrentQuery] = useState<string | null>(null);
    const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);

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

    // Smart Recommendation State
    const [smartRecommendation, setSmartRecommendation] = useState<string | null>(null);
    const [smartRecommendationModel, setSmartRecommendationModel] = useState<ProteinModelData | null>(null);
    const [smartRecommendationActions, setSmartRecommendationActions] = useState<string[] | null>(null);

    const triggerChat = (msg: string) => {
        setExternalTriggerDetails(msg);
        setTimeout(() => setExternalTriggerDetails(null), 100);
    }

    // --- Handlers ---

    const handleProteinSearch = (query: string, platform?: string) => {
        // RESET States
        setCurrentQuery(query);
        setSelectedPlatform(platform || null);
        setModels([]);
        setIsSearching(true);
        setIsSearchComplete(false);
        setSearchProgress(null);
        setSmartRecommendation(null);
        setSmartRecommendationModel(null);
        setSmartRecommendationActions(null);

        // SWITCH to grid view
        setActiveView('protein_grid');

        // TRIGGER Search
        let searchMsg = `Search for protein scores for ${query}`;
        if (platform) {
            searchMsg += ` on ${platform} platform`;
        }
        triggerChat(searchMsg);
    };

    const handlePlatformSelect = (platform: string) => {
        handleProteinSearch("", platform);
    };

    // --- Effects ---
    useEffect(() => {
        if (activeView === 'protein_grid' && isSearchComplete && models.length > 0) {
            // Generate smart recommendation
            const best = models.reduce((prev, current) => {
                const prevR2 = prev.metrics?.R2 || 0;
                const currR2 = current.metrics?.R2 || 0;
                return prevR2 > currR2 ? prev : current;
            }, models[0]);

            let msg = `I found **${models.length}** proteomics genetic scores`;
            if (currentQuery) {
                msg += ` related to **'${currentQuery}'**`;
            }
            if (selectedPlatform) {
                msg += ` on the **${selectedPlatform}** platform`;
            }
            msg += ` from OmicsPred.\n\n`;
            msg += `The top scoring model is **${best.name}** (ID: ${best.id}).\n`;
            msg += `You can view detailed information for this result and others in the **Canvas** panel.`;

            setSmartRecommendation(msg);
            setSmartRecommendationModel(best);
            setSmartRecommendationActions([
                "View Score Details",
                "Download this Score",
                "Browse Another Platform"
            ]);
        }
    }, [activeView, isSearchComplete, models, currentQuery, selectedPlatform]);

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
            // Go back to platform selection
            setActiveView('protein_search');
        } else {
            triggerChat(`I want to ${action.toLowerCase()}`);
        }
    };

    const handleBackToPrevious = () => {
        if (activeView === 'protein_grid') {
            setActiveView('protein_search');
        } else {
            setActiveView('protein_search');
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
                        <Home size={20} />
                    </button>
                    <Dna className="text-violet-500" size={24} />
                    <span className="bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">Proteomics PRS Models</span>
                </div>
                <div className="ml-auto flex items-center gap-4">
                    {(activeView !== 'protein_search') && (
                        <button
                            onClick={() => {
                                setActiveView('protein_search');
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
                        platform={selectedPlatform}
                        models={models}
                        onSearch={handleProteinSearch}
                        onPlatformSelect={handlePlatformSelect}
                        onSelectModel={handleSelectModel}
                        onViewDetails={handleViewDetails}
                        onBackToSelection={handleBackToPrevious}
                        searchProgress={searchProgress}
                        isSearchComplete={isSearchComplete}
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
    platform: string | null;
    models: ProteinModelData[];
    onSearch: (query: string, platform?: string) => void;
    onPlatformSelect: (platform: string) => void;
    onSelectModel: (modelId: string) => void;
    onViewDetails: (model: ModelData) => void;
    onBackToSelection: () => void;
    searchProgress: { status: string; total: number; fetched: number; current_action: string } | null;
    isSearchComplete: boolean;
}

function ProteinCanvasArea({
    view,
    query,
    platform,
    models,
    onSearch,
    onPlatformSelect,
    onSelectModel,
    onViewDetails,
    onBackToSelection,
    searchProgress,
    isSearchComplete
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

    if (view === 'protein_search') {
        return (
            <div className="h-full flex flex-col items-center justify-center p-8 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
                {/* Search Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent mb-4">
                        Proteomics PRS Models
                    </h1>
                    <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl">
                        Search for single or multiple proteins (comma-separated) to find genetic prediction models from
                        <a href="https://www.omicspred.org" target="_blank" rel="noopener noreferrer" className="text-violet-600 hover:underline ml-1">
                            OmicsPred
                        </a>
                    </p>
                </div>

                {/* Search Bar */}
                <div className="w-full max-w-2xl mb-12">
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
                            placeholder="Search by protein name (e.g., APOE, IL6), gene symbol, or UniProt ID..."
                            className="w-full px-6 py-4 text-lg rounded-2xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:border-violet-500 focus:ring-4 focus:ring-violet-500/20 outline-none transition-all"
                        />
                        <button
                            onClick={() => searchInput.trim() && onSearch(searchInput.trim())}
                            className="absolute right-3 top-1/2 -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-violet-500 to-purple-500 text-white font-semibold rounded-xl hover:from-violet-600 hover:to-purple-600 transition-all"
                        >
                            Search
                        </button>
                    </div>
                </div>

                {/* Featured Scenarios */}
                <div className="w-full max-w-4xl mb-12">
                    <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4 text-center">
                        Featured Scenarios
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button
                            onClick={() => onSearch("APOE, BIN1, CLU, ABCA7, CR1, PICALM, MS4A6A, CD33, TREM2, SORL1")}
                            className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-violet-400 transition-all text-left group"
                        >
                            <div className="font-bold text-gray-800 dark:text-gray-100 group-hover:text-violet-600 mb-1">
                                Alzheimer's Disease (AD)
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                                APOE, BIN1, CLU, ABCA7, CR1, PICALM, MS4A6A, CD33...
                            </div>
                        </button>

                        <button
                            onClick={() => onSearch("IL6, TNF, CRP, IL1B, IL18, CXCL8, IL10, IL2")}
                            className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-violet-400 transition-all text-left group"
                        >
                            <div className="font-bold text-gray-800 dark:text-gray-100 group-hover:text-violet-600 mb-1">
                                Inflammation Panel
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                                IL6, TNF, CRP, IL1B, IL18, CXCL8, IL10, IL2...
                            </div>
                        </button>

                        <button
                            onClick={() => onSearch("PCSK9, LPA, ANGPTL3, APOC3, APOB, LDLR, LPL")}
                            className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-violet-400 transition-all text-left group"
                        >
                            <div className="font-bold text-gray-800 dark:text-gray-100 group-hover:text-violet-600 mb-1">
                                Lipid Metabolism
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                                PCSK9, LPA, ANGPTL3, APOC3, APOB, LDLR, LPL...
                            </div>
                        </button>
                    </div>
                </div>

                {/* Platform Cards */}
                <div className="w-full max-w-4xl">
                    <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-6 text-center">
                        Or Browse by Platform
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {platforms.map((p) => (
                            <button
                                key={p.id}
                                onClick={() => onPlatformSelect(p.id)}
                                className="group relative p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:-translate-y-1 transition-all text-left"
                            >
                                <div className={`absolute top-0 left-0 w-2 h-full rounded-l-2xl bg-gradient-to-b ${p.color}`}></div>
                                <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-2 ml-2">{p.name}</h3>
                                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 ml-2">{p.description}</p>
                                <span className="inline-block ml-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300">
                                    {p.proteins}
                                </span>
                            </button>
                        ))}
                    </div>
                </div>
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
                            {query ? `Results for "${query}"` : platform ? `${platform} Scores` : "All Scores"}
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

import { useState as useReactState, useRef, useEffect as useReactEffect } from "react";
import { SendHorizontal, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { AnimatePresence, motion } from "framer-motion";
import { ProgressBar } from "./ProgressBar";

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
    const [messages, setMessages] = useReactState<Message[]>([
        {
            role: 'agent',
            content: "Welcome to **PennPRS-Protein**! 🧬\n\nI can help you search for genetic prediction models for protein expression levels from OmicsPred.\n\nTry asking: *\"Find scores for APOE\"* or *\"Browse Olink proteins\"*",
            id: 'welcome'
        }
    ]);
    const [input, setInput] = useReactState("");
    const [isLoading, setIsLoading] = useReactState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useReactEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Handle external triggers
    useReactEffect(() => {
        if (externalTrigger) {
            handleSend(externalTrigger);
        }
    }, [externalTrigger]);

    // Handle external agent message (for smart recommendations)
    useReactEffect(() => {
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
