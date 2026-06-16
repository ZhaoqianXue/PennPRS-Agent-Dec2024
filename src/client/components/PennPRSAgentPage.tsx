"use client";

import { useEffect, useRef, useState } from "react";
import type { MouseEvent } from "react";
import Link from "next/link";
import { Activity, Bookmark, CheckCircle2, Home, Loader2, Mail, SendHorizontal } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import CanvasArea, { type ViewType } from "./CanvasArea";
import ModelDetailModal from "./ModelDetailModal";
import type { ModelData } from "./ModelCard";
import type { TrainingConfig } from "./TrainingConfigForm";
import type { MultiAncestryTrainingConfig } from "./MultiAncestryTrainingForm";
import { ChatBubble } from "./chat/ChatBubble";

interface PennPRSAgentPageProps {
    onBack: () => void;
}

type AgentMode = "cached" | "live";

interface AgentTraceStep {
    id: string;
    title: string;
    status: "queued" | "running" | "completed" | "skipped" | "failed";
    detail: string;
    provenance?: string[];
}

interface QualityAssessment {
    accept_direct_baseline: boolean;
    rationale: string;
}

interface FinalRecommendation {
    recommendation_source: "same_trait" | "cross_trait_transfer" | "none";
    recommended_pgs_id?: string | null;
    recommended_trait?: string | null;
    confidence?: string | null;
    summary: string;
}

interface PerformanceMetrics {
    auc?: number | string | null;
    pgs_only_auc?: number | string | null;
    full_model_auc?: number | string | null;
    r2?: number | string | null;
    pgs_only_r2?: number | string | null;
    full_model_r2?: number | string | null;
    [key: string]: unknown;
}

interface SameTraitEvidence {
    trait_reported?: string | null;
    trait_efo?: string | null;
    method?: string | null;
    ancestry_distribution?: string | null;
    samples_training?: string | null;
    validation_sample_size?: string | number | null;
    performance_metrics?: PerformanceMetrics;
    [key: string]: unknown;
}

interface SameTraitResult {
    status: "found" | "unavailable" | string;
    execution_mode?: string;
    resolved_trait?: string | null;
    match_score?: number | null;
    match_kind?: string | null;
    matched_label?: string | null;
    recommendation_type?: string | null;
    pgs_id?: string | null;
    confidence?: string | null;
    rationale?: string | null;
    models_evaluated?: number | null;
    candidate_model_ids?: string[];
    shortlist_model_ids?: string[];
    selected_model_evidence?: SameTraitEvidence;
    model_preview?: ModelData | null;
    model_previews?: ModelData[] | null;
}

interface TransferResult {
    status: "found" | "unavailable" | string;
    execution_mode?: string;
    target_trait?: string | null;
    source_trait?: string | null;
    pgs_id?: string | null;
    confidence?: string | null;
    rationale?: string | null;
    model_previews?: ModelData[] | null;
}

interface AgentResponse {
    target_trait: string;
    mode: AgentMode;
    same_trait_result: SameTraitResult;
    same_trait_quality_assessment: QualityAssessment;
    transfer_result: TransferResult | null;
    final_recommendation: FinalRecommendation;
    agent_trace_steps: AgentTraceStep[];
    artifacts_used: Array<Record<string, unknown>>;
    warnings: string[];
    errors: string[];
    timing: Record<string, unknown>;
}

interface ProgressState {
    status: string;
    total: number;
    fetched: number;
    current_action: string;
}

interface ChatMessage {
    role: "user" | "agent";
    content: string;
    id: string;
    modelCard?: ModelData;
    actions?: string[];
    progressData?: ProgressState | null;
}

type SummaryDisplayMode = "target" | "source";

const API_BASE = "http://localhost:8000";
const AGENT_MODE: AgentMode = "cached";

const agentWorkflowPaths = [
    {
        title: "Same-trait baseline accepted",
        label: "Path 1 · Direct",
        description: "The agent finds a same-trait PRS and the quality gate accepts it, so no transfer escalation is needed.",
        example: "Breast cancer",
        exampleTrait: "Breast cancer",
        tone: "blue" as const,
    },
    {
        title: "Same-trait baseline is insufficient",
        label: "Path 2 · Escalate",
        description: "A same-trait PRS exists, but the quality gate rejects it as too weak or suboptimal, so transfer evidence is evaluated.",
        example: "Alzheimer disease",
        exampleTrait: "late-onset Alzheimer's disease",
        tone: "amber" as const,
    },
    {
        title: "No same-trait baseline found",
        label: "Path 3 · Transfer",
        description: "No usable same-trait PRS is available, so the agent relies on cross-trait transfer while preserving the missing baseline as context.",
        example: "Migraine",
        exampleTrait: "migraine",
        tone: "rose" as const,
    },
];

