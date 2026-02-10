"use client";

import { useState, useRef, useEffect } from "react";
import { Home, Plus, Sparkles, Mic, AudioLines, Loader2, CheckCircle2, Circle, FileText, MessageSquare, PanelLeft, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ModelCard, { type ModelData } from "./ModelCard";
import SearchSummaryView from "./SearchSummaryView";

interface CoScientistPageProps {
  onBack: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

type ResearchStatus = 'idle' | 'running' | 'completed';
type StepStatus = 'queued' | 'running' | 'completed';

interface ResearchStep {
  id: string;
  title: string;
  tool: string;
  status: StepStatus;
  detail?: string;
  progressTotal?: number;
  progressFetched?: number;
}

interface ReportData {
  recommendationType: 'DIRECT_HIGH_QUALITY' | 'DIRECT_SUB_OPTIMAL' | 'CROSS_DISEASE' | 'NO_MATCH_FOUND';
  primaryRecommendation: {
    pgsId: string;
    trait: string;
    confidence: 'High' | 'Moderate' | 'Low';
    rationale: string;
  };
  directMatchEvidence: {
    modelsEvaluated: number;
    performanceSummary: string[];
    clinicalBenchmarks: string[];
  };
  crossDiseaseEvidence?: {
    sourceTrait: string;
    rgMeta: number;
    transferScore: number;
    sharedGenes: string[];
  };
  geneticGraphEvidence: Array<{
    neighborTrait: string;
    rgMeta: number;
    transferScore: number;
    bestModelId: string;
    mechanismSummary?: string;
    mechanismConfidence?: string;
    sharedGenes?: string[];
    studyPower?: { nCorrelations?: number; rgMeta?: number } | null;
  }>;
  caveats: string[];
  followUpOptions: Array<{
    label: string;
    action: string;
  }>;
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export default function CoScientistPage({ onBack }: CoScientistPageProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [researchStatus, setResearchStatus] = useState<ResearchStatus>('idle');
  const [researchSteps, setResearchSteps] = useState<ResearchStep[]>([]);
  const [report, setReport] = useState<ReportData | null>(null);
  const [isEvidenceCanvasOpen, setIsEvidenceCanvasOpen] = useState(false);
  const [canvasPrimaryModel, setCanvasPrimaryModel] = useState<ModelData | null>(null);
  const [canvasDirectModels, setCanvasDirectModels] = useState<ModelData[]>([]);
  const [canvasTrait, setCanvasTrait] = useState<string>("");
  const [primaryModelCard, setPrimaryModelCard] = useState<ModelData | null>(null);
  const [relatedModelCards, setRelatedModelCards] = useState<Record<string, ModelData | null>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const researchSessionRef = useRef(0);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const updateStepStatus = (id: string, status: StepStatus, detail?: string) => {
    setResearchSteps((prev) =>
      prev.map((step) =>
        step.id === id
          ? {
              ...step,
              status,
              detail: detail ?? step.detail
            }
          : step
      )
    );
  };

  // Map backend RecommendationReport to frontend ReportData
  const mapBackendReportToFrontend = (backendReport: any): ReportData => {
    const performanceMetrics = backendReport.direct_match_evidence?.performance_metrics || {};
    const performanceSummary: string[] = [];
    
    if (performanceMetrics.auc) {
      const auc = performanceMetrics.auc;
      performanceSummary.push(`AUC: ${auc.median || 'N/A'} (range: ${auc.min || 'N/A'} - ${auc.max || 'N/A'})`);
    }
    if (performanceMetrics.r2) {
      const r2 = performanceMetrics.r2;
      performanceSummary.push(`R²: ${r2.median || 'N/A'} (range: ${r2.min || 'N/A'} - ${r2.max || 'N/A'})`);
    }
    if (performanceMetrics.sample_size) {
      const ss = performanceMetrics.sample_size;
      performanceSummary.push(`Sample Size: ${ss.median || 'N/A'} (range: ${ss.min || 'N/A'} - ${ss.max || 'N/A'})`);
    }

    const geneticGraphEvidence = (backendReport.genetic_graph_evidence || []).map((item: any) => ({
      neighborTrait: item.neighbor_trait,
      rgMeta: item.rg_meta || 0,
      transferScore: item.transfer_score || 0,
      bestModelId: item.neighbor_best_model_id || 'N/A',
      mechanismSummary: item.mechanism_summary || undefined,
      mechanismConfidence: item.mechanism_confidence || undefined,
      sharedGenes: item.shared_genes || undefined,
      studyPower: item.study_power || null
    }));

    return {
      recommendationType: backendReport.recommendation_type,
      primaryRecommendation: backendReport.primary_recommendation ? {
        pgsId: backendReport.primary_recommendation.pgs_id || 'N/A',
        trait: backendReport.primary_recommendation.source_trait || '',
        confidence: backendReport.primary_recommendation.confidence,
        rationale: backendReport.primary_recommendation.rationale
      } : {
        pgsId: 'N/A',
        trait: '',
        confidence: 'Low' as const,
        rationale: 'No primary recommendation available'
      },
      directMatchEvidence: {
        modelsEvaluated: backendReport.direct_match_evidence?.models_evaluated || 0,
        performanceSummary,
        clinicalBenchmarks: backendReport.direct_match_evidence?.clinical_benchmarks || []
      },
      crossDiseaseEvidence: backendReport.cross_disease_evidence ? {
        sourceTrait: backendReport.cross_disease_evidence.source_trait,
        rgMeta: backendReport.cross_disease_evidence.rg_meta || 0,
        transferScore: backendReport.cross_disease_evidence.transfer_score || 0,
        sharedGenes: backendReport.cross_disease_evidence.shared_genes || []
      } : undefined,
      geneticGraphEvidence,
      caveats: backendReport.caveats_and_limitations || [],
      followUpOptions: (backendReport.follow_up_options || []).map((opt: any) => ({
        label: opt.label,
        action: opt.action
      }))
    };
  };

  const extractPreviewModelsFromBackend = (backendReport: any) => {
    const primaryPreview = backendReport?.primary_model_preview || null;
    const directPreview = backendReport?.direct_models_preview || [];
    const relatedPreview = backendReport?.related_models_preview || [];

    const relatedMap: Record<string, ModelData | null> = {};
    if (Array.isArray(relatedPreview)) {
      for (const item of relatedPreview) {
        const trait = item?.neighbor_trait;
        if (!trait) continue;
        relatedMap[trait] = item?.best_model_preview || null;
      }
    }

    return {
      primaryPreview,
      directPreview: Array.isArray(directPreview) ? directPreview : [],
      relatedMap,
    };
  };

  const fetchModelCard = async (pgsId: string, signal?: AbortSignal): Promise<ModelData | null> => {
    if (!pgsId || pgsId === "N/A") return null;
    try {
      const res = await fetch("http://localhost:8000/pgs/model_card", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pgs_id: pgsId }),
        signal
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  };

  const openEvidenceCanvas = async (backendReport: any, reportData: ReportData, signal?: AbortSignal) => {
    const trait = reportData.primaryRecommendation?.trait || backendReport?.target_trait || "";
    setCanvasTrait(trait);
    setIsEvidenceCanvasOpen(true);

    // Primary model card
    const primaryPgsId = reportData.primaryRecommendation?.pgsId;
    const primary = await fetchModelCard(primaryPgsId, signal);
    setCanvasPrimaryModel(primary);

    // Direct model list for canvas (best-effort: use backend direct_models if available)
    const directModels = backendReport?.direct_models?.models || backendReport?.direct_models?.hits || [];
    const directIds: string[] = Array.isArray(directModels)
      ? directModels.map((m: any) => m?.id).filter(Boolean)
      : [];
    const uniqueIds = Array.from(new Set(directIds)).slice(0, 25);

    if (uniqueIds.length === 0) {
      setCanvasDirectModels([]);
      return;
    }

    const cards: ModelData[] = [];
    for (const pid of uniqueIds) {
      const card = await fetchModelCard(pid, signal);
      if (card) cards.push(card);
    }
    setCanvasDirectModels(cards);
  };

  const startResearch = async (query: string) => {
    const sessionId = researchSessionRef.current + 1;
    researchSessionRef.current = sessionId;

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new AbortController for this request
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setResearchStatus("running");
    setReport(null);
    setIsEvidenceCanvasOpen(false);
    setCanvasPrimaryModel(null);
    setCanvasDirectModels([]);
    setCanvasTrait("");
    setPrimaryModelCard(null);
    setRelatedModelCards({});

    // Generate request ID for progress tracking
    const requestId = crypto.randomUUID();

    // User-friendly step definitions - only show first step initially
    const allSteps: ResearchStep[] = [
      {
        id: "step-1",
        title: "Searching PRS models",
        tool: "",
        status: "queued",
        detail: `Looking for models related to "${query}"`
      },
      {
        id: "step-2",
        title: "Analyzing performance",
        tool: "",
        status: "queued",
        detail: "Evaluating AUC, R², and sample sizes"
      },
      {
        id: "step-3",
        title: "Reviewing clinical standards",
        tool: "",
        status: "queued",
        detail: "Checking PRS reporting standards and thresholds"
      },
      {
        id: "step-4",
        title: "Exploring genetic relationships",
        tool: "",
        status: "queued",
        detail: "Finding genetically correlated traits"
      },
      {
        id: "step-5",
        title: "Validating biological mechanisms",
        tool: "",
        status: "queued",
        detail: "Identifying shared genes and biological pathways"
      },
      {
        id: "step-final",
        title: "Generating report",
        tool: "",
        status: "queued",
        detail: "Compiling recommendations and evidence"
      }
    ];

    // Start with only the first step visible, but mark it as running immediately
    // so the progress bar shows up right away
    // IMPORTANT: Don't set progressTotal/progressFetched here - wait for backend to provide them
    setResearchSteps([{
      ...allSteps[0],
      status: "running" as StepStatus,
      progressTotal: undefined,
      progressFetched: undefined
    }]);

    // Map backend step names to frontend step IDs
    const stepMapping: Record<string, string> = {
      "step-1": "step-1",
      "step-2": "step-2",
      "step-3": "step-3",
      "step-4": "step-4",
      "step-5": "step-5",
      "step-final": "step-final"
    };

    // Start polling for real progress
    // Clear any existing polling interval
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    
    pollIntervalRef.current = setInterval(async () => {
      // Check if this session is still active
      if (researchSessionRef.current !== sessionId || abortController.signal.aborted) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return;
      }

      try {
        // Check if request was aborted before fetching progress
        if (abortController.signal.aborted || researchSessionRef.current !== sessionId) {
          return;
        }
        
        const progressRes = await fetch(`http://localhost:8000/agent/search_progress/${requestId}`, {
          signal: abortController.signal
        });
        
        // Check again after fetch
        if (abortController.signal.aborted || researchSessionRef.current !== sessionId) {
          return;
        }
        
        if (progressRes.ok) {
          const progress = await progressRes.json();
          
          // Check again after JSON parsing
          if (abortController.signal.aborted || researchSessionRef.current !== sessionId) {
            return;
          }
          
          if (progress.status === "unknown") {
            return; // Not initialized yet
          }
          
          // Debug: Log progress for step-1 to help diagnose issues
          if (progress.current_step === "step-1" || (progress.total !== undefined && progress.total > 0)) {
            console.log("[Progress Debug] step-1 progress:", {
              current_step: progress.current_step,
              total: progress.total,
              fetched: progress.fetched,
              current_action: progress.current_action,
              status: progress.status
            });
          }

          // Update current step based on backend progress
          const currentStep = progress.current_step;
          if (currentStep && stepMapping[currentStep]) {
            const stepId = stepMapping[currentStep];
            
            setResearchSteps((prev) => {
              const currentStepIndex = allSteps.findIndex(s => s.id === stepId);
              const newSteps: ResearchStep[] = [];
              const modelsTotal = progress.models_total;
              const modelsFetched = progress.models_fetched;
              
              // Add steps up to and including current step
              for (let i = 0; i <= currentStepIndex; i++) {
                const step = allSteps[i];
                
                // Skip step-4 and step-5 unless we're at step-4 or beyond
                if ((step.id === "step-4" || step.id === "step-5") && currentStepIndex < 3) {
                  continue; // Don't show genetic graph steps until step-4 is reached
                }
                
                // Check if step already exists
                const existingIndex = prev.findIndex(s => s.id === step.id);
                if (existingIndex >= 0) {
                  // Update existing step
                  const existingStep = prev[existingIndex];
                  if (i === currentStepIndex) {
                    // Current step: mark as running and update progress if step-1
                    const updatedStep: ResearchStep = {
                      ...existingStep,
                      status: "running" as StepStatus,
                      detail: progress.current_action || existingStep.detail
                    };
                    if (stepId === "step-1") {
                      // Step-1 progress should use model-level fields only.
                      if (modelsTotal !== undefined && modelsFetched !== undefined && modelsTotal > 0) {
                        updatedStep.progressTotal = modelsTotal;
                        updatedStep.progressFetched = modelsFetched;
                      }
                    }
                    newSteps.push(updatedStep);
                  } else {
                    // Previous steps: mark as completed
                    newSteps.push({
                      ...existingStep,
                      status: "completed" as StepStatus
                    });
                  }
                } else {
                  // Add new step
                  if (i === currentStepIndex) {
                    const newStep: ResearchStep = {
                      ...step,
                      status: "running" as StepStatus,
                      detail: progress.current_action || step.detail
                    };
                    if (stepId === "step-1") {
                      if (modelsTotal !== undefined && modelsFetched !== undefined && modelsTotal > 0) {
                        newStep.progressTotal = modelsTotal;
                        newStep.progressFetched = modelsFetched;
                      }
                    }
                    // If no progress data yet, step will still be marked as running (progress bar will show "Initializing...")
                    newSteps.push(newStep);
                  } else {
                    newSteps.push({
                      ...step,
                      status: "completed" as StepStatus
                    });
                  }
                }
              }
              
              return newSteps;
            });
          }
          
          // Update step-1 model hydration progress whenever model fields exist.
          if (progress.models_total !== undefined && progress.models_fetched !== undefined && progress.models_total > 0) {
            setResearchSteps((prev) => {
              const step1Index = prev.findIndex(s => s.id === "step-1");
              if (step1Index >= 0) {
                return prev.map((step, idx) => {
                  if (idx === step1Index) {
                    // Always update progress when we have valid model data
                    return {
                      ...step,
                      progressTotal: progress.models_total!,
                      progressFetched: progress.models_fetched!,
                      status: step.status === "queued" ? "running" as StepStatus : step.status,
                      detail: progress.current_action || step.detail
                    };
                  }
                  return step;
                });
              }
              // If step-1 doesn't exist yet but we have progress data, create it
              if (prev.length === 0 || !prev.some(s => s.id === "step-1")) {
                const step1 = allSteps.find(s => s.id === "step-1");
                if (step1) {
                  return [{
                    ...step1,
                    status: "running" as StepStatus,
                    progressTotal: progress.models_total!,
                    progressFetched: progress.models_fetched!,
                    detail: progress.current_action || step1.detail
                  }];
                }
              }
              return prev;
            });
          }
          
          // Ensure step-1 is marked as running when current_step is step-1, even if progress data isn't ready yet
          if (progress.current_step === "step-1") {
            setResearchSteps((prev) => {
              const step1Index = prev.findIndex(s => s.id === "step-1");
              if (step1Index >= 0) {
                return prev.map((step, idx) => {
                  if (idx === step1Index && step.status === "queued") {
                    // Mark as running if it's still queued
                    return {
                      ...step,
                      status: "running" as StepStatus,
                      detail: progress.current_action || step.detail
                    };
                  }
                  return step;
                });
              }
              return prev;
            });
          }

            // If completed, mark all steps as completed and stop polling
            if (progress.status === "completed") {
              if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
              }
              setResearchSteps((prev) => 
                prev.map(step => {
                  if (step.id === "step-1") {
                    // Finalize step-1 using model-level progress fields.
                    const finalTotal = progress.models_total ?? step.progressTotal;
                    const finalFetched = progress.models_fetched ?? step.progressFetched;
                    return {
                      ...step,
                      status: "completed" as StepStatus,
                      progressTotal: finalTotal,
                      // If we have a total, step-1 must be completed by now.
                      progressFetched: (finalTotal !== undefined && finalTotal > 0)
                        ? finalTotal
                        : finalFetched,
                      detail: undefined
                    }
                  }
                  return {
                    ...step,
                    status: "completed" as StepStatus,
                    detail: undefined // Clear detail for all completed steps
                  };
                })
              );
              setResearchStatus("completed");
            }
        }
      } catch (e) {
        // Ignore abort errors (expected when request is cancelled)
        if (e instanceof Error && e.name === 'AbortError') {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          return;
        }
        // Ignore other polling errors
      }
    }, 800); // Poll every 800ms to reduce backend log spam

    try {
      // Call real backend API with request_id and abort signal
      const response = await fetch("http://localhost:8000/agent/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trait: query, request_id: requestId }),
        signal: abortController.signal
      });

      if (!response.ok) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        throw new Error(`API Error: ${response.statusText}`);
      }

      // Check if request was aborted before processing response
      if (abortController.signal.aborted || researchSessionRef.current !== sessionId) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return null;
      }
      
      const backendReport = await response.json();
      
      // Check again after JSON parsing (in case it was aborted during parsing)
      if (abortController.signal.aborted || researchSessionRef.current !== sessionId) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return null;
      }
      
      // Stop polling immediately after receiving response
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      
      // Immediately mark all steps as completed since we have the report
      setResearchSteps((prev) => 
        prev.map(step => {
          // For step-1, clear detail but keep actual progress values
          if (step.id === "step-1") {
            const total = step.progressTotal;
            return {
              ...step,
              status: "completed" as StepStatus,
              // Ensure step-1 doesn't get stuck at e.g. 53/56 due to polling stop race.
              progressFetched: (total !== undefined && total > 0) ? total : step.progressFetched,
              detail: undefined // Clear detail when completed
            };
          }
          return {
            ...step,
            status: "completed" as StepStatus,
            detail: undefined // Clear detail for all completed steps
          };
        })
      );
      
      // Determine which steps actually ran based on recommendation type
      const ranCrossDisease = backendReport.recommendation_type !== "DIRECT_HIGH_QUALITY";
      
      // Update steps based on actual workflow
      if (!ranCrossDisease) {
        // If direct high quality, remove cross-disease steps
        setResearchSteps((prev) => prev.filter(step => step.id !== "step-4" && step.id !== "step-5"));
      }

      // Map backend report to frontend format
      const reportData = mapBackendReportToFrontend(backendReport);
      setReport(reportData);

      // Prefer server-provided previews (faster, fewer round-trips).
      const previews = extractPreviewModelsFromBackend(backendReport);
      if (previews.primaryPreview) {
        setPrimaryModelCard(previews.primaryPreview);
      } else {
        const primary = await fetchModelCard(reportData.primaryRecommendation?.pgsId, abortController.signal);
        setPrimaryModelCard(primary);
      }

      if (Object.keys(previews.relatedMap).length > 0) {
        setRelatedModelCards(previews.relatedMap);
      } else {
        // Backward-compatible fallback.
        const relatedEntries = reportData.geneticGraphEvidence || [];
        const relatedMap: Record<string, ModelData | null> = {};
        for (const e of relatedEntries) {
          if (!e.bestModelId || e.bestModelId === "N/A") {
            relatedMap[e.neighborTrait] = null;
            continue;
          }
          relatedMap[e.neighborTrait] = await fetchModelCard(e.bestModelId, abortController.signal);
        }
        setRelatedModelCards(relatedMap);
      }

      // Evidence canvas inputs
      setCanvasTrait(query);
      setCanvasDirectModels(previews.directPreview);
      setCanvasPrimaryModel(previews.primaryPreview);

      setResearchStatus("completed");
      setIsLoading(false);
      return reportData;
    } catch (error) {
      // Ignore abort errors (they're expected when user cancels)
      if (error instanceof Error && error.name === 'AbortError') {
        console.log("Request was cancelled");
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return null;
      }
      
      console.error("Error calling recommendation API:", error);
      
      // Stop polling on error
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      
      // Mark all steps as completed even on error
      setResearchSteps((prev) => 
        prev.map(step => ({
          ...step,
          status: "completed" as StepStatus,
          detail: step.status === "running" 
            ? `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
            : step.detail
        }))
      );
      
      setResearchStatus("completed");
      
      // Return a fallback report
      const fallbackReport: ReportData = {
        recommendationType: "NO_MATCH_FOUND",
        primaryRecommendation: {
          pgsId: "N/A",
          trait: query,
          confidence: "Low",
          rationale: "Error occurred while fetching recommendations. Please try again."
        },
        directMatchEvidence: {
          modelsEvaluated: 0,
          performanceSummary: [],
          clinicalBenchmarks: []
        },
        geneticGraphEvidence: [],
        caveats: ["API call failed. Please check your connection and try again."],
        followUpOptions: []
      };
      setReport(fallbackReport);
      return fallbackReport;
    }
  };

  const handleTrainNew = (query: string) => {
    const message: Message = {
      id: (Date.now() + 2).toString(),
      role: "assistant",
      content: `Training configuration for "${query}" will be generated in the next step.`,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, message]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const query = input.trim();
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    const reportData = await startResearch(query);
    if (!reportData) {
      setIsLoading(false);
      return;
    }

    // Don't add completion message - report will be displayed directly
    setIsLoading(false);
  };

  const handleNewChat = () => {
    // Cancel ongoing research by incrementing session ID
    researchSessionRef.current += 1000; // Large increment to ensure all ongoing requests are cancelled
    
    // Abort any ongoing API request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // Clear polling interval
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    
    // Reset all state
    setMessages([]);
    setInput("");
    setIsLoading(false);
    setResearchStatus("idle");
    setResearchSteps([]);
    setReport(null);
  };


  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Get greeting based on co-scientist persona
  const getGreeting = () => {
    return "What PRS model are you looking for?";
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 overflow-hidden">
      {/* Left Sidebar - Narrow */}
      <aside className="w-12 flex flex-col items-center py-4 border-r border-slate-800 bg-slate-900/50">
        {/* Home Button */}
        <button
          onClick={onBack}
          className="w-10 h-10 rounded-lg hover:bg-slate-800 flex items-center justify-center transition-colors mb-4"
          title="Back to home"
        >
          <Home className="w-5 h-5" />
        </button>
        
        {/* New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-10 h-10 rounded-lg hover:bg-slate-800 flex items-center justify-center transition-colors"
          title="New chat"
        >
          <MessageSquare className="w-5 h-5" />
        </button>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 pt-8 pb-40">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full max-w-3xl mx-auto -mt-20">
              {/* Central Prompt Text */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-center mb-8"
              >
                <h1 className="text-2xl font-semibold mb-2 flex items-center gap-2 justify-center">
                  <Sparkles className="w-5 h-5 text-blue-500" />
                  {getGreeting()}
                </h1>
                <p className="text-slate-400 text-sm">
                  I'm your PennPRS co-scientist. How can I help you today?
                </p>
              </motion.div>
              
              {/* Floating Input Bar - Centered */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="w-full"
              >
                <div className="relative bg-[#2F2F2F] rounded-[28px] ring-1 ring-white/10 shadow-[0_18px_60px_rgba(0,0,0,0.55)]">
                  <div className="flex items-center gap-4 px-5 py-3">
                    {/* Left: Plus icon */}
                    <button
                      className="p-1.5 hover:bg-white/10 rounded-full transition-colors flex-shrink-0"
                      aria-label="Add"
                      type="button"
                    >
                      <Plus className="w-5 h-5 text-white" />
                    </button>
                    
                    {/* Center: Text input */}
                    <div className="flex-1 relative min-w-0">
                      <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask anything"
                        className="w-full bg-transparent border-0 text-white placeholder-slate-400 text-base focus:outline-none resize-none min-h-[22px] max-h-[96px] leading-6"
                        rows={1}
                        style={{
                          height: 'auto',
                          minHeight: '22px',
                        }}
                        onInput={(e) => {
                          const target = e.target as HTMLTextAreaElement;
                          target.style.height = 'auto';
                          target.style.height = `${Math.min(target.scrollHeight, 96)}px`;
                        }}
                      />
                    </div>
                    
                    {/* Right: Icons */}
                    <div className="flex items-center gap-3 flex-shrink-0">
                      {/* Microphone icon */}
                      <button
                        className="p-2 hover:bg-white/10 rounded-full transition-colors flex-shrink-0"
                        aria-label="Voice input"
                        type="button"
                      >
                        <Mic className="w-5 h-5 text-white" />
                      </button>

                      {/* White circular action button (waveform) */}
                      <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        className="w-10 h-10 rounded-full bg-white hover:bg-slate-200 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors flex items-center justify-center flex-shrink-0"
                        aria-label="Send"
                      >
                        <AudioLines className="w-5 h-5 text-black" />
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          ) : (
            <div className={`${isEvidenceCanvasOpen ? "max-w-6xl" : "max-w-3xl"} mx-auto space-y-4 pt-6`}>
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className={`${message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}
                  >
                    {message.role === 'user' ? (
                      // User message: wrapped in bubble (ChatGPT-like)
                      <div className="max-w-[85%] rounded-lg px-3 py-2 bg-slate-800 text-slate-100">
                        <p className="whitespace-pre-wrap text-base leading-relaxed">{message.content}</p>
                      </div>
                    ) : (
                      // Assistant message: no bubble, just text (ChatGPT-like)
                      <div className="max-w-[85%] text-slate-200">
                        <p className="whitespace-pre-wrap text-base leading-relaxed">{message.content}</p>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="text-slate-200">
                    <div className="flex gap-1">
                      <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                      <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                    </div>
                  </div>
                </motion.div>
              )}

              {researchStatus !== "idle" && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-base font-semibold text-slate-200">
                    <FileText className="w-4 h-4 text-blue-400" />
                    Deep Research Trace
                    {researchStatus === "running" ? (
                      <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin ml-2" />
                    ) : (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 ml-2" />
                    )}
                  </div>
                  <div className="border-l border-slate-800 pl-4 space-y-3">
                    {researchSteps.map((step) => (
                      <div key={step.id} className="relative">
                        <div className="absolute -left-[22px] top-1.5">
                          {step.status === "running" && (
                            <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />
                          )}
                          {step.status === "completed" && (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          )}
                          {step.status === "queued" && (
                            <Circle className="w-3.5 h-3.5 text-slate-600" />
                          )}
                        </div>
                        <div className="text-base font-medium text-slate-100">{step.title}</div>
                        {step.detail && step.status !== "completed" && (
                          <div className="text-sm text-slate-400 mt-0.5">{step.detail}</div>
                        )}
                        {/* Sub-progress bar for step-1 - show when running or completed */}
                        {step.id === "step-1" && step.status !== "queued" && (
                          <div className="mt-2 space-y-1">
                            <div className="flex justify-between items-center text-sm">
                              <span className={step.status === "completed" ? "text-emerald-400" : "text-slate-400"}>
                                {step.status === "completed" ? "PRS models search completed" : "Searching PRS models..."}
                              </span>
                              {step.progressTotal !== undefined && step.progressFetched !== undefined && step.progressTotal > 0 ? (
                                <span className={`font-mono ${step.status === "completed" ? "text-emerald-400" : "text-slate-400"}`}>
                                  {step.progressFetched} / {step.progressTotal} Models
                                </span>
                              ) : (
                                <span className="text-slate-500 text-xs">Initializing...</span>
                              )}
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                              {step.progressTotal !== undefined && step.progressFetched !== undefined && step.progressTotal > 0 ? (
                                <div
                                  className={`h-1.5 rounded-full transition-all duration-300 ease-out ${
                                    step.status === "completed" ? "bg-emerald-500" : "bg-blue-500"
                                  }`}
                                  style={{ 
                                    width: `${Math.min(100, Math.max(0, (step.progressFetched / step.progressTotal) * 100))}%`
                                  }}
                                />
                              ) : (
                                <div className="h-1.5 rounded-full bg-blue-500 animate-pulse" style={{ width: "0%" }} />
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {report && (
                <div className="space-y-4">
                  {/* Report Header */}
                  <div className="flex items-center gap-3">
                    <h2 className="text-lg font-semibold text-slate-100">PRS Recommendation Report</h2>
                    {/* Intentionally hide internal workflow labels for user-friendliness */}
                  </div>
                  
                  {/* Report Content - No borders, clean layout like ChatGPT */}
                  <div className="space-y-5 text-base text-slate-300 leading-relaxed">
                    {/* Primary Recommendation */}
                    {report.primaryRecommendation && report.primaryRecommendation.pgsId !== 'N/A' && (
                      <div className="space-y-2">
                        <h3 className="text-base font-semibold text-slate-100">Primary Recommendation</h3>
                        {primaryModelCard ? (
                          <div className="max-w-[420px]">
                            <ModelCard
                              model={primaryModelCard}
                              onSelect={() => {}}
                              onViewDetails={() => {}}
                            />
                          </div>
                        ) : (
                          <div className="text-sm text-slate-400">
                            Loading model preview...
                          </div>
                        )}
                        {/* Keep reasoning for now */}
                        {report.primaryRecommendation.rationale && (
                          <div className="pt-2">
                            <h4 className="text-sm font-semibold text-slate-200">Reasoning</h4>
                            <p className="mt-1 text-slate-300">{report.primaryRecommendation.rationale}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Evidence Details -> interactive button that opens canvas */}
                    {report.directMatchEvidence && report.directMatchEvidence.modelsEvaluated > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-base font-semibold text-slate-100">Evidence</h3>
                        <button
                          type="button"
                          onClick={() => {
                            setIsEvidenceCanvasOpen(true);
                          }}
                          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors text-sm"
                        >
                          <PanelLeft className="w-4 h-4" />
                          View evidence details
                        </button>
                      </div>
                    )}

                    {/* Cross-Disease Evidence */}
                    {report.crossDiseaseEvidence && (
                      <div className="space-y-2">
                        <h3 className="text-base font-semibold text-slate-100">Cross-Disease Transfer Evidence</h3>
                        <div className="space-y-2">
                          <p>
                            Found related trait: <span className="font-semibold text-slate-200">{report.crossDiseaseEvidence.sourceTrait}</span>
                          </p>
                          <div className="grid grid-cols-2 gap-4">
                            <p>
                              <span className="font-semibold text-slate-200">Genetic correlation (rg):</span> {report.crossDiseaseEvidence.rgMeta.toFixed(3)}
                            </p>
                            <p>
                              <span className="font-semibold text-slate-200">Transfer score:</span> {report.crossDiseaseEvidence.transferScore.toFixed(3)}
                            </p>
                          </div>
                          {report.crossDiseaseEvidence.sharedGenes.length > 0 && (
                            <p>
                              <span className="font-semibold text-slate-200">Shared genes:</span> {report.crossDiseaseEvidence.sharedGenes.join(", ")}
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Genetic Graph Evidence */}
                    {report.geneticGraphEvidence.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-base font-semibold text-slate-100">Related Traits PRS Model</h3>
                        <div className="space-y-3">
                          {report.geneticGraphEvidence.map((item, idx) => (
                            <div key={idx} className="space-y-2">
                              <div className="text-sm font-semibold text-slate-200">{item.neighborTrait}</div>

                              {relatedModelCards[item.neighborTrait] ? (
                                <div className="max-w-[420px]">
                                  <ModelCard
                                    model={relatedModelCards[item.neighborTrait] as ModelData}
                                    onSelect={() => {}}
                                    onViewDetails={() => {}}
                                  />
                                </div>
                              ) : (
                                <div className="text-sm text-slate-400">
                                  Loading model preview...
                                </div>
                              )}

                              <div className="text-sm text-slate-400 leading-relaxed">
                                {item.mechanismSummary ? (
                                  <p>
                                    Evidence suggests shared biology supported by Open Targets / PheWAS. {item.mechanismSummary}
                                    {item.sharedGenes && item.sharedGenes.length > 0 ? (
                                      <> Key shared genes include <span className="font-mono">{item.sharedGenes.slice(0, 6).join(", ")}</span>.</>
                                    ) : null}
                                  </p>
                                ) : (
                                  <p>
                                    Evidence is supported by genetic correlation and transfer scoring; biological mechanism evidence is limited for this trait pair.
                                  </p>
                                )}
                                {item.studyPower?.nCorrelations ? (
                                  <p className="mt-1">
                                    Study support: aggregated from {item.studyPower.nCorrelations} correlation pairs (meta rg {item.studyPower.rgMeta?.toFixed?.(3) ?? "N/A"}).
                                  </p>
                                ) : null}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Caveats */}
                    {report.caveats.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-base font-semibold text-slate-100">Caveats & Limitations</h3>
                        <ul className="list-disc list-inside space-y-1">
                          {report.caveats.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Follow-up Options */}
                    {report.followUpOptions.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-base font-semibold text-slate-100">Next Steps</h3>
                        <ul className="list-disc list-inside space-y-1">
                          {report.followUpOptions.map((item, idx) => (
                            <li key={idx}>{item.label}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Split canvas overlay (left canvas, right chat) */}
              {isEvidenceCanvasOpen && (
                <div className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm">
                  <div className="absolute inset-6 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex">
                    {/* Left canvas */}
                    <div className="flex-[2] border-r border-slate-800 bg-slate-950/40 overflow-y-auto">
                      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
                        <div className="text-sm font-semibold text-slate-100">Evidence Canvas</div>
                        <button
                          type="button"
                          onClick={() => setIsEvidenceCanvasOpen(false)}
                          className="p-2 rounded-lg hover:bg-slate-800 text-slate-200"
                          title="Close canvas"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="p-4 space-y-6">
                        {canvasPrimaryModel && (
                          <div>
                            <div className="text-sm font-semibold text-slate-200 mb-2">Summary</div>
                            <div className="max-w-[520px]">
                              <ModelCard model={canvasPrimaryModel} onSelect={() => {}} onViewDetails={() => {}} />
                            </div>
                          </div>
                        )}
                        {canvasDirectModels.length > 0 && canvasTrait && (
                          <div>
                            <div className="text-sm font-semibold text-slate-200 mb-2">Direct Models</div>
                            <div className="bg-slate-900/40 border border-slate-800 rounded-xl">
                              <SearchSummaryView
                                trait={canvasTrait}
                                models={canvasDirectModels}
                                onAncestrySubmit={() => {}}
                              />
                            </div>
                          </div>
                        )}
                        {canvasDirectModels.length === 0 && (
                          <div className="text-sm text-slate-400">
                            Direct model list is not available for this report yet.
                          </div>
                        )}
                      </div>
                    </div>
                    {/* Right: real conversation panel (read-only mirror) */}
                    <div className="flex-1 bg-slate-900 overflow-y-auto">
                      <div className="px-4 py-3 border-b border-slate-800 text-sm font-semibold text-slate-100">
                        Conversation
                      </div>
                      <div className="p-4 space-y-3">
                        {messages.map((message) => (
                          <div
                            key={`canvas-${message.id}`}
                            className={`${message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}
                          >
                            {message.role === 'user' ? (
                              <div className="max-w-[90%] rounded-lg px-3 py-2 bg-slate-800 text-slate-100">
                                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                              </div>
                            ) : (
                              <div className="max-w-[90%] text-slate-200">
                                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                              </div>
                            )}
                          </div>
                        ))}
                        {isLoading && (
                          <div className="flex justify-start text-slate-400 text-sm">
                            Thinking...
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area - Only show when messages exist */}
        {messages.length > 0 && (
          <>
            {/* Soft fade like ChatGPT behind the floating bar */}
            <div className="pointer-events-none fixed inset-x-0 bottom-0 z-10 h-24 bg-gradient-to-t from-slate-900 to-transparent" />

            {/* Floating input bar (does NOT occupy a full bottom panel) */}
            <div className="fixed inset-x-0 bottom-4 z-20">
              <div className="max-w-3xl mx-auto px-4">
                <div className="relative bg-[#2F2F2F] rounded-[28px] ring-1 ring-white/10 shadow-[0_18px_60px_rgba(0,0,0,0.55)]">
                  <div className="flex items-center gap-3 px-4 py-2.5">
                    {/* Left: Plus icon */}
                    <button
                      className="p-1 hover:bg-white/10 rounded-full transition-colors flex-shrink-0"
                      aria-label="Add"
                      type="button"
                    >
                      <Plus className="w-4 h-4 text-white" />
                    </button>

                    {/* Center: Text input */}
                    <div className="flex-1 relative min-w-0">
                      <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask anything"
                        className="w-full bg-transparent border-0 text-white placeholder-slate-400 text-sm focus:outline-none resize-none min-h-[20px] max-h-[96px] leading-5"
                        rows={1}
                        style={{
                          height: 'auto',
                          minHeight: '20px',
                        }}
                        onInput={(e) => {
                          const target = e.target as HTMLTextAreaElement;
                          target.style.height = 'auto';
                          target.style.height = `${Math.min(target.scrollHeight, 96)}px`;
                        }}
                      />
                    </div>

                    {/* Right: Icons */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <button
                        className="p-1.5 hover:bg-white/10 rounded-full transition-colors flex-shrink-0"
                        aria-label="Voice input"
                        type="button"
                      >
                        <Mic className="w-4 h-4 text-white" />
                      </button>

                      <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        className="w-8 h-8 rounded-full bg-white hover:bg-slate-200 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors flex items-center justify-center flex-shrink-0"
                        aria-label="Send"
                      >
                        <AudioLines className="w-4 h-4 text-black" />
                      </button>
                    </div>
                  </div>
                </div>

                <p className="text-center text-xs text-slate-500 mt-2">
                  PennPRS co-scientist can make mistakes. Check important info.
                </p>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
