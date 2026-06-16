"use client";

import { type FormEvent, type ReactNode, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Archive,
  ArrowDownToLine,
  BarChart3,
  Bot,
  Braces,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleDot,
  Database,
  Dna,
  FileText,
  FlaskConical,
  Folder,
  Globe2,
  Layers,
  Loader2,
  MessageSquarePlus,
  PanelLeft,
  Play,
  Search,
  Settings,
  Sparkles,
  TerminalSquare,
  TrendingUp,
  User,
  Users,
  Zap,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type AgentMode = "cached" | "live";
type ChatRole = "assistant" | "user";
type DetailPanel = "inventory" | "landscape" | "candidates" | "reasoning" | "warnings" | "provenance" | "exports" | "training";
type RunStatus = "running" | "completed" | "failed";

type ReasoningStep = {
  id: string;
  title: string;
  detail: string;
};

type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
  run?: {
    id: string;
    trait: string;
    mode: AgentMode;
    status: RunStatus;
    activeStage: number;
    response?: AgentResponse;
    backendTrace?: AgentTraceStep[];
    error?: string;
  };
  response?: AgentResponse;
  variant?: "normal" | "error";
};

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

interface ModelPreview {
  id?: string | null;
  name?: string | null;
  trait?: string | null;
  ancestry?: string | null;
  method?: string | null;
  source?: string | null;
  num_variants?: number | null;
  sample_size?: number | null;
  metrics?: {
    AUC?: number | string | null;
    R2?: number | string | null;
    [key: string]: unknown;
  };
}

interface SameTraitResult {
  status: string;
  resolved_trait?: string | null;
  recommendation_type?: string | null;
  pgs_id?: string | null;
  confidence?: string | null;
  rationale?: string | null;
  models_evaluated?: number | null;
  model_preview?: ModelPreview | null;
  model_previews?: ModelPreview[] | null;
}

interface TransferResult {
  status: string;
  source_trait?: string | null;
  pgs_id?: string | null;
  confidence?: string | null;
  rationale?: string | null;
  model_previews?: ModelPreview[] | null;
  trace_summary?: Record<string, unknown> | null;
}

interface FinalRecommendation {
  recommendation_source: "same_trait" | "cross_trait_transfer" | "none";
  recommended_pgs_id?: string | null;
  recommended_trait?: string | null;
  confidence?: string | null;
  summary: string;
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

interface MetricStats {
  count: number;
  min: number;
  median: number;
  max: number;
}

interface LandscapeBucket {
  label: string;
  count: number;
  percent: number;
}

interface LandscapePoint {
  model: ModelPreview;
  auc: number | null;
  r2: number | null;
  sampleSize: number | null;
  x: number;
  y: number;
  size: number;
  isRecommended: boolean;
}

interface ModelLandscape {
  totalModels: number;
  recommendedModel: ModelPreview | null;
  recommendedRankByAuc: number | null;
  auc: MetricStats | null;
  r2: MetricStats | null;
  sampleSize: MetricStats | null;
  variants: MetricStats | null;
  ancestries: LandscapeBucket[];
  methods: LandscapeBucket[];
  sources: LandscapeBucket[];
  completeness: LandscapeBucket[];
  points: LandscapePoint[];
}

const RECOMMEND_ENDPOINT = "/api/pennprs-agent/recommend";
const REQUEST_TIMEOUT_MS = 20_000;

const EXAMPLES = [
  { label: "Breast carcinoma", trait: "breast carcinoma", path: "Direct" },
  { label: "Late-onset Alzheimer", trait: "late-onset Alzheimer's disease", path: "Transfer check" },
  { label: "Bipolar disorder", trait: "bipolar disorder", path: "Transfer check" },
  { label: "Coronary artery disease", trait: "coronary artery disease", path: "Direct" },
];

const SAVED_RUNS = [
  { label: "Alzheimer fallback review", meta: "transfer check", active: true },
  { label: "Breast carcinoma baseline", meta: "same-trait" },
  { label: "Bipolar transfer review", meta: "transfer" },
  { label: "CAD baseline comparison", meta: "same-trait" },
];

const DETAIL_TABS: Array<{ id: DetailPanel; label: string; icon: LucideIcon }> = [
  { id: "inventory", label: "Model inventory", icon: Database },
  { id: "landscape", label: "Performance landscape", icon: BarChart3 },
  { id: "candidates", label: "Candidate tradeoffs", icon: Layers },
  { id: "reasoning", label: "Decision rationale", icon: Sparkles },
  { id: "warnings", label: "Warnings", icon: AlertTriangle },
  { id: "provenance", label: "Provenance", icon: Archive },
  { id: "exports", label: "Exports", icon: ArrowDownToLine },
  { id: "training", label: "Training job", icon: FlaskConical },
];

const REASONING_STEPS: ReasoningStep[] = [
  {
    id: "frame",
    title: "Frame the scientific question",
    detail: "Resolve the requested phenotype and decide whether this is primarily a same-trait PRS selection problem or a case that may need cross-trait transfer.",
  },
  {
    id: "inventory",
    title: "Read the PRS model inventory",
    detail: "Before answering, inspect how many candidate models are visible and which fields are complete: performance, ancestry, sample size, variants, method, and source.",
  },
  {
    id: "landscape",
    title: "Look for separable quality signals",
    detail: "Use the performance landscape to see whether one candidate is clearly better, whether metrics are sparse, and whether the selected model is an evidence outlier or a conservative fallback.",
  },
  {
    id: "tradeoffs",
    title: "Compare candidate tradeoffs",
    detail: "Prefer phenotype fidelity first, then comparable PRS-only performance, ancestry portability, method context, and validation evidence; do not let a single metric dominate.",
  },
  {
    id: "finalize",
    title: "Decide with caveats visible",
    detail: "Only after the evidence review, apply the sufficiency gate and transfer check, then state the final recommendation with caveats and downstream actions.",
  },
];

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "welcome",
    role: "assistant",
    text:
      "Ask for a PRS recommendation by target trait. I will first open the model inventory and evidence landscape, then show the visible reasoning notes, and only then return the final recommendation.",
  },
];

function labelize(value?: string | null) {
  if (!value) return "N/A";
  return value.replace(/_/g, " ");
}

function metricValue(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) return value.toFixed(value < 1 ? 3 : 0);
  if (typeof value === "string" && value.trim()) return value;
  return "N/A";
}

function statusTone(status: AgentTraceStep["status"]) {
  if (status === "completed") return "bg-emerald-400";
  if (status === "failed") return "bg-red-400";
  if (status === "skipped") return "bg-zinc-500";
  return "bg-amber-400";
}