const welcomeMessage: ChatMessage = {
    id: "welcome",
    role: "agent",
    content:
        "Welcome to PennPRS Lab! I'm your research assistant — here to help you navigate and leverage this platform. I can answer questions, design research workflows, and analyze results. Let me know what you need help with! To begin, you can type in the chat box or select a disease of interest from the side panel, and I'll recommend the most suitable PRS models for you.",
};

function coerceNumber(value: unknown): number | undefined {
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string") {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : undefined;
    }
    return undefined;
}

function normalizeModel(model: ModelData): ModelData {
    return {
        ...model,
        id: model.id || model.name,
        name: model.name || model.id,
        trait: model.trait || "Unknown trait",
        ancestry: model.ancestry || "N/A",
        method: model.method || "Unknown",
        source: model.source || "PGS Catalog",
        metrics: {
            AUC: coerceNumber(model.metrics?.AUC),
            R2: coerceNumber(model.metrics?.R2),
            HR: coerceNumber(model.metrics?.HR),
            OR: coerceNumber(model.metrics?.OR),
            Beta: coerceNumber(model.metrics?.Beta),
        },
    };
}

function sameTraitModelListFromResponse(response: AgentResponse): ModelData[] {
    const sameTrait = response.same_trait_result;
    const rawModels = [
        sameTrait.model_preview,
        ...(Array.isArray(sameTrait.model_previews) ? sameTrait.model_previews : []),
    ].filter(Boolean) as ModelData[];

    const modelsById = new Map<string, ModelData>();
    rawModels.map(normalizeModel).forEach((model) => {
        if (model.id && !modelsById.has(model.id)) {
            modelsById.set(model.id, model);
        }
    });

    if (modelsById.size === 0 && sameTrait.pgs_id) {
        modelsById.set(sameTrait.pgs_id, {
            id: sameTrait.pgs_id,
            name: sameTrait.pgs_id,
            trait: sameTrait.resolved_trait || response.target_trait,
            ancestry: sameTrait.selected_model_evidence?.ancestry_distribution || "N/A",
            method: sameTrait.selected_model_evidence?.method || "Unknown",
            source: "PGS Catalog",
            metrics: {
                AUC: coerceNumber(
                    sameTrait.selected_model_evidence?.performance_metrics?.auc ||
                    sameTrait.selected_model_evidence?.performance_metrics?.pgs_only_auc ||
                    sameTrait.selected_model_evidence?.performance_metrics?.full_model_auc
                ),
                R2: coerceNumber(
                    sameTrait.selected_model_evidence?.performance_metrics?.r2 ||
                    sameTrait.selected_model_evidence?.performance_metrics?.pgs_only_r2 ||
                    sameTrait.selected_model_evidence?.performance_metrics?.full_model_r2
                ),
            },
        });
    }

    return Array.from(modelsById.values());
}

function transferModelListFromResponse(response: AgentResponse): ModelData[] {
    const transfer = response.transfer_result;
    const rawModels = Array.isArray(transfer?.model_previews) ? transfer.model_previews : [];
    const modelsById = new Map<string, ModelData>();

    rawModels.map(normalizeModel).forEach((model) => {
        if (model.id && !modelsById.has(model.id)) {
            modelsById.set(model.id, model);
        }
    });

    const finalPgsId = response.final_recommendation.recommended_pgs_id;
    if (didExecuteC3Transfer(response) && finalPgsId && !modelsById.has(finalPgsId)) {
        modelsById.set(finalPgsId, {
            id: finalPgsId,
            name: finalPgsId,
            trait:
                transfer?.source_trait ||
                response.final_recommendation.recommended_trait ||
                response.target_trait,
            ancestry: "Cross-trait transfer",
            method: "Transfer recommendation",
            source: "PGS Catalog",
            metrics: {},
        });
    }

    return Array.from(modelsById.values());
}

function getTransferSourceTrait(response: AgentResponse | null) {
    return response?.transfer_result?.source_trait || response?.final_recommendation.recommended_trait || null;
}

function inferTraitFromMessage(message: string) {
    const cleaned = message.trim();
    const patterns = [
        /models?\s+for\s+(.+)$/i,
        /search\s+for\s+(.+)$/i,
        /recommend\s+(.+)$/i,
    ];
    for (const pattern of patterns) {
        const match = cleaned.match(pattern);
        if (match?.[1]) return match[1].replace(/[.!?]+$/, "").trim();
    }
    return cleaned;
}

function pickBestModel(models: ModelData[]) {
    if (models.length === 0) return null;
    return models.reduce((best, current) => {
        const bestAuc = best.metrics?.AUC || 0;
        const currentAuc = current.metrics?.AUC || 0;
        return currentAuc > bestAuc ? current : best;
    }, models[0]);
}

function filterModelsByAncestry(models: ModelData[], selectedAncestry: string[]) {
    if (selectedAncestry.length === 0) return models;
    const ancestryMap: Record<string, string> = {
        EUR: "European",
        AFR: "African",
        EAS: "East Asian",
        SAS: "South Asian",
        AMR: "Hispanic",
        MIX: "Others",
    };
    return models.filter((model) => {
        const ancestry = (model.ancestry || "").toLowerCase();
        return selectedAncestry.some((code) => {
            const label = ancestryMap[code] || code;
            return ancestry.includes(code.toLowerCase()) || ancestry.includes(label.toLowerCase());
        });
    });
}

function didExecuteC3Transfer(response: AgentResponse) {
    return response.transfer_result?.status === "found" || response.final_recommendation.recommendation_source === "cross_trait_transfer";
}

function formatAgentLabel(value?: string | null) {
    if (!value) return "N/A";
    return value.replace(/_/g, " ");
}

function buildCompletionMessage(response: AgentResponse, models: ModelData[]) {
    const sameTrait = response.same_trait_result;
    const quality = response.same_trait_quality_assessment;
    const transfer = response.transfer_result;
    const final = response.final_recommendation;
    const evaluated = models.length || sameTrait.models_evaluated || 0;
    const selected = final.recommended_pgs_id || sameTrait.pgs_id || "N/A";
    const c3Executed = didExecuteC3Transfer(response);
    const c2Line =
        sameTrait.status === "found"
            ? `found \`${sameTrait.pgs_id || "N/A"}\` (${formatAgentLabel(sameTrait.recommendation_type || sameTrait.confidence)})`
            : `unavailable (${formatAgentLabel(sameTrait.recommendation_type || sameTrait.status)})`;
    const c3Line = c3Executed
        ? `executed C3 transfer from \`${transfer?.source_trait || final.recommended_trait || "N/A"}\` and selected \`${transfer?.pgs_id || selected}\``
        : quality.accept_direct_baseline
            ? "skipped because the C2 same-trait baseline passed the quality gate"
            : "unavailable because no C3 transfer score passed the agent filters";

    return `### 🔍 Analysis Complete

I have analyzed the available PRS landscape for **${response.target_trait}** using the PennPRS Agent workflow.

*   **Total Models Found**: \`${evaluated}\` clinical-grade scores
*   **Recommended Model**: \`${selected}\`
*   **C2 Same-Trait Baseline**: ${c2Line}
*   **Quality Gate**: \`${quality.accept_direct_baseline ? "accepted" : "rejected"}\` - ${quality.rationale || "No quality-gate rationale returned."}
*   **C3 Transfer**: ${c3Line}
*   **Final Source**: \`${formatAgentLabel(final.recommendation_source)}\`

---

**Guidance**: To refine these results for your specific study, please **select a target ancestry** from the filter panel on the left. This will allow me to recommend the most relevant model for your population.`;
}