function collectModels(response: AgentResponse | null) {
  if (!response) return [];
  const models = [
    response.same_trait_result.model_preview,
    ...(response.same_trait_result.model_previews || []),
    ...(response.transfer_result?.model_previews || []),
  ].filter(Boolean) as ModelPreview[];

  const seen = new Set<string>();
  return models.filter((model) => {
    const id = model.id || model.name;
    if (!id || seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

function coerceMetricNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function formatCompactNumber(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "N/A";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(value >= 10_000 ? 0 : 1)}k`;
  if (value > 0 && value < 1) return value.toFixed(3);
  return value.toLocaleString();
}

function metricStats(values: Array<number | null>): MetricStats | null {
  const numeric = values.filter((value): value is number => value !== null && Number.isFinite(value));
  if (!numeric.length) return null;
  const sorted = [...numeric].sort((a, b) => a - b);
  return {
    count: sorted.length,
    min: sorted[0],
    median: sorted[Math.floor(sorted.length / 2)],
    max: sorted[sorted.length - 1],
  };
}

function bucketize(labels: string[], total: number): LandscapeBucket[] {
  const counts = new Map<string, number>();
  labels.forEach((label) => {
    const clean = label.trim() || "Unknown";
    counts.set(clean, (counts.get(clean) || 0) + 1);
  });

  return Array.from(counts.entries())
    .map(([label, count]) => ({
      label,
      count,
      percent: total > 0 ? (count / total) * 100 : 0,
    }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
}

function ancestryBucketsForModel(model: ModelPreview) {
  const raw = model.ancestry || "";
  const normalized = raw.toLowerCase();
  const buckets = [
    { code: "EUR", patterns: ["eur", "european"] },
    { code: "AFR", patterns: ["afr", "african"] },
    { code: "EAS", patterns: ["eas", "east asian"] },
    { code: "SAS", patterns: ["sas", "south asian"] },
    { code: "AMR", patterns: ["amr", "hispanic", "admixed american"] },
    { code: "MIX", patterns: ["mix", "multi", "other", "multiple"] },
  ];
  const matched = buckets.filter((bucket) => bucket.patterns.some((pattern) => normalized.includes(pattern))).map((bucket) => bucket.code);
  if (matched.length) return Array.from(new Set(matched));
  if (raw.trim() && raw !== "N/A") return [raw.trim()];
  return ["Unknown"];
}

function computeModelLandscape(models: ModelPreview[], response: AgentResponse): ModelLandscape {
  const total = models.length;
  const finalId = response.final_recommendation.recommended_pgs_id;
  const modelId = (model: ModelPreview) => model.id || model.name || "";
  const recommendedModel = models.find((model) => modelId(model) === finalId) || models[0] || null;
  const aucValues = models.map((model) => coerceMetricNumber(model.metrics?.AUC));
  const r2Values = models.map((model) => coerceMetricNumber(model.metrics?.R2));
  const sampleValues = models.map((model) => coerceMetricNumber(model.sample_size));
  const variantValues = models.map((model) => coerceMetricNumber(model.num_variants));
  const aucSorted = [...models]
    .filter((model) => coerceMetricNumber(model.metrics?.AUC) !== null)
    .sort((a, b) => (coerceMetricNumber(b.metrics?.AUC) || 0) - (coerceMetricNumber(a.metrics?.AUC) || 0));
  const recommendedRankByAuc = finalId ? aucSorted.findIndex((model) => modelId(model) === finalId) + 1 : 0;
  const maxSample = Math.max(1, ...sampleValues.filter((value): value is number => value !== null));
  const maxR2 = Math.max(0.01, ...r2Values.filter((value): value is number => value !== null));

  return {
    totalModels: total,
    recommendedModel,
    recommendedRankByAuc: recommendedRankByAuc > 0 ? recommendedRankByAuc : null,
    auc: metricStats(aucValues),
    r2: metricStats(r2Values),
    sampleSize: metricStats(sampleValues),
    variants: metricStats(variantValues),
    ancestries: bucketize(models.flatMap(ancestryBucketsForModel), Math.max(total, 1)).slice(0, 6),
    methods: bucketize(models.map((model) => model.method || "Unknown"), Math.max(total, 1)).slice(0, 6),
    sources: bucketize(models.map((model) => model.source || "Unknown"), Math.max(total, 1)).slice(0, 4),
    completeness: [
      { label: "AUC", count: aucValues.filter((value) => value !== null).length, percent: total ? (aucValues.filter((value) => value !== null).length / total) * 100 : 0 },
      { label: "R2", count: r2Values.filter((value) => value !== null).length, percent: total ? (r2Values.filter((value) => value !== null).length / total) * 100 : 0 },
      {
        label: "Sample size",
        count: sampleValues.filter((value) => value !== null).length,
        percent: total ? (sampleValues.filter((value) => value !== null).length / total) * 100 : 0,
      },
      { label: "Variants", count: variantValues.filter((value) => value !== null).length, percent: total ? (variantValues.filter((value) => value !== null).length / total) * 100 : 0 },
    ],
    points: models.map((model, index) => {
      const auc = coerceMetricNumber(model.metrics?.AUC);
      const r2 = coerceMetricNumber(model.metrics?.R2);
      const sampleSize = coerceMetricNumber(model.sample_size);
      const fallbackX = total > 1 ? (index / (total - 1)) * 84 + 8 : 50;
      const x = auc !== null ? Math.max(6, Math.min(94, ((auc - 0.5) / 0.5) * 88 + 6)) : fallbackX;
      const y = r2 !== null ? Math.max(8, Math.min(88, 92 - (r2 / maxR2) * 76)) : 74;
      const size = sampleSize !== null ? Math.max(9, Math.min(24, 8 + Math.sqrt(sampleSize / maxSample) * 16)) : 10;
      return {
        model,
        auc,
        r2,
        sampleSize,
        x,
        y,
        size,
        isRecommended: !!finalId && modelId(model) === finalId,
      };
    }),
  };
}

function downloadText(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function toMarkdown(response: AgentResponse) {
  const final = response.final_recommendation;
  const same = response.same_trait_result;
  const transfer = response.transfer_result;
  return [
    `# PennPRS Agent Recommendation: ${response.target_trait}`,
    "",
    `- Mode: ${response.mode}`,
    `- Final source: ${labelize(final.recommendation_source)}`,
    `- Recommended PGS: ${final.recommended_pgs_id || "N/A"}`,
    `- Recommended trait: ${final.recommended_trait || "N/A"}`,
    `- Confidence: ${final.confidence || "N/A"}`,
    "",
    "## Summary",
    final.summary,
    "",
    "## Same-trait result",
    `- Status: ${same.status}`,
    `- PGS: ${same.pgs_id || "N/A"}`,
    `- Quality gate: ${response.same_trait_quality_assessment.accept_direct_baseline ? "accepted" : "rejected"}`,
    `- Rationale: ${same.rationale || "N/A"}`,
    "",
    "## Transfer result",
    `- Status: ${transfer?.status || "not run"}`,
    `- Source trait: ${transfer?.source_trait || "N/A"}`,
    `- PGS: ${transfer?.pgs_id || "N/A"}`,
    `- Rationale: ${transfer?.rationale || "N/A"}`,
    "",
    "## Warnings",
    ...(response.warnings.length ? response.warnings.map((warning) => `- ${warning}`) : ["- None"]),
  ].join("\n");
}

function toCsv(models: ModelPreview[]) {
  const rows = [
    ["pgs_id", "trait", "ancestry", "method", "source", "auc", "r2", "variants", "sample_size"],
    ...models.map((model) => [
      model.id || model.name || "",
      model.trait || "",
      model.ancestry || "",
      model.method || "",
      model.source || "",
      String(model.metrics?.AUC || ""),
      String(model.metrics?.R2 || ""),
      String(model.num_variants || ""),
      String(model.sample_size || ""),
    ]),
  ];
  return rows.map((row) => row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(",")).join("\n");
}

function nextMessageId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function sleep(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export default function PennPRSWorkplace() {
  const [targetTrait, setTargetTrait] = useState("late-onset Alzheimer's disease");
  const [mode, setMode] = useState<AgentMode>("cached");
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [selectedPanel, setSelectedPanel] = useState<DetailPanel>("inventory");
  const [isRunning, setIsRunning] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [requestError, setRequestError] = useState<string | null>(null);
  const scrollAnchorRef = useRef<HTMLDivElement | null>(null);

  const models = useMemo(() => collectModels(result), [result]);
  const warningCount = (result?.warnings.length || 0) + (result?.errors.length || 0);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ block: "end" });
  }, [messages, isRunning]);

  const runRecommendation = async (trait = targetTrait) => {
    const cleanTrait = trait.trim();
    if (!cleanTrait || isRunning) return;
    const runMode: AgentMode = "cached";

    setTargetTrait(cleanTrait);
    setMode(runMode);
    setIsRunning(true);
    setRequestError(null);
    setSelectedPanel("inventory");
    const runId = nextMessageId("run");
    setMessages((current) => [
      ...current,
      { id: nextMessageId("user"), role: "user", text: cleanTrait },
      {
        id: runId,
        role: "assistant",
        text: "I’ll inspect the PRS model inventory first, then compare the evidence and show the reasoning notes before the final recommendation.",
        run: {
          id: runId,
          trait: cleanTrait,
          mode: runMode,
          status: "running",
          activeStage: 0,
        },
      },
    ]);

    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
      const requestPromise = fetch(RECOMMEND_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_trait: cleanTrait, mode: runMode }),
        signal: controller.signal,
      }).finally(() => window.clearTimeout(timeoutId));

      for (let index = 0; index < REASONING_STEPS.length; index += 1) {
        setMessages((current) =>
          current.map((message) =>
            message.id === runId && message.run
              ? { ...message, run: { ...message.run, activeStage: index, status: "running" } }
              : message
          )
        );
        await sleep(520);
      }

      const response = await requestPromise;

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Request failed with status ${response.status}`);
      }

      const payload = (await response.json()) as AgentResponse;
      setResult(payload);
      setMessages((current) => [
        ...current.map((message) =>
          message.id === runId && message.run
            ? {
                ...message,
                text: "PRS evidence review complete. The model summary, landscape, and tradeoff notes are ready; the final recommendation follows after them.",
                run: {
                  ...message.run,
                  status: "completed" as RunStatus,
                  activeStage: REASONING_STEPS.length - 1,
                  response: payload,
                  backendTrace: payload.agent_trace_steps,
                },
              }
            : message
        ),
        {
          id: nextMessageId("assistant"),
          role: "assistant",
          text: "Recommendation ready. Open the sections below to inspect the evidence behind the answer or hand the selected model to training.",
          response: payload,
        },
      ]);
    } catch (error) {
      const message =
        error instanceof DOMException && error.name === "AbortError"
          ? "Cached PennPRS Agent request timed out after 20 seconds. Check that the local backend is responding on 127.0.0.1:8000."
          : error instanceof Error
            ? error.message
            : "PennPRS Agent request failed.";
      setResult(null);
      setRequestError(message);
      setMessages((current) =>
        current.map((item) =>
          item.id === runId && item.run
            ? {
                ...item,
                text: "Evidence review stopped before a final recommendation could be returned.",
                variant: "error",
                run: { ...item.run, status: "failed", error: message },
              }
            : item
        )
      );
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void runRecommendation();
  };

  const startNewChat = () => {
    setMessages(INITIAL_MESSAGES);
    setResult(null);
    setRequestError(null);
    setSelectedPanel("inventory");
  };

  return (
    <main className="flex h-screen overflow-hidden bg-[#1f1f1f] text-zinc-100">
      {sidebarOpen && (
        <>
          <button
            type="button"
            aria-label="Close sidebar overlay"
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          />
          <ConversationHistory
            activeTrait={targetTrait}
            onNewChat={startNewChat}
            onRunExample={(trait) => void runRecommendation(trait)}
          />
        </>
      )}

      <section className="flex min-w-0 flex-1 flex-col">
        <TopBar sidebarOpen={sidebarOpen} onToggleSidebar={() => setSidebarOpen((open) => !open)} />

        <div className="flex min-h-0 flex-1 flex-col">
          <div className="min-h-0 flex-1 overflow-y-auto px-4 py-5">
            <div className="mx-auto flex w-full max-w-[980px] flex-col gap-5">
              {messages.map((message) => (
                <ChatBubble
                  key={message.id}
                  message={message}
                  selectedPanel={selectedPanel}
                  onSelectPanel={(panel) => setSelectedPanel((current) => (current === panel ? panel : panel))}
                />
              ))}

              {isRunning && <div className="ml-11 text-xs text-zinc-500">PennPRS Agent is still working locally...</div>}
              <div ref={scrollAnchorRef} />
            </div>
          </div>

          <Composer
            value={targetTrait}
            mode={mode}
            disabled={isRunning}
            requestError={requestError}
            onChange={setTargetTrait}
            onModeChange={setMode}
            onSubmit={handleSubmit}
          />
        </div>
      </section>

      <RunInspector result={result} models={models} warningCount={warningCount} />
    </main>
  );
}

function ConversationHistory({
  activeTrait,
  onNewChat,
  onRunExample,
}: {
  activeTrait: string;
  onNewChat: () => void;
  onRunExample: (trait: string) => void;
}) {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-[280px] shrink-0 flex-col border-r border-zinc-800 bg-[#262625] px-3 py-3 text-sm text-zinc-300 lg:static lg:z-auto">
      <div className="mb-4 flex h-8 items-center gap-2 px-2">
        <span className="size-3 rounded-full bg-zinc-500" />
        <span className="size-3 rounded-full bg-zinc-500" />
        <span className="size-3 rounded-full bg-zinc-500" />
        <span className="ml-3 rounded border border-zinc-700 px-1.5 py-0.5 text-[10px] text-zinc-500">local</span>
      </div>

      <nav className="flex flex-col gap-1">
        <SidebarAction icon={MessageSquarePlus} label="New recommendation" onClick={onNewChat} />
        <SidebarAction icon={Search} label="Trait search" />
        <SidebarAction icon={Settings} label="Credential setup" />
        <SidebarAction icon={Archive} label="Local result cache" />
      </nav>

      <section className="mt-6">
        <SidebarHeading>Local run history</SidebarHeading>
        <div className="mt-2 flex flex-col gap-1">
          {SAVED_RUNS.map((thread) => (
            <button
              key={thread.label}
              type="button"
              className={cn(
                "flex items-center gap-2 rounded-lg px-2 py-2 text-left text-zinc-400 hover:bg-zinc-700/40 hover:text-zinc-100",
                thread.active && "bg-zinc-700/50 text-zinc-100"
              )}
            >
              <Archive className="size-3.5" />
              <span className="min-w-0 flex-1 truncate">{thread.label}</span>
              <span className="text-xs text-zinc-500">{thread.meta}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="mt-5">
        <SidebarHeading>Demo validation traits</SidebarHeading>
        <div className="mt-2 rounded-lg px-2 py-2">
          <div className="flex items-center gap-2 text-zinc-300">
            <Folder className="size-4" />
            Cached evaluation set
          </div>
          <div className="mt-2 flex flex-col gap-1 pl-6">
            {EXAMPLES.map((example) => (
              <button
                key={example.trait}
                type="button"
                onClick={() => onRunExample(example.trait)}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2 py-1.5 text-left text-zinc-400 hover:bg-zinc-700/40 hover:text-zinc-100",
                  activeTrait === example.trait && "bg-zinc-700/50 text-zinc-100"
                )}
              >
                <span className="min-w-0 flex-1 truncate">{example.label}</span>
                <span className="text-xs text-zinc-500">{example.path}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <div className="mt-auto flex flex-col gap-1 border-t border-zinc-800 pt-3">
        <SidebarAction icon={Settings} label="Settings" />
        <div className="flex items-center gap-2 px-2 py-2 text-xs text-zinc-500">
          <Globe2 className="size-3.5" />
          Local-first workplace
        </div>
      </div>
    </aside>
  );
}

function SidebarHeading({ children }: { children: string }) {
  return <div className="px-2 text-xs font-medium uppercase tracking-wide text-zinc-500">{children}</div>;
}

function SidebarAction({ icon: Icon, label, onClick }: { icon: LucideIcon; label: string; onClick?: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-2 rounded-lg px-2 py-2 text-left text-zinc-300 hover:bg-zinc-700/40 hover:text-zinc-100"
    >
      <Icon className="size-4 text-zinc-400" />
      {label}
    </button>
  );
}

function TopBar({ sidebarOpen, onToggleSidebar }: { sidebarOpen: boolean; onToggleSidebar: () => void }) {
  return (
    <header className="flex h-12 shrink-0 items-center border-b border-zinc-800 bg-[#2b2b2a] px-4">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={onToggleSidebar}
        className="mr-2 size-8 rounded-md text-zinc-400 hover:bg-zinc-700 hover:text-zinc-100"
        title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
      >
        <PanelLeft className="size-4" />
      </Button>
      <Link href="/" className="text-sm font-semibold text-zinc-100">
        PennPRS Agent
      </Link>
      <span className="ml-2 text-zinc-500">...</span>
      <div className="ml-auto hidden items-center gap-2 text-xs text-zinc-500 md:flex">
        <Zap className="size-3.5" />
        <span>Local research workspace</span>
        <span className="rounded-md border border-zinc-700 bg-zinc-800 px-2 py-1 text-zinc-300">/workplace</span>
      </div>
    </header>
  );
}

function ChatBubble({
  message,
  selectedPanel,
  onSelectPanel,
}: {
  message: ChatMessage;
  selectedPanel: DetailPanel;
  onSelectPanel: (panel: DetailPanel) => void;
}) {
  const isUser = message.role === "user";

  return (
    <article className={cn("flex gap-3", isUser && "justify-end")}>
      {!isUser && (
        <div className="mt-1 flex size-8 shrink-0 items-center justify-center rounded-full border border-zinc-700 bg-[#30302f]">
          <Bot className="size-4 text-zinc-300" />
        </div>
      )}

      <div className={cn("min-w-0 max-w-[860px]", isUser && "flex max-w-[720px] flex-row-reverse gap-3")}>
        {isUser && (
          <div className="mt-1 flex size-8 shrink-0 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800">
            <User className="size-4 text-zinc-300" />
          </div>
        )}
        <div
          className={cn(
            "rounded-2xl border px-4 py-3 text-sm leading-6",
            isUser
              ? "border-zinc-700 bg-[#3a3a39] text-zinc-100"
              : "border-zinc-800 bg-transparent text-zinc-300",
            message.variant === "error" && "border-red-900 bg-red-950/30 text-red-200"
          )}
        >
          <p>{message.text}</p>
          {message.run && <ReasoningTraceMessage run={message.run} />}
          {message.response && (
            <RecommendationCard response={message.response} selectedPanel={selectedPanel} onSelectPanel={onSelectPanel} />
          )}
        </div>
      </div>
    </article>
  );
}

function ReasoningTraceMessage({ run }: { run: NonNullable<ChatMessage["run"]> }) {
  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-zinc-700 bg-[#2d2d2c]">
      <div className="flex items-start justify-between gap-4 border-b border-zinc-700 p-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
            {run.status === "running" ? <Loader2 className="size-3.5 animate-spin" /> : <CheckCircle2 className="size-3.5" />}
            PRS evidence review
          </div>
          <div className="mt-2 text-sm font-semibold text-zinc-100">{run.trait}</div>
          <div className="mt-1 text-xs text-zinc-500">
            {run.mode} mode · evidence first, answer last
          </div>
        </div>
        <span
          className={cn(
            "rounded-md border px-2 py-1 text-xs capitalize",
            run.status === "completed"
              ? "border-emerald-900 bg-emerald-950/30 text-emerald-200"
              : run.status === "failed"
                ? "border-red-900 bg-red-950/30 text-red-200"
                : "border-zinc-700 bg-[#252524] text-zinc-300"
          )}
        >
          {run.status}
        </span>
      </div>

      <div className="flex flex-col gap-3 p-4">
        {run.response ? (
          <EvidenceReviewCard response={run.response} />
        ) : (
          <RunningReasoningPreview run={run} />
        )}

        {run.backendTrace?.length ? (
          <div className="rounded-lg border border-zinc-700 bg-[#252524] p-3">
            <div className="text-xs font-medium uppercase tracking-wide text-zinc-500">Evidence that supports the reasoning</div>
            <div className="mt-2 flex flex-col gap-2">
              {run.backendTrace.map((step) => (
                <div key={step.id} className="flex gap-2 text-xs text-zinc-400">
                  <span className={cn("mt-1.5 size-1.5 rounded-full", statusTone(step.status))} />
                  <span className="font-medium text-zinc-300">{step.title}</span>
                  <span className="truncate text-zinc-500">{step.detail}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {run.error && <div className="rounded-lg border border-red-900 bg-red-950/30 p-3 text-sm text-red-200">{run.error}</div>}
      </div>
    </div>
  );
}

function RunningReasoningPreview({ run }: { run: NonNullable<ChatMessage["run"]> }) {
  return (
    <>
      <div className="text-xs font-medium uppercase tracking-wide text-zinc-500">Visible reasoning notes</div>
      {REASONING_STEPS.map((stage, index) => {
        const isCompleted = run.status === "completed" || index < run.activeStage;
        const isRunning = run.status === "running" && index === run.activeStage;
        const isFailed = run.status === "failed" && index >= run.activeStage;
        return (
          <div key={stage.id} className="flex gap-3 rounded-lg border border-zinc-700 bg-[#252524] p-3">
            <span
              className={cn(
                "mt-1 flex size-5 shrink-0 items-center justify-center rounded-full border",
                isCompleted && "border-emerald-500 bg-emerald-500/20 text-emerald-200",
                isRunning && "border-zinc-500 bg-zinc-700 text-zinc-100",
                isFailed && "border-red-700 bg-red-950/40 text-red-200",
                !isCompleted && !isRunning && !isFailed && "border-zinc-700 text-zinc-600"
              )}
            >
              {isRunning ? <Loader2 className="size-3 animate-spin" /> : isCompleted ? <CheckCircle2 className="size-3" /> : index + 1}
            </span>
            <div className="min-w-0">
              <div className="text-sm font-medium text-zinc-100">{stage.title}</div>
              <p className="mt-1 text-xs leading-5 text-zinc-500">{reasoningDetailForStep(stage, run)}</p>
            </div>
          </div>
        );
      })}
      {run.status === "running" && run.activeStage >= REASONING_STEPS.length - 1 ? (
        <div className="rounded-lg border border-zinc-700 bg-[#252524] p-3 text-xs leading-5 text-zinc-500">
          Waiting for the cached local API response through {RECOMMEND_ENDPOINT}. No live runner is being used.
        </div>
      ) : null}
    </>
  );
}

function reasoningDetailForStep(stage: ReasoningStep, run: NonNullable<ChatMessage["run"]>) {
  const response = run.response;
  if (!response || run.status !== "completed") return stage.detail;

  const final = response.final_recommendation;
  const same = response.same_trait_result;
  const transfer = response.transfer_result;

  if (stage.id === "frame") {
    return `I interpret the request as selecting a PRS for ${response.target_trait}; direct same-trait evidence gets priority unless quality or transfer evidence gives a stronger reason to switch.`;
  }

  if (stage.id === "inventory") {
    return `The visible inventory contains ${collectModels(response).length || same.models_evaluated || 0} candidate model preview(s); I check metric completeness and ancestry/method coverage before treating any PGS ID as a recommendation.`;
  }

  if (stage.id === "landscape") {
    return `The performance landscape is used as supporting evidence, not as a single scoreboard; sparse AUC/R2 fields or inconsistent sample metadata lower confidence.`;
  }

  if (stage.id === "tradeoffs") {
    return response.same_trait_quality_assessment.accept_direct_baseline
      ? `The same-trait baseline ${same.pgs_id || final.recommended_pgs_id || "candidate"} passes the quality gate, so transfer evidence does not need to override it.`
      : `The same-trait baseline ${same.pgs_id || "candidate"} is useful but not cleanly sufficient; I check whether transfer evidence can improve the answer.`;
  }

  if (stage.id === "finalize") {
    return final.recommendation_source === "cross_trait_transfer"
      ? `Transfer evidence changes the answer: ${transfer?.pgs_id || final.recommended_pgs_id || "the transfer candidate"} is selected, with ${response.warnings.length + response.errors.length} caveat(s) visible.`
      : `Transfer evidence does not override the retained candidate; ${final.recommended_pgs_id || "the selected PGS"} remains the final recommendation with ${final.confidence || "reported"} confidence and visible caveats.`;
  }

  return stage.detail;
}

function EvidenceReviewCard({ response }: { response: AgentResponse }) {
  const models = collectModels(response);

  return (
    <div className="flex flex-col gap-3">
      <AnalysisStageCard
        eyebrow="Evidence first"
        title="PRS model inventory summary"
        icon={Database}
        defaultOpen
        status="complete"
      >
        <ModelSummaryViz response={response} models={models} />
      </AnalysisStageCard>

      <AnalysisStageCard
        eyebrow="Evidence shape"
        title="Performance landscape"
        icon={BarChart3}
        defaultOpen={models.length <= 5}
        status="complete"
      >
        <ModelLandscapePanel response={response} models={models} compact />
      </AnalysisStageCard>

      <AnalysisStageCard
        eyebrow="Selection pressure"
        title="Candidate tradeoffs"
        icon={Layers}
        defaultOpen
        status="complete"
      >
        <CandidateTradeoffMatrix response={response} models={models} compact />
      </AnalysisStageCard>

      <AnalysisStageCard
        eyebrow="Visible reasoning notes"
        title="Why the answer is not returned immediately"
        icon={Sparkles}
        defaultOpen
        status="complete"
      >
        <ReasoningNotes response={response} />
      </AnalysisStageCard>

      <AnalysisStageCard
        eyebrow="Risk control"
        title="Warnings and caveats before use"
        icon={AlertTriangle}
        defaultOpen={(response.warnings.length + response.errors.length) > 0}
        status={(response.warnings.length + response.errors.length) > 0 ? "attention" : "complete"}
      >
        <CaveatPreview response={response} />
      </AnalysisStageCard>
    </div>
  );
}

function AnalysisStageCard({
  eyebrow,
  title,
  icon: Icon,
  defaultOpen = false,
  status,
  children,
}: {
  eyebrow: string;
  title: string;
  icon: LucideIcon;
  defaultOpen?: boolean;
  status: "complete" | "attention";
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="overflow-hidden rounded-xl border border-zinc-700 bg-[#252524]">
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-zinc-800/60"
      >
        <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg border border-zinc-700 bg-[#30302f]">
          <Icon className="size-4 text-zinc-300" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-medium uppercase tracking-wide text-zinc-500">{eyebrow}</span>
            <span
              className={cn(
                "rounded-full px-2 py-0.5 text-[11px]",
                status === "attention" ? "bg-amber-950/50 text-amber-200" : "bg-emerald-950/40 text-emerald-200"
              )}
            >
              {status === "attention" ? "needs review" : "complete"}
            </span>
          </div>
          <div className="mt-1 text-sm font-semibold text-zinc-100">{title}</div>
        </div>
        {open ? <ChevronDown className="mt-1 size-4 text-zinc-500" /> : <ChevronRight className="mt-1 size-4 text-zinc-500" />}
      </button>
      {open && <div className="border-t border-zinc-700 p-3">{children}</div>}
    </section>
  );
}

function RecommendationCard({
  response,
  selectedPanel,
  onSelectPanel,
}: {
  response: AgentResponse;
  selectedPanel: DetailPanel;
  onSelectPanel: (panel: DetailPanel) => void;
}) {
  const models = collectModels(response);
  const final = response.final_recommendation;
  const transferActive = final.recommendation_source === "cross_trait_transfer";
  const warningCount = response.warnings.length + response.errors.length;

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-zinc-700 bg-[#2d2d2c]">
      <div className="border-b border-zinc-700 p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
              <CheckCircle2 className="size-3.5" />
              Final recommendation
            </div>
            <h2 className="font-mono text-2xl font-semibold text-zinc-50">{final.recommended_pgs_id || "No PGS"}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-300">{final.summary}</p>
          </div>
          <div className="rounded-lg border border-zinc-700 bg-[#252524] px-3 py-2 text-right">
            <div className="text-xs text-zinc-500">source</div>
            <div className={cn("text-sm font-semibold", transferActive ? "text-sky-300" : "text-emerald-300")}>
              {labelize(final.recommendation_source)}
            </div>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
          <Metric label="Target" value={response.target_trait} />
          <Metric label="Trait" value={final.recommended_trait || "N/A"} />
          <Metric label="Confidence" value={final.confidence || "N/A"} />
          <Metric label="Mode" value={response.mode} />
        </div>
      </div>

      <div className="grid grid-cols-1 border-b border-zinc-700 sm:grid-cols-3">
        <DecisionCell
          label="Same-trait baseline"
          value={response.same_trait_result.pgs_id || "N/A"}
          detail={response.same_trait_quality_assessment.accept_direct_baseline ? "quality gate accepted" : "quality gate rejected"}
        />
        <DecisionCell
          label="Cross-trait transfer"
          value={response.transfer_result?.pgs_id || "N/A"}
          detail={response.transfer_result?.source_trait || "not final path"}
        />
        <DecisionCell label="Flags" value={String(warningCount)} detail={`${models.length} candidate models`} />
      </div>

      <div className="flex flex-wrap gap-2 border-b border-zinc-700 p-3">
        {DETAIL_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onSelectPanel(tab.id)}
            className={cn(
              "flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition-colors",
              selectedPanel === tab.id
                ? "border-zinc-500 bg-zinc-700 text-zinc-50"
                : "border-zinc-700 bg-[#252524] text-zinc-400 hover:border-zinc-600 hover:text-zinc-100"
            )}
          >
            <tab.icon className="size-3.5" />
            {tab.label}
            {selectedPanel === tab.id ? <ChevronDown className="size-3.5" /> : <ChevronRight className="size-3.5" />}
          </button>
        ))}
      </div>

      <ExpandableDetail panel={selectedPanel} response={response} models={models} />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#252524] p-3">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 truncate text-sm font-medium text-zinc-100">{value}</div>
    </div>
  );
}

function DecisionCell({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="border-b border-zinc-700 p-4 last:border-b-0 sm:border-r sm:border-b-0 sm:last:border-r-0">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 truncate font-mono text-sm font-semibold text-zinc-100">{value}</div>
      <div className="mt-1 truncate text-xs text-zinc-500">{detail}</div>
    </div>
  );
}

function ExpandableDetail({
  panel,
  response,
  models,
}: {
  panel: DetailPanel;
  response: AgentResponse;
  models: ModelPreview[];
}) {
  if (panel === "inventory") {
    return (
      <DetailShell title="PRS model inventory summary">
        <ModelSummaryViz response={response} models={models} expanded />
      </DetailShell>
    );
  }

  if (panel === "landscape") {
    return (
      <DetailShell title="Performance landscape">
        <ModelLandscapePanel response={response} models={models} expanded />
      </DetailShell>
    );
  }

  if (panel === "candidates") {
    return (
      <DetailShell title="Candidate tradeoffs">
        <CandidateTradeoffMatrix response={response} models={models} />
      </DetailShell>
    );
  }

  if (panel === "reasoning") {
    return (
      <DetailShell title="Decision rationale">
        <div className="grid gap-3 md:grid-cols-2">
          <EvidenceBlock
            title="Final answer"
            value={response.final_recommendation.recommended_pgs_id || "N/A"}
            body={response.final_recommendation.summary}
          />
          <EvidenceBlock
            title="Quality gate"
            value={response.same_trait_quality_assessment.accept_direct_baseline ? "accepted" : "rejected"}
            body={response.same_trait_quality_assessment.rationale || "No quality-gate rationale returned."}
          />
          <EvidenceBlock
            title="Same-trait baseline"
            value={response.same_trait_result.pgs_id || "N/A"}
            body={response.same_trait_result.rationale || "No same-trait rationale returned."}
          />
          <EvidenceBlock
            title="Cross-trait transfer"
            value={response.transfer_result?.pgs_id || "N/A"}
            body={response.transfer_result?.rationale || "No transfer rationale returned."}
          />
        </div>
        <div className="mt-3">
          <ReasoningNotes response={response} showBackendTrace />
        </div>
      </DetailShell>
    );
  }

  if (panel === "warnings") {
    const items = [...response.warnings, ...response.errors];
    return (
      <DetailShell title="Warnings and caveats">
        {items.length ? (
          <div className="flex flex-col gap-2">
            {items.map((item) => (
              <div key={item} className="rounded-lg border border-amber-900/70 bg-amber-950/30 p-3 text-sm leading-6 text-amber-100">
                {item}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">No warnings returned for this run.</p>
        )}
      </DetailShell>
    );
  }

  if (panel === "provenance") {
    return (
      <DetailShell title="Provenance">
        <div className="flex flex-col gap-2">
          {response.artifacts_used.map((artifact, index) => (
            <div key={`${artifact.path}-${index}`} className="rounded-lg border border-zinc-700 bg-[#252524] p-3">
              <div className="text-sm font-medium text-zinc-200">{String(artifact.name || "Artifact")}</div>
              <div className="mt-1 break-all font-mono text-xs leading-5 text-zinc-500">{String(artifact.path || "")}</div>
            </div>
          ))}
        </div>
      </DetailShell>
    );
  }

  if (panel === "exports") {
    return (
      <DetailShell title="Export result">
        <div className="grid gap-2 sm:grid-cols-3">
          <ExportButton
            icon={Braces}
            label="Export JSON"
            onClick={() =>
              downloadText(`pennprs-agent-${response.target_trait}.json`, JSON.stringify(response, null, 2), "application/json")
            }
          />
          <ExportButton
            icon={FileText}
            label="Export Markdown"
            onClick={() => downloadText(`pennprs-agent-${response.target_trait}.md`, toMarkdown(response), "text/markdown")}
          />
          <ExportButton
            icon={ArrowDownToLine}
            label="Export candidates CSV"
            onClick={() => downloadText(`pennprs-agent-${response.target_trait}-candidates.csv`, toCsv(models), "text/csv")}
          />
        </div>
      </DetailShell>
    );
  }

  return (
    <DetailShell title="Training job">
      <TrainingJobActions response={response} />
    </DetailShell>
  );
}

function ModelSummaryViz({
  response,
  models,
  expanded = false,
}: {
  response: AgentResponse;
  models: ModelPreview[];
  expanded?: boolean;
}) {
  const landscape = computeModelLandscape(models, response);
  const finalId = response.final_recommendation.recommended_pgs_id || "N/A";

  if (!models.length) {
    return (
      <div className="rounded-xl border border-zinc-700 bg-[#252524] p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
          <BarChart3 className="size-4 text-zinc-400" />
          PRS model summary viz
        </div>
        <p className="mt-2 text-sm leading-6 text-zinc-500">
          No candidate model previews were returned, so the PRS-Disease model inventory summary cannot be reconstructed for this run.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-zinc-700 bg-[#252524] p-4">
      <div className="flex flex-col gap-3 border-b border-zinc-700 pb-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
            <BarChart3 className="size-4 text-zinc-400" />
            PRS model summary viz
          </div>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-zinc-500">
            Migrated from PRS-Disease as a pre-decision inventory view: counts, metadata completeness, ancestry coverage, method mix, source mix, and metric availability. It is not the final recommendation.
          </p>
        </div>
        <div className="rounded-lg border border-zinc-700 bg-[#30302f] px-3 py-2 text-xs">
          <div className="text-zinc-500">recommended</div>
          <div className="mt-1 font-mono font-semibold text-zinc-100">{finalId}</div>
          <div className="mt-1 text-zinc-500">
            {landscape.recommendedRankByAuc ? `AUC rank ${landscape.recommendedRankByAuc}/${landscape.auc?.count || landscape.totalModels}` : "rank unavailable"}
          </div>
        </div>
      </div>

      <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        <LandscapeStat icon={Database} label="Candidate models" value={String(landscape.totalModels)} sublabel={`${landscape.sources.length} source group(s)`} />
        <LandscapeStat icon={TrendingUp} label="AUC median" value={landscape.auc ? landscape.auc.median.toFixed(3) : "N/A"} sublabel={`${landscape.auc?.count || 0} with AUC`} />
        <LandscapeStat icon={Users} label="Sample median" value={landscape.sampleSize ? formatCompactNumber(landscape.sampleSize.median) : "N/A"} sublabel={`${landscape.sampleSize?.count || 0} with sample size`} />
        <LandscapeStat icon={Layers} label="Variant median" value={landscape.variants ? formatCompactNumber(landscape.variants.median) : "N/A"} sublabel={`${landscape.variants?.count || 0} with variants`} />
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-2">
        <MetricDistributionStrip
          title="Sample size distribution"
          stats={landscape.sampleSize}
          values={models.map((model) => coerceMetricNumber(model.sample_size))}
          formatter={formatCompactNumber}
          tone="sky"
        />
        <MetricDistributionStrip
          title="AUC distribution"
          stats={landscape.auc}
          values={models.map((model) => coerceMetricNumber(model.metrics?.AUC))}
          formatter={(value) => value.toFixed(3)}
          tone="emerald"
        />
        <MetricDistributionStrip
          title="R2 distribution"
          stats={landscape.r2}
          values={models.map((model) => coerceMetricNumber(model.metrics?.R2))}
          formatter={(value) => value.toFixed(4)}
          tone="violet"
        />
        <MetricDistributionStrip
          title="Variant count distribution"
          stats={landscape.variants}
          values={models.map((model) => coerceMetricNumber(model.num_variants))}
          formatter={formatCompactNumber}
          tone="amber"
        />
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-2">
        <EvidenceCompleteness buckets={landscape.completeness} total={landscape.totalModels} />
        <BucketPanel title="Ancestry coverage" icon={Dna} buckets={landscape.ancestries} />
      </div>

      {expanded && (
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <BucketPanel title="Method mix" icon={FlaskConical} buckets={landscape.methods} />
          <BucketPanel title="Source mix" icon={Archive} buckets={landscape.sources} />
          <MetricRangePanel title="Sample size range" stats={landscape.sampleSize} formatter={formatCompactNumber} />
          <MetricRangePanel title="Variant range" stats={landscape.variants} formatter={formatCompactNumber} />
          <MetricRangePanel title="AUC range" stats={landscape.auc} formatter={(value) => value.toFixed(3)} />
          <MetricRangePanel title="R2 range" stats={landscape.r2} formatter={(value) => value.toFixed(4)} />
        </div>
      )}
    </div>
  );
}

function ModelLandscapePanel({
  response,
  models,
  compact = false,
  expanded = false,
}: {
  response: AgentResponse;
  models: ModelPreview[];
  compact?: boolean;
  expanded?: boolean;
}) {
  const landscape = computeModelLandscape(models, response);

  if (!models.length) {
    return (
      <div className="rounded-xl border border-zinc-700 bg-[#252524] p-4 text-sm leading-6 text-zinc-500">
        No candidate model previews were returned, so the performance landscape cannot be plotted.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-zinc-700 bg-[#252524] p-4">
      <div className="flex flex-col gap-2 border-b border-zinc-700 pb-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
            <BarChart3 className="size-4 text-zinc-400" />
            Performance landscape
          </div>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-zinc-500">
            This is separate from the inventory summary: it asks whether reported AUC, R2, sample size, and variant count create a clear quality signal or expose sparse evidence.
          </p>
        </div>
        <div className="rounded-lg border border-zinc-700 bg-[#30302f] px-3 py-2 text-xs">
          <div className="text-zinc-500">selected model</div>
          <div className="mt-1 font-mono font-semibold text-zinc-100">
            {response.final_recommendation.recommended_pgs_id || "N/A"}
          </div>
          <div className="mt-1 text-zinc-500">
            {landscape.recommendedRankByAuc ? `AUC rank ${landscape.recommendedRankByAuc}/${landscape.auc?.count || landscape.totalModels}` : "AUC rank unavailable"}
          </div>
        </div>
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-[1.3fr_0.7fr]">
        <PerformanceLandscape landscape={landscape} />
        <div className="grid gap-3">
          <MetricRangePanel title="AUC range" stats={landscape.auc} formatter={(value) => value.toFixed(3)} />
          <MetricRangePanel title="R2 range" stats={landscape.r2} formatter={(value) => value.toFixed(4)} />
        </div>
      </div>

      {(expanded || !compact) && (
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <MetricRangePanel title="Sample size range" stats={landscape.sampleSize} formatter={formatCompactNumber} />
          <MetricRangePanel title="Variant range" stats={landscape.variants} formatter={formatCompactNumber} />
        </div>
      )}
    </div>
  );
}

function MetricDistributionStrip({
  title,
  stats,
  values,
  formatter,
  tone,
}: {
  title: string;
  stats: MetricStats | null;
  values: Array<number | null>;
  formatter: (value: number) => string;
  tone: "sky" | "emerald" | "violet" | "amber";
}) {
  const numericValues = values.filter((value): value is number => value !== null && Number.isFinite(value));
  const min = stats?.min ?? 0;
  const max = stats?.max ?? 0;
  const spread = Math.max(1e-9, max - min);

  return (
    <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3">
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-semibold text-zinc-100">{title}</div>
        <span className="font-mono text-xs text-zinc-500">{numericValues.length}/{values.length}</span>
      </div>
      {stats ? (
        <>
          <div className="relative mt-4 h-10 rounded-lg border border-zinc-700 bg-[#20201f]">
            <div className="absolute inset-y-2 left-1/2 border-l border-dashed border-zinc-700" />
            {numericValues.map((value, index) => {
              const left = min === max ? 50 : ((value - min) / spread) * 88 + 6;
              return (
                <span
                  key={`${title}-${value}-${index}`}
                  title={formatter(value)}
                  className={cn(
                    "absolute top-1/2 size-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full border",
                    tone === "sky" && "border-sky-200 bg-sky-400",
                    tone === "emerald" && "border-emerald-200 bg-emerald-400",
                    tone === "violet" && "border-violet-200 bg-violet-400",
                    tone === "amber" && "border-amber-200 bg-amber-400"
                  )}
                  style={{ left: `${left}%` }}
                />
              );
            })}
          </div>
          <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
            <MetricRangeValue label="min" value={formatter(stats.min)} />
            <MetricRangeValue label="median" value={formatter(stats.median)} active />
            <MetricRangeValue label="max" value={formatter(stats.max)} />
          </div>
        </>
      ) : (
        <div className="mt-3 rounded-md border border-zinc-700 bg-[#252524] px-3 py-3 text-sm text-zinc-500">No values returned.</div>
      )}
    </div>
  );
}

function LandscapeStat({ icon: Icon, label, value, sublabel }: { icon: LucideIcon; label: string; value: string; sublabel: string }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3">
      <div className="flex items-center justify-between gap-2">
        <div className="text-xs text-zinc-500">{label}</div>
        <Icon className="size-3.5 text-zinc-500" />
      </div>
      <div className="mt-2 font-mono text-lg font-semibold text-zinc-100">{value}</div>
      <div className="mt-1 text-xs text-zinc-500">{sublabel}</div>
    </div>
  );
}

function PerformanceLandscape({ landscape }: { landscape: ModelLandscape }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div>
          <div className="text-sm font-semibold text-zinc-100">Performance landscape</div>
          <div className="text-xs text-zinc-500">x = AUC, y = R2, dot size = training sample size</div>
        </div>
        <BarChart3 className="size-4 text-zinc-500" />
      </div>
      <div className="relative h-44 overflow-hidden rounded-lg border border-zinc-700 bg-[#20201f]">
        <div className="absolute inset-x-4 top-5 border-t border-dashed border-zinc-700" />
        <div className="absolute inset-x-4 top-1/2 border-t border-dashed border-zinc-800" />
        <div className="absolute inset-x-4 bottom-7 border-t border-dashed border-zinc-700" />
        <div className="absolute bottom-2 left-3 text-[10px] text-zinc-600">AUC 0.5</div>
        <div className="absolute bottom-2 right-3 text-[10px] text-zinc-600">AUC 1.0</div>
        <div className="absolute left-3 top-2 text-[10px] text-zinc-600">higher R2</div>
        {landscape.points.map((point) => (
          <div
            key={point.model.id || point.model.name}
            title={`${point.model.id || point.model.name}: AUC ${metricValue(point.auc)}, R2 ${metricValue(point.r2)}, sample ${formatCompactNumber(point.sampleSize)}`}
            className={cn(
              "absolute rounded-full border transition-transform hover:z-10 hover:scale-125",
              point.isRecommended
                ? "border-emerald-200 bg-emerald-400 shadow-[0_0_0_5px_rgba(16,185,129,0.18)]"
                : "border-sky-200/80 bg-sky-400/80"
            )}
            style={{
              left: `${point.x}%`,
              top: `${point.y}%`,
              width: point.size,
              height: point.size,
              transform: "translate(-50%, -50%)",
            }}
          />
        ))}
      </div>
    </div>
  );
}

function EvidenceCompleteness({ buckets, total }: { buckets: LandscapeBucket[]; total: number }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="text-sm font-semibold text-zinc-100">Evidence completeness</div>
        <CheckCircle2 className="size-4 text-zinc-500" />
      </div>
      <div className="space-y-2">
        {buckets.map((bucket) => (
          <div key={bucket.label}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-zinc-400">{bucket.label}</span>
              <span className="font-mono text-zinc-500">
                {bucket.count}/{total}
              </span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div className="h-full rounded-full bg-emerald-400" style={{ width: `${Math.max(bucket.percent, bucket.count ? 6 : 0)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function BucketPanel({ title, icon: Icon, buckets }: { title: string; icon: LucideIcon; buckets: LandscapeBucket[] }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="text-sm font-semibold text-zinc-100">{title}</div>
        <Icon className="size-4 text-zinc-500" />
      </div>
      {buckets.length ? (
        <div className="space-y-2">
          {buckets.map((bucket) => (
            <div key={bucket.label}>
              <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                <span className="min-w-0 truncate text-zinc-400">{bucket.label}</span>
                <span className="font-mono text-zinc-500">{bucket.count}</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
                <div className="h-full rounded-full bg-sky-400" style={{ width: `${Math.max(bucket.percent, 6)}%` }} />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-sm text-zinc-500">No data available.</div>
      )}
    </div>
  );
}

function MetricRangePanel({ title, stats, formatter }: { title: string; stats: MetricStats | null; formatter: (value: number) => string }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3">
      <div className="text-sm font-semibold text-zinc-100">{title}</div>
      {stats ? (
        <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
          <MetricRangeValue label="min" value={formatter(stats.min)} />
          <MetricRangeValue label="median" value={formatter(stats.median)} active />
          <MetricRangeValue label="max" value={formatter(stats.max)} />
        </div>
      ) : (
        <div className="mt-2 text-sm text-zinc-500">No values returned.</div>
      )}
    </div>
  );
}

function MetricRangeValue({ label, value, active = false }: { label: string; value: string; active?: boolean }) {
  return (
    <div className="rounded-md border border-zinc-700 bg-[#252524] px-2 py-2">
      <div className="text-zinc-500">{label}</div>
      <div className={cn("mt-1 truncate font-mono text-sm", active ? "text-emerald-300" : "text-zinc-200")}>{value}</div>
    </div>
  );
}

function DetailShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="bg-[#30302f] p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-100">
        <CircleDot className="size-3.5 text-zinc-500" />
        {title}
      </div>
      {children}
    </div>
  );
}

function EvidenceBlock({ title, value, body }: { title: string; value: string; body: string }) {
  return (
    <div className="rounded-lg border border-zinc-700 bg-[#252524] p-3">
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-medium text-zinc-100">{title}</div>
        <div className="truncate font-mono text-xs text-zinc-400">{value}</div>
      </div>
      <p className="mt-2 line-clamp-6 text-sm leading-6 text-zinc-400">{body}</p>
    </div>
  );
}

function ExportButton({ icon: Icon, label, onClick }: { icon: LucideIcon; label: string; onClick: () => void }) {
  return (
    <Button
      type="button"
      variant="outline"
      onClick={onClick}
      className="h-10 justify-start gap-2 rounded-lg border-zinc-700 bg-[#252524] text-zinc-200 hover:bg-zinc-700 hover:text-zinc-50"
    >
      <Icon className="size-4" />
      {label}
    </Button>
  );
}

function TrainingJobActions({ response }: { response: AgentResponse }) {
  const selected = response.final_recommendation.recommended_pgs_id || response.same_trait_result.pgs_id || "selected PGS";
  const actions = [
    {
      title: "Single-ancestry training",
      detail: "Submit one GWAS summary-statistics job with ancestry, phenotype type, LD reference, and method settings.",
      status: "contract staged",
      command: "Prepare request",
    },
    {
      title: "Multi-ancestry training",
      detail: "Submit ancestry-stratified summary statistics, per-ancestry metadata, and harmonized downstream result collection.",
      status: "contract staged",
      command: "Prepare request",
    },
    {
      title: "Uploaded-data training",
      detail: "Use local upload metadata and credentials from Settings, then track job ID, status polling, logs, and result download.",
      status: "needs backend",
      command: "Open setup",
    },
  ];

  return (
    <div className="grid gap-3">
      <div className="rounded-lg border border-zinc-700 bg-[#252524] p-4">
        <div className="flex items-start gap-3">
          <FlaskConical className="mt-1 size-4 text-zinc-400" />
          <div>
            <div className="font-medium text-zinc-100">Training handoff for {selected}</div>
            <p className="mt-1 text-sm leading-6 text-zinc-400">
              The workplace now exposes the three product-scope training paths. The next backend milestone is real job submission, job ID persistence, status polling, log display, and result download.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-3">
        {actions.map((action) => (
          <div key={action.title} className="rounded-lg border border-zinc-700 bg-[#252524] p-3">
            <div className="flex items-start justify-between gap-2">
              <div className="font-medium text-zinc-100">{action.title}</div>
              <span className="shrink-0 rounded-full bg-amber-950/40 px-2 py-0.5 text-[11px] text-amber-200">{action.status}</span>
            </div>
            <p className="mt-2 min-h-20 text-xs leading-5 text-zinc-500">{action.detail}</p>
            <Button
              type="button"
              variant="outline"
              disabled
              className="mt-3 h-9 w-full justify-center rounded-lg border-zinc-700 bg-[#30302f] text-zinc-500"
            >
              {action.command}
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}

function modelIdentifier(model: ModelPreview) {
  return model.id || model.name || "unknown";
}

function candidateRole(response: AgentResponse, model: ModelPreview) {
  const id = modelIdentifier(model);
  if (id === response.final_recommendation.recommended_pgs_id) return "selected";
  if (id === response.same_trait_result.pgs_id) return "same-trait baseline";
  if (id === response.transfer_result?.pgs_id) return "transfer candidate";
  return "candidate";
}

function candidateEvidenceGap(model: ModelPreview) {
  const gaps = [];
  if (coerceMetricNumber(model.metrics?.AUC) === null) gaps.push("AUC missing");
  if (coerceMetricNumber(model.metrics?.R2) === null) gaps.push("R2 missing");
  if (!model.ancestry || model.ancestry === "N/A") gaps.push("ancestry unclear");
  if (!model.sample_size) gaps.push("sample size missing");
  return gaps.length ? gaps.join(", ") : "core metadata visible";
}

function CandidateTradeoffMatrix({
  response,
  models,
  compact = false,
}: {
  response: AgentResponse;
  models: ModelPreview[];
  compact?: boolean;
}) {
  const rows = compact ? models.slice(0, 5) : models;
  const finalId = response.final_recommendation.recommended_pgs_id;

  if (!rows.length) {
    return (
      <div className="rounded-lg border border-zinc-700 bg-[#252524] p-3 text-sm leading-6 text-zinc-500">
        No candidate previews were returned. The decision relies on the backend trace and warnings instead of a visible candidate table.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-700">
      <table className="w-full min-w-[860px] text-left text-sm">
        <thead className="bg-[#30302f] text-xs uppercase tracking-wide text-zinc-500">
          <tr>
            <th className="px-3 py-2 font-medium">Role</th>
            <th className="px-3 py-2 font-medium">PGS ID</th>
            <th className="px-3 py-2 font-medium">Trait fit</th>
            <th className="px-3 py-2 font-medium">AUC</th>
            <th className="px-3 py-2 font-medium">R2</th>
            <th className="px-3 py-2 font-medium">Method / ancestry</th>
            <th className="px-3 py-2 font-medium">Evidence gap</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800">
          {rows.map((model) => {
            const id = modelIdentifier(model);
            const role = candidateRole(response, model);
            const selected = id === finalId;
            return (
              <tr key={id} className={cn("hover:bg-zinc-800/60", selected && "bg-emerald-950/20")}>
                <td className="px-3 py-2">
                  <span
                    className={cn(
                      "rounded-full px-2 py-1 text-xs",
                      selected ? "bg-emerald-950/60 text-emerald-200" : "bg-zinc-800 text-zinc-400"
                    )}
                  >
                    {role}
                  </span>
                </td>
                <td className="px-3 py-2 font-mono text-xs text-zinc-100">{id}</td>
                <td className="max-w-[220px] truncate px-3 py-2 text-zinc-300">{model.trait || "N/A"}</td>
                <td className="px-3 py-2 font-mono text-xs text-zinc-300">{metricValue(model.metrics?.AUC)}</td>
                <td className="px-3 py-2 font-mono text-xs text-zinc-300">{metricValue(model.metrics?.R2)}</td>
                <td className="max-w-[260px] px-3 py-2 text-zinc-400">
                  <div className="truncate">{model.method || "Unknown method"}</div>
                  <div className="mt-0.5 truncate text-xs text-zinc-500">{model.ancestry || "Unknown ancestry"}</div>
                </td>
                <td className="max-w-[220px] truncate px-3 py-2 text-zinc-500">{candidateEvidenceGap(model)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {compact && models.length > rows.length ? (
        <div className="border-t border-zinc-700 bg-[#30302f] px-3 py-2 text-xs text-zinc-500">
          Showing top {rows.length} visible candidates. Open Candidate tradeoffs for the full table.
        </div>
      ) : null}
    </div>
  );
}

function ReasoningNotes({ response, showBackendTrace = false }: { response: AgentResponse; showBackendTrace?: boolean }) {
  const pseudoRun: NonNullable<ChatMessage["run"]> = {
    id: "completed-reasoning",
    trait: response.target_trait,
    mode: response.mode,
    status: "completed",
    activeStage: REASONING_STEPS.length - 1,
    response,
  };

  return (
    <div className="grid gap-2">
      {REASONING_STEPS.map((stage, index) => (
        <div key={stage.id} className="flex gap-3 rounded-lg border border-zinc-700 bg-[#30302f] p-3">
          <span className="mt-1 flex size-5 shrink-0 items-center justify-center rounded-full border border-emerald-500 bg-emerald-500/20 text-xs text-emerald-200">
            {index + 1}
          </span>
          <div className="min-w-0">
            <div className="text-sm font-medium text-zinc-100">{stage.title}</div>
            <p className="mt-1 text-xs leading-5 text-zinc-500">{reasoningDetailForStep(stage, pseudoRun)}</p>
          </div>
        </div>
      ))}

      {showBackendTrace && response.agent_trace_steps.length ? (
        <div className="mt-1 rounded-lg border border-zinc-700 bg-[#30302f] p-3">
          <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
            <TerminalSquare className="size-3.5" />
            Backend trace
          </div>
          <div className="flex flex-col gap-2">
            {response.agent_trace_steps.map((step) => (
              <div key={step.id} className="flex gap-3 text-xs leading-5 text-zinc-400">
                <span className={cn("mt-1.5 size-1.5 rounded-full", statusTone(step.status))} />
                <span className="font-medium text-zinc-300">{step.title}</span>
                <span className="min-w-0 flex-1 truncate text-zinc-500">{step.detail}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function CaveatPreview({ response }: { response: AgentResponse }) {
  const items = [...response.warnings, ...response.errors];
  if (!items.length) {
    return (
      <div className="rounded-lg border border-zinc-700 bg-[#30302f] p-3 text-sm leading-6 text-zinc-500">
        No blocking warnings were returned. Continue to check original PGS Catalog entries before clinical or downstream cohort use.
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-2">
      {items.slice(0, 4).map((item) => (
        <div key={item} className="rounded-lg border border-amber-900/70 bg-amber-950/30 p-3 text-sm leading-6 text-amber-100">
          {item}
        </div>
      ))}
      {items.length > 4 ? <div className="text-xs text-zinc-500">Open Warnings for {items.length - 4} more item(s).</div> : null}
    </div>
  );
}

function Composer({
  value,
  mode,
  disabled,
  requestError,
  onChange,
  onModeChange,
  onSubmit,
}: {
  value: string;
  mode: AgentMode;
  disabled: boolean;
  requestError: string | null;
  onChange: (value: string) => void;
  onModeChange: (mode: AgentMode) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="shrink-0 bg-gradient-to-t from-[#1f1f1f] via-[#1f1f1f] to-transparent px-4 pb-4 pt-3">
      <form onSubmit={onSubmit} className="mx-auto max-w-[860px]">
        {requestError && (
          <div className="mb-2 rounded-lg border border-red-900 bg-red-950/40 px-3 py-2 text-sm text-red-200">{requestError}</div>
        )}
        <div className="rounded-2xl border border-zinc-700 bg-[#3a3a39] p-3 shadow-2xl">
          <label className="sr-only" htmlFor="pennprs-composer">
            Ask PennPRS Agent
          </label>
          <textarea
            id="pennprs-composer"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder="Ask PennPRS Agent for a target trait..."
            className="max-h-36 min-h-16 w-full resize-none bg-transparent text-sm leading-6 text-zinc-100 outline-none placeholder:text-zinc-500"
          />
          <div className="mt-2 flex items-center gap-2">
            <Button type="button" variant="ghost" size="icon" className="size-8 rounded-lg text-zinc-400 hover:bg-zinc-700 hover:text-zinc-100">
              <MessageSquarePlus className="size-4" />
            </Button>
            <div className="flex rounded-lg border border-zinc-700 bg-[#2d2d2c] p-1">
              {(["cached", "live"] as AgentMode[]).map((option) => (
                <button
                  key={option}
                  type="button"
                  disabled={option === "live"}
                  title={option === "live" ? "Live mode is locked until you explicitly ask to enable it." : "Use cached local artifacts"}
                  onClick={() => onModeChange("cached")}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-xs font-medium capitalize transition-colors disabled:cursor-not-allowed disabled:opacity-40",
                    mode === option ? "bg-zinc-700 text-zinc-100" : "text-zinc-500 hover:text-zinc-200"
                  )}
                >
                  {option}
                </button>
              ))}
            </div>
            <div className="ml-auto flex items-center gap-2 text-xs text-zinc-500">
              <span className="hidden sm:inline">local agent</span>
              <Button
                type="submit"
                size="icon"
                disabled={disabled}
                className="size-9 rounded-full bg-zinc-100 text-zinc-950 hover:bg-white"
                title="Run recommendation"
              >
                {disabled ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />}
              </Button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}

function RunInspector({
  result,
  models,
  warningCount,
}: {
  result: AgentResponse | null;
  models: ModelPreview[];
  warningCount: number;
}) {
  return (
    <aside className="hidden w-[320px] shrink-0 border-l border-zinc-800 bg-[#2b2b2a] p-4 xl:block">
      <div className="rounded-2xl border border-zinc-700 bg-[#343433] p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="text-sm font-semibold text-zinc-200">Agent run status</div>
          <CircleDot className="size-4 text-zinc-500" />
        </div>
        <ProgressRow done label="Local workplace loaded" />
        <ProgressRow done={models.length > 0} label="Model inventory summarized" />
        <ProgressRow done={models.length > 0} label="Candidate tradeoffs visible" />
        <ProgressRow done={!!result} label="Final recommendation reviewed" />
      </div>

      <div className="mt-4 rounded-2xl border border-zinc-700 bg-[#343433] p-4">
        <div className="mb-3 text-sm font-semibold text-zinc-200">Run details</div>
        <InspectorMetric label="Target" value={result?.target_trait || "No active run"} />
        <InspectorMetric label="Recommended PGS" value={result?.final_recommendation.recommended_pgs_id || "N/A"} />
        <InspectorMetric label="Models" value={String(models.length)} />
        <InspectorMetric label="Flags" value={String(warningCount)} />
      </div>

      <div className="mt-4 rounded-2xl border border-zinc-700 bg-[#343433] p-4">
        <div className="mb-3 text-sm font-semibold text-zinc-200">Artifacts</div>
        {result ? (
          <ArtifactList result={result} />
        ) : (
          <div className="rounded-lg border border-zinc-700 bg-[#252524] p-3 text-sm leading-6 text-zinc-500">
            Run a trait recommendation to produce a model summary, recommendation report, candidate table, provenance bundle, and training job request.
          </div>
        )}
      </div>
    </aside>
  );
}

function ArtifactList({ result }: { result: AgentResponse }) {
  const safeTrait = result.target_trait.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const base = safeTrait || "trait";
  const artifacts = [
    { title: "PRS model summary", filename: `${base}-model-summary.json`, status: "ready" },
    { title: "Recommendation report", filename: `${base}-recommendation-report.md`, status: "ready" },
    { title: "Candidate model table", filename: `${base}-candidate-models.csv`, status: "ready" },
    { title: "Warnings and caveats", filename: `${base}-caveats.md`, status: result.warnings.length || result.errors.length ? "review" : "ready" },
    { title: "Provenance bundle", filename: `${base}-provenance.json`, status: "ready" },
    { title: "Training job request", filename: `${base}-training-request.json`, status: "staged" },
  ];

  return (
    <div className="flex flex-col gap-2 text-sm text-zinc-400">
      {artifacts.map((artifact) => (
        <div key={artifact.filename} className="flex items-start gap-2 rounded-lg border border-zinc-700 bg-[#252524] px-3 py-2">
          <FileText className="size-4 shrink-0" />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="min-w-0 flex-1 truncate text-zinc-200">{artifact.title}</span>
              <span className={cn("text-xs", artifact.status === "ready" ? "text-emerald-300" : "text-amber-300")}>{artifact.status}</span>
            </div>
            <div className="mt-0.5 truncate font-mono text-[11px] text-zinc-500">{artifact.filename}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ProgressRow({ done, label }: { done: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2 py-1.5 text-sm text-zinc-400">
      <span className={cn("flex size-4 items-center justify-center rounded-full", done ? "bg-zinc-500 text-zinc-900" : "border border-zinc-600")}>
        {done && <CheckCircle2 className="size-3" />}
      </span>
      {label}
    </div>
  );
}

function InspectorMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-t border-zinc-700 py-2 first:border-t-0">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 truncate text-sm text-zinc-200">{value}</div>
    </div>
  );
}