export default function PennPRSAgentPage({ onBack }: PennPRSAgentPageProps) {
    const [activeView, setActiveView] = useState<ViewType>("mode_selection");
    const [currentTrait, setCurrentTrait] = useState<string | null>(null);
    const [models, setModels] = useState<ModelData[]>([]);
    const [downstreamOps, setDownstreamOps] = useState<{ modelId: string; trait: string; options: string[] } | null>(null);
    const [selectedModelDetails, setSelectedModelDetails] = useState<ModelData | null>(null);
    const [selectedActionModel, setSelectedActionModel] = useState<ModelData | null>(null);
    const [savedModels, setSavedModels] = useState<ModelData[]>([]);
    const [flyingModel, setFlyingModel] = useState<{ model: ModelData; startPos: { x: number; y: number } } | null>(null);
    const savedButtonRef = useRef<HTMLButtonElement>(null);

    const [searchProgress, setSearchProgress] = useState<ProgressState | null>(null);
    const [isSearchComplete, setIsSearchComplete] = useState(false);
    const [selectedAncestry, setSelectedAncestry] = useState<string[]>([]);
    const [isAncestrySubmitted, setIsAncestrySubmitted] = useState(false);
    const [agentResult, setAgentResult] = useState<AgentResponse | null>(null);
    const [targetTraitModels, setTargetTraitModels] = useState<ModelData[]>([]);
    const [transferTraitModels, setTransferTraitModels] = useState<ModelData[]>([]);
    const [summaryDisplayMode, setSummaryDisplayMode] = useState<SummaryDisplayMode>("target");
    const [requestError, setRequestError] = useState<string | null>(null);

    const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [activeProgressMessageId, setActiveProgressMessageId] = useState<string | null>(null);

    const [viewStack, setViewStack] = useState<ViewType[]>(["mode_selection"]);
    const [forwardStack, setForwardStack] = useState<ViewType[]>([]);

    const [trainingSubmitModal, setTrainingSubmitModal] = useState<{
        isOpen: boolean;
        jobName: string;
        email: string;
        jobType: "single" | "multi";
    } | null>(null);
    const [isTrainingSubmitting, setIsTrainingSubmitting] = useState(false);

    const canGoForward = forwardStack.length > 0;

    const pushView = (newView: ViewType) => {
        setViewStack((prev) => [...prev, newView]);
        setForwardStack([]);
        setActiveView(newView);
    };

    const goBack = () => {
        if (viewStack.length <= 1) return;
        const newStack = [...viewStack];
        const currentView = newStack.pop()!;
        const nextView = newStack[newStack.length - 1];

        setViewStack(newStack);
        setForwardStack((prev) => [currentView, ...prev]);
        if (activeView === "model_actions") setSelectedActionModel(null);
        if (activeView === "model_grid") setIsAncestrySubmitted(false);
        setActiveView(nextView);
    };

    const goForward = () => {
        if (forwardStack.length === 0) return;
        const newForwardStack = [...forwardStack];
        const nextView = newForwardStack.shift()!;

        setForwardStack(newForwardStack);
        setViewStack((prev) => [...prev, nextView]);
        setActiveView(nextView);
    };

    const resetToModeSelection = () => {
        setViewStack(["mode_selection"]);
        setForwardStack([]);
        setActiveView("mode_selection");
        setCurrentTrait(null);
        setModels([]);
        setTargetTraitModels([]);
        setTransferTraitModels([]);
        setSummaryDisplayMode("target");
        setDownstreamOps(null);
        setAgentResult(null);
        setSearchProgress(null);
        setIsSearchComplete(false);
        setSelectedAncestry([]);
        setIsAncestrySubmitted(false);
        setRequestError(null);
    };

    const goToSearchSummary = () => {
        setViewStack((prev) => {
            const base: ViewType[] = prev.includes("disease_selection")
                ? prev.filter((view) => view !== "search_summary" && view !== "model_grid")
                : ["mode_selection", "disease_selection"];
            return [...base, "search_summary"];
        });
        setForwardStack([]);
        setActiveView("search_summary");
    };

    const transferSourceTrait = getTransferSourceTrait(agentResult);
    const activeSummaryTrait =
        summaryDisplayMode === "source" && transferSourceTrait ? transferSourceTrait : currentTrait;
    const canSwitchTransferSummary =
        !!agentResult && didExecuteC3Transfer(agentResult) && !!transferSourceTrait && transferTraitModels.length > 0;

    const showSummaryMode = (mode: SummaryDisplayMode) => {
        if (mode === "source" && transferTraitModels.length === 0) return;
        setSummaryDisplayMode(mode);
        setSelectedAncestry([]);
        setIsAncestrySubmitted(false);
        setModels(mode === "source" ? transferTraitModels : targetTraitModels);
    };

    const runAgentForTrait = async (trait: string, userText = `I want to search for models for ${trait}`) => {
        const targetTrait = trait.trim();
        if (!targetTrait || loading) return;

        const progressId = `prog-${Date.now()}`;
        const userMessage: ChatMessage = {
            id: `${Date.now()}`,
            role: "user",
            content: userText,
        };
        const progressMessage: ChatMessage = {
            id: progressId,
            role: "agent",
            content: "Searching for clinical PRS models...",
            progressData: null,
        };

        setCurrentTrait(targetTrait);
        setModels([]);
        setTargetTraitModels([]);
        setTransferTraitModels([]);
        setSummaryDisplayMode("target");
        setDownstreamOps(null);
        setAgentResult(null);
        setRequestError(null);
        setSelectedAncestry([]);
        setIsAncestrySubmitted(false);
        setIsSearchComplete(false);
        setLoading(true);
        setActiveProgressMessageId(progressId);
        setSearchProgress({
            status: "running",
            total: 4,
            fetched: 1,
            current_action: "Resolving target trait and cached artifacts...",
        });
        setMessages((prev) => [...prev, userMessage, progressMessage]);

        if (activeView === "mode_selection") {
            setViewStack(["mode_selection", "disease_selection"]);
            setForwardStack([]);
            setActiveView("disease_selection");
        }

        const timers = [
            window.setTimeout(() => {
                setSearchProgress({
                    status: "running",
                    total: 4,
                    fetched: 2,
                    current_action: "Evaluating same-trait PGS baseline...",
                });
            }, 250),
            window.setTimeout(() => {
                setSearchProgress({
                    status: "running",
                    total: 4,
                    fetched: 3,
                    current_action: "Running the quality gate and C3 transfer when needed...",
                });
            }, 650),
        ];

        try {
            const response = await fetch(`${API_BASE}/pennprs-agent/recommend`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ target_trait: targetTrait, mode: AGENT_MODE }),
            });
            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || `Request failed with status ${response.status}`);
            }

            const payload = (await response.json()) as AgentResponse;
            const nextTargetModels = sameTraitModelListFromResponse(payload);
            const nextTransferModels = transferModelListFromResponse(payload);
            const c3Executed = didExecuteC3Transfer(payload);
            const shouldShowTransferSummary = c3Executed && nextTransferModels.length > 0;
            const nextSummaryMode: SummaryDisplayMode = shouldShowTransferSummary ? "source" : "target";
            const nextModels = shouldShowTransferSummary ? nextTransferModels : nextTargetModels;
            const bestModel = nextModels.find((model) => model.id === payload.final_recommendation.recommended_pgs_id) || pickBestModel(nextModels) || undefined;
            const finalProgress: ProgressState = {
                status: "completed",
                total: 4,
                fetched: 4,
                current_action: c3Executed ? "C3 transfer executed; recommendation complete" : "C2 baseline accepted; C3 skipped",
            };

            setAgentResult(payload);
            setTargetTraitModels(nextTargetModels);
            setTransferTraitModels(nextTransferModels);
            setSummaryDisplayMode(nextSummaryMode);
            setModels(nextModels);
            setSearchProgress(finalProgress);
            setIsSearchComplete(true);
            setMessages((prev) =>
                prev.map((message) =>
                    message.id === progressId
                        ? {
                            ...message,
                            content: buildCompletionMessage(payload, nextModels),
                            progressData: finalProgress,
                            modelCard: bestModel,
                            actions: bestModel ? ["Download this Model", "Train a Custom Model"] : ["Train Custom Model"],
                        }
                        : message
                )
            );
            goToSearchSummary();
        } catch (error) {
            const message = error instanceof Error ? error.message : "PennPRS Agent request failed.";
            setRequestError(message);
            setSearchProgress(null);
            setMessages((prev) =>
                prev.map((item) =>
                    item.id === progressId
                        ? {
                            ...item,
                            content: `Search failed. ${message}`,
                            progressData: null,
                        }
                        : item
                )
            );
        } finally {
            timers.forEach((timer) => window.clearTimeout(timer));
            setLoading(false);
            setActiveProgressMessageId(null);
        }
    };

    useEffect(() => {
        if (activeView !== "search_summary" || !isAncestrySubmitted) return;

        const relevantModels = filterModelsByAncestry(models, selectedAncestry);
        const best = pickBestModel(relevantModels);
        const ancestryMap: Record<string, string> = {
            EUR: "European",
            AFR: "African",
            EAS: "East Asian",
            SAS: "South Asian",
            AMR: "Hispanic",
            MIX: "Others",
        };
        const ancestryLabel =
            selectedAncestry.length > 0
                ? selectedAncestry.map((code) => ancestryMap[code] || code).join(", ")
                : "All Ancestries";

        let content = `I found **${relevantModels.length}** models for **'${activeSummaryTrait}'** `;
        if (selectedAncestry.length > 0) {
            content += `matching your ancestry criteria (**${ancestryLabel}**).\n\n`;
        } else {
            content += "across all ancestries.\n\n";
        }
        if (best) {
            content += `The model with the highest AUC is **${best.name}** (ID: ${best.id}).\n`;
            content += "I've displayed the best model card below. You can view detailed information for this result and others in the **Canvas** panel.";
        } else {
            content += "No direct matches remain after filtering. You can broaden the filter or train a custom model.";
        }

        setMessages((prev) => [
            ...prev,
            {
                id: `ancestry-${Date.now()}`,
                role: "agent",
                content,
                modelCard: best || undefined,
                actions: best ? ["Download this Model", "Train a Custom Model"] : ["Train Custom Model"],
            },
        ]);
        setIsAncestrySubmitted(false);
        pushView("model_grid");
    }, [activeSummaryTrait, activeView, isAncestrySubmitted, models, selectedAncestry]);

    const handleAncestrySubmit = (ancestries: string[]) => {
        setSelectedAncestry(ancestries);
        if (activeView === "search_summary") {
            setIsAncestrySubmitted(true);
        }
    };

    const handleChatSubmit = (text: string) => {
        const trait = inferTraitFromMessage(text);
        void runAgentForTrait(trait, text);
    };

    const handleSelectModel = (modelId: string) => {
        setDownstreamOps({
            modelId,
            trait: activeSummaryTrait || agentResult?.target_trait || "selected trait",
            options: ["Evaluate this Model on Cohort(s)", "Ensemble this Model Across Phenotypes"],
        });
        pushView("downstream_options");
    };

    const handleDeepScan = (modelId: string) => {
        setMessages((prev) => [
            ...prev,
            {
                id: `deep-${Date.now()}`,
                role: "agent",
                content: `Deep metadata scanning is not required for the PennPRS Agent retained recommendation. Model **${modelId}** is already displayed with the available cached evidence.`,
            },
        ]);
    };

    const handleTrainNew = () => {
        pushView("train_type_selection");
    };

    const handleDownstreamAction = (action: string) => {
        if (action.includes("Evaluate") || action.includes("Ensemble")) {
            pushView("coming_soon");
            return;
        }
        setMessages((prev) => [
            ...prev,
            {
                id: `action-${Date.now()}`,
                role: "agent",
                content: `The selected downstream action is **${action}**. This PRS Agent view keeps the recommendation workflow unchanged and hands off downstream analysis through the standard PRS-Disease interaction surface.`,
            },
        ]);
    };

    const handleModelSave = (model: ModelData, event?: MouseEvent) => {
        if (savedModels.some((saved) => saved.id === model.id)) return;

        const startPos = event
            ? { x: event.clientX, y: event.clientY }
            : { x: window.innerWidth / 2, y: window.innerHeight / 2 };

        setFlyingModel({ model, startPos });
        window.setTimeout(() => {
            setSavedModels((prev) => [model, ...prev]);
            setFlyingModel(null);
        }, 600);
        setSelectedActionModel(model);
        pushView("model_actions");
    };

    const handleModelDownload = (model: ModelData, event?: MouseEvent) => {
        if (model.download_url) {
            window.open(model.download_url, "_blank");
        }
        if (!savedModels.some((saved) => saved.id === model.id)) {
            handleModelSave(model, event);
            return;
        }
        setSelectedActionModel(model);
        pushView("model_actions");
    };

    const handleRemoveSavedModel = (modelId: string) => {
        setSavedModels((prev) => prev.filter((model) => model.id !== modelId));
    };

    const handleModeSelect = (mode: "search" | "train") => {
        if (mode === "search") {
            pushView("disease_selection");
            return;
        }
        pushView("train_type_selection");
    };

    const handleTrainTypeSelect = (type: "single" | "multi") => {
        pushView(type === "single" ? "train_config" : "train_multi_config");
    };

    const handleTrainingSubmit = async (config: TrainingConfig) => {
        setIsTrainingSubmitting(true);
        try {
            await fetch("http://localhost:8000/api/submit-training-job", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config),
            });
        } catch (error) {
            console.error("Error submitting training job:", error);
        } finally {
            setTrainingSubmitModal({
                isOpen: true,
                jobName: config.jobName,
                email: config.email,
                jobType: "single",
            });
            setIsTrainingSubmitting(false);
        }
    };

    const handleMultiAncestrySubmit = async (config: MultiAncestryTrainingConfig) => {
        setIsTrainingSubmitting(true);
        try {
            await fetch("http://localhost:8000/api/submit-training-job", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    ...config,
                    jobType: "multi",
                    ancestries: config.dataSources.map((source) => source.ancestry).join("+"),
                }),
            });
        } catch (error) {
            console.error("Error submitting multi-ancestry training job:", error);
        } finally {
            setTrainingSubmitModal({
                isOpen: true,
                jobName: config.jobName,
                email: config.email,
                jobType: "multi",
            });
            setIsTrainingSubmitting(false);
        }
    };

    return (
        <div className="flex h-screen flex-col bg-background font-sans text-foreground overflow-hidden">
            <header className="flex h-14 items-center border-b px-6 bg-white dark:bg-gray-900 z-10 shrink-0 shadow-sm">
                <div className="flex items-center gap-4 font-bold text-lg">
                    <button
                        onClick={onBack}
                        className="text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors"
                        title="Back to Modules"
                    >
                        <Home size={20} />
                    </button>
                    <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                        PennPRS Agent
                    </span>
                </div>
                <div className="ml-auto flex items-center gap-4">
                    <Link
                        href="/workplace"
                        className="rounded-md border border-zinc-200 bg-zinc-950 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-zinc-800 dark:border-zinc-700"
                    >
                        Open Research Workplace
                    </Link>
                    {activeView !== "mode_selection" && (
                        <button
                            onClick={resetToModeSelection}
                            className="text-sm font-medium text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            Start Over
                        </button>
                    )}
                    <button
                        ref={savedButtonRef}
                        onClick={() => {
                            pushView("my_models");
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

            <AnimatePresence>
                {flyingModel && savedButtonRef.current && (
                    <motion.div
                        initial={{
                            x: flyingModel.startPos.x - 20,
                            y: flyingModel.startPos.y - 20,
                            scale: 1,
                            opacity: 1,
                        }}
                        animate={{
                            x: savedButtonRef.current.getBoundingClientRect().left + savedButtonRef.current.getBoundingClientRect().width / 2 - 20,
                            y: savedButtonRef.current.getBoundingClientRect().top + savedButtonRef.current.getBoundingClientRect().height / 2 - 20,
                            scale: 0.3,
                            opacity: 0.8,
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

            <div className="flex-1 flex overflow-hidden">
                <div className="flex-[2] border-r border-gray-200 dark:border-gray-800 relative">
                    <CanvasArea
                        view={activeView}
                        trait={activeSummaryTrait}
                        models={models}
                        downstreamOps={downstreamOps}
                        moduleTitle="PennPRS Agent"
                        moduleDescription="Choose how you want to proceed with your Polygenic Risk Score recommendation workflow."
                        traitSelectionTitle="Select a Target Disease"
                        traitSelectionDescription="Select a phenotype to run the PennPRS Agent recommendation workflow."
                        searchLoadingTitle="Running PennPRS Agent..."
                        traitSelectionFlows={agentWorkflowPaths}
                        summaryTraitSwitch={
                            canSwitchTransferSummary
                                ? {
                                    active: summaryDisplayMode,
                                    sourceTrait: transferSourceTrait || "transfer source",
                                    targetTrait: agentResult?.target_trait || currentTrait || "target trait",
                                    sourceModelCount: transferTraitModels.length,
                                    targetModelCount: targetTraitModels.length,
                                    onShowSource: () => showSummaryMode("source"),
                                    onShowTarget: () => showSummaryMode("target"),
                                }
                                : null
                        }
                        onSelectDisease={(trait) => void runAgentForTrait(trait)}
                        onSelectModel={handleSelectModel}
                        onTrainNew={handleTrainNew}
                        onViewDetails={setSelectedModelDetails}
                        onDownstreamAction={handleDownstreamAction}
                        onModeSelect={handleModeSelect}
                        onBackToSelection={goBack}
                        onTrainingSubmit={handleTrainingSubmit}
                        onMultiAncestrySubmit={handleMultiAncestrySubmit}
                        onTrainTypeSelect={handleTrainTypeSelect}
                        searchProgress={searchProgress}
                        isSearchComplete={isSearchComplete}
                        onAncestrySubmit={handleAncestrySubmit}
                        activeAncestry={selectedAncestry}
                        selectedActionModel={selectedActionModel}
                        savedModels={savedModels}
                        onRemoveSavedModel={handleRemoveSavedModel}
                        onSelectSavedModel={(model) => {
                            setSelectedActionModel(model);
                            pushView("model_actions");
                        }}
                        onSaveModel={handleModelSave}
                        onGoToModelGrid={() => {
                            if (models.length > 0) {
                                pushView("model_grid");
                            } else {
                                pushView("disease_selection");
                            }
                        }}
                        canGoForward={canGoForward}
                        onGoForward={goForward}
                        isTrainingSubmitting={isTrainingSubmitting}
                    />

                    {requestError && (
                        <div className="absolute bottom-4 left-4 right-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 shadow-lg">
                            {requestError}
                        </div>
                    )}

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
                        isModelSaved={selectedModelDetails ? savedModels.some((model) => model.id === selectedModelDetails.id) : false}
                    />
                </div>

                <div className="flex-1 min-w-[320px] bg-white dark:bg-gray-900 border-l border-gray-100 dark:border-gray-800 shadow-xl z-20">
                    <AgentChatPanel
                        messages={messages}
                        input={input}
                        setInput={setInput}
                        loading={loading}
                        searchProgress={searchProgress}
                        activeProgressMessageId={activeProgressMessageId}
                        currentTrait={currentTrait}
                        onSend={handleChatSubmit}
                        onViewDetails={setSelectedModelDetails}
                        onTrainNew={handleTrainNew}
                        onDownstreamAction={handleDownstreamAction}
                        onModelDownload={handleModelDownload}
                        onModelSave={handleModelSave}
                        savedModelIds={savedModels.map((model) => model.id)}
                    />
                </div>
            </div>

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
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                                <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                                Training Job Submitted!
                            </h2>
                            <p className="text-gray-600 dark:text-gray-300 mb-4">
                                Your {trainingSubmitModal.jobType === "multi" ? "multi-ancestry" : "single-ancestry"} training job{" "}
                                <span className="font-semibold text-blue-600 dark:text-blue-400">&quot;{trainingSubmitModal.jobName}&quot;</span> has been successfully submitted.
                            </p>
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
                            <button
                                onClick={() => {
                                    setTrainingSubmitModal(null);
                                    resetToModeSelection();
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

function AgentChatPanel({
    messages,
    input,
    setInput,
    loading,
    searchProgress,
    activeProgressMessageId,
    currentTrait,
    onSend,
    onViewDetails,
    onTrainNew,
    onDownstreamAction,
    onModelDownload,
    onModelSave,
    savedModelIds,
}: {
    messages: ChatMessage[];
    input: string;
    setInput: (value: string) => void;
    loading: boolean;
    searchProgress: ProgressState | null;
    activeProgressMessageId: string | null;
    currentTrait: string | null;
    onSend: (text: string) => void;
    onViewDetails: (model: ModelData) => void;
    onTrainNew: () => void;
    onDownstreamAction: (action: string) => void;
    onModelDownload: (model: ModelData, event?: MouseEvent) => void;
    onModelSave: (model: ModelData, event?: MouseEvent) => void;
    savedModelIds: string[];
}) {
    const [showSuggestions, setShowSuggestions] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, searchProgress]);

    const submit = (text = input) => {
        if (!text.trim() || loading) return;
        onSend(text);
        setInput("");
        setShowSuggestions(false);
    };

    return (
        <div className="flex flex-col h-full relative bg-white dark:bg-gray-900">
            <div className="p-4 border-b bg-white dark:bg-gray-900 shrink-0">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <Activity className="text-blue-500" size={20} />
                    PennPRS Agent
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 scroll-smooth" ref={scrollRef}>
                <div className="space-y-6">
                    <AnimatePresence initial={false}>
                        {messages.map((message) => (
                            <motion.div
                                key={message.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <ChatBubble
                                    role={message.role}
                                    content={message.content}
                                    modelCard={message.modelCard}
                                    actions={message.actions}
                                    progress={message.id === activeProgressMessageId ? searchProgress : message.progressData}
                                    onViewDetails={onViewDetails}
                                    onTrainNew={onTrainNew}
                                    onDownstreamAction={onDownstreamAction}
                                    onModelDownload={onModelDownload}
                                    onModelSave={onModelSave}
                                    isModelSaved={message.modelCard ? savedModelIds.includes(message.modelCard.id) : false}
                                    isLoading={message.id === activeProgressMessageId && loading}
                                />
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </div>

            <div className="border-t bg-background p-4 shrink-0">
                <div className="mx-auto flex max-w-3xl gap-2 relative">
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
                                {[
                                    "I want to search for models for Alzheimer's disease",
                                    "I want to search for models for Type 2 Diabetes",
                                    "I want to search for models for Breast Cancer",
                                    "I want to search for models for Coronary Artery Disease",
                                ].map((suggestion) => (
                                    <button
                                        key={suggestion}
                                        className="w-full text-left px-4 py-3 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 text-gray-700 dark:text-gray-200"
                                        onMouseDown={(event) => {
                                            event.preventDefault();
                                            setInput(suggestion);
                                            setShowSuggestions(false);
                                        }}
                                        onClick={() => {
                                            setInput(suggestion);
                                            setShowSuggestions(false);
                                        }}
                                    >
                                        <span className="bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 p-1 rounded">
                                            <SendHorizontal className="h-3 w-3" />
                                        </span>
                                        {suggestion}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                    <Input
                        placeholder={currentTrait ? `Ask about ${currentTrait}...` : "Type a message..."}
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        onKeyDown={(event) => event.key === "Enter" && submit()}
                        onFocus={() => setShowSuggestions(true)}
                        onBlur={() => setShowSuggestions(false)}
                        disabled={loading}
                        className="flex-1"
                    />
                    <Button
                        onClick={() => submit()}
                        disabled={loading || !input.trim()}
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 shadow-md transition-all active:scale-95"
                    >
                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
                    </Button>
                </div>
                <div className="text-center text-[10px] text-gray-400 mt-2 flex flex-col gap-0.5 select-none">
                    <div>PennPRS Lab &copy; 2025</div>
                    <div className="flex items-center justify-center gap-1 opacity-60">
                        <span>Data:</span>
                        <a href="https://www.pgscatalog.org/" target="_blank" rel="noopener noreferrer" className="hover:text-blue-500 hover:underline transition-colors text-[9px]">
                            PGS Catalog
                        </a>
                        <span className="mx-0.5">•</span>
                        <span>Training:</span>
                        <a href="https://pennprs.org/" target="_blank" rel="noopener noreferrer" className="hover:text-blue-500 hover:underline transition-colors text-[9px]">
                            PennPRS
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}
