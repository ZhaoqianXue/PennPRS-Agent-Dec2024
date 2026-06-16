"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  ArrowDownToLine,
  BarChart3,
  BookOpenCheck,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  Database,
  Dna,
  Download,
  FileText,
  FlaskConical,
  GitBranch,
  Layers3,
  LockKeyhole,
  Moon,
  Network,
  PanelLeft,
  Search,
  ShieldCheck,
  Sparkles,
  Table2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { scaleLinear } from "d3";
import { cn } from "@/lib/utils";

export type FigureView = "within" | "cross" | "downstream";
export type ThemeMode = "light" | "dark";

type ModelDatum = {
  id: string;
  trait: string;
  method: string;
  ancestry: string;
  auc?: number;
  r2?: number;
  variants: string;
  sample: string;
  role: "selected" | "alternative" | "context";
};

type EvidenceItem = {
  label: string;
  value: string;
  detail: string;
  status: "selected" | "supported" | "review";
  icon: LucideIcon;
};

const figureTabs: Array<{ id: FigureView; label: string; caption: string; icon: LucideIcon }> = [
  {
    id: "within",
    label: "Figure 1",
    caption: "Within-phenotype report",
    icon: BarChart3,
  },
  {
    id: "cross",
    label: "Figure 2",
    caption: "Cross-phenotype report",
    icon: GitBranch,
  },
  {
    id: "downstream",
    label: "Figure 3",
    caption: "Downstream workspace",
    icon: ClipboardCheck,
  },
];

const withinModels: ModelDatum[] = [
  {
    id: "PGS004153",
    trait: "Breast cancer",
    method: "UKBB-EUR.MultiPRS.CV",
    ancestry: "EUR training; EUR/SAS evaluation",
    auc: 0.663,
    r2: 0.076,
    variants: "1.13M",
    sample: "12.5k",
    role: "selected",
  },
  {
    id: "PGS004040",
    trait: "Breast cancer",
    method: "LDpred2.CV",
    ancestry: "EUR training; EUR/SAS evaluation",
    auc: 0.66,
    r2: 0.074,
    variants: "1.04M",
    sample: "12.5k",
    role: "alternative",
  },
  {
    id: "PGS004025",
    trait: "Breast cancer",
    method: "LDpred2-auto",
    ancestry: "EUR training; EUR/SAS evaluation",
    auc: 0.66,
    r2: 0.074,
    variants: "1.04M",
    sample: "12.5k",
    role: "alternative",
  },
  {
    id: "PGS004083",
    trait: "Breast cancer",
    method: "PRS-CS-auto",
    ancestry: "EUR training; EUR/SAS evaluation",
    auc: 0.655,
    r2: 0.07,
    variants: "1.10M",
    sample: "12.5k",
    role: "context",
  },
  {
    id: "PGS004069",
    trait: "Breast cancer",
    method: "MegaPRS.CV",
    ancestry: "EUR training; EUR/SAS evaluation",
    auc: 0.656,
    r2: 0.071,
    variants: "869k",
    sample: "12.5k",
    role: "context",
  },
  {
    id: "PGS000531",
    trait: "Breast cancer female",
    method: "lassosum",
    ancestry: "EUR training and evaluation",
    auc: 0.61,
    r2: 0.037,
    variants: "98k",
    sample: "7.4k",
    role: "context",
  },
  {
    id: "PGS000488",
    trait: "Breast cancer female",
    method: "P+T",
    ancestry: "EUR training and evaluation",
    auc: 0.598,
    r2: 0.023,
    variants: "79",
    sample: "68.5k",
    role: "context",
  },
];

const crossTargetModels: ModelDatum[] = [
  {
    id: "F22",
    trait: "Delusional disorders",
    method: "No self PRS",
    ancestry: "No direct benchmark",
    variants: "-",
    sample: "AoU target",
    role: "context",
  },
];

const crossSourceModels: ModelDatum[] = [
  {
    id: "PGS000136",
    trait: "Schizophrenia",
    method: "PRS-CS",
    ancestry: "EAS/EUR GWAS; EUR evaluation",
    auc: 0.64,
    variants: "1.1M+",
    sample: "18.5k",
    role: "selected",
  },
  {
    id: "PGS000135",
    trait: "Schizophrenia",
    method: "PRS-CS",
    ancestry: "EAS/EUR GWAS; EUR evaluation",
    auc: 0.74,
    variants: "1.1M+",
    sample: "9.6k",
    role: "alternative",
  },
  {
    id: "PGS000133",
    trait: "Schizophrenia",
    method: "PRS-CS",
    ancestry: "EAS/EUR GWAS; EUR evaluation",
    auc: 0.6,
    variants: "1.1M+",
    sample: "public",
    role: "context",
  },
];

const withinEvidence: EvidenceItem[] = [
  {
    label: "Phenotype match",
    value: "Direct breast cancer endpoint",
    detail: "The selected PGS is trained and evaluated for the queried phenotype family.",
    status: "selected",
    icon: Search,
  },
  {
    label: "Model landscape",
    value: "163 breast cancer candidates",
    detail: "The recommendation is made after comparing alternatives across method, ancestry, and reported performance.",
    status: "supported",
    icon: Database,
  },
  {
    label: "Validation context",
    value: "EUR/SAS evaluation signal",
    detail: "The report keeps ancestry context visible before downstream cohort use.",
    status: "supported",
    icon: Dna,
  },
  {
    label: "Review note",
    value: "Use with cohort validation",
    detail: "The application records caveats and planned validation steps before export.",
    status: "review",
    icon: ClipboardCheck,
  },
];

const crossEvidence: EvidenceItem[] = [
  {
    label: "Target phenotype",
    value: "Delusional disorders",
    detail: "No self PRS benchmark is available for the target phenotype.",
    status: "review",
    icon: BrainCircuit,
  },
  {
    label: "Source phenotype",
    value: "Schizophrenia",
    detail: "A related psychiatric phenotype is nominated for transfer after evidence scouting.",
    status: "selected",
    icon: GitBranch,
  },
  {
    label: "Genetic-correlation evidence",
    value: "Psychosis-spectrum proximity",
    detail: "The report separates genetic-correlation support from downstream validation requirements.",
    status: "supported",
    icon: Network,
  },
  {
    label: "Open Targets evidence",
    value: "Biological overlap reviewed",
    detail: "Disease-target and pathway overlap are displayed as supporting evidence, not as automatic proof.",
    status: "supported",
    icon: BookOpenCheck,
  },
];

const downstreamSteps = [
  {
    title: "Local data binding",
    status: "Ready",
    detail: "Connect selected PGS weights with individual-level genotype, phenotype, covariate, and ancestry files in the user's own environment.",
    icon: LockKeyhole,
  },
  {
    title: "Validation metrics",
    status: "Planned",
    detail: "Estimate discrimination, calibration, incremental predictive value, and cohort-specific model behavior.",
    icon: Activity,
  },
  {
    title: "Risk stratification",
    status: "Planned",
    detail: "Define PRS percentile bins and compare risk profiles across clinically relevant strata.",
    icon: BarChart3,
  },
  {
    title: "Subgroup checks",
    status: "Planned",
    detail: "Evaluate performance by ancestry, sex, age group, and site when these fields are available.",
    icon: Layers3,
  },
  {
    title: "Recommendation record",
    status: "Ready",
    detail: "Preserve target phenotype, selected model, alternatives, evidence channels, caveats, and validation plan.",
    icon: FileText,
  },
  {
    title: "PennPRS training handoff",
    status: "Optional",
    detail: "Prepare a single-ancestry, multi-ancestry, or ensemble training request when no existing score is sufficient.",
    icon: FlaskConical,
  },
];

export function parseFigure(value: string | null | undefined): FigureView {
  if (value === "cross" || value === "downstream" || value === "within") return value;
  return "within";
}

export function parseTheme(value: string | null | undefined): ThemeMode {
  return value === "dark" ? "dark" : "light";
}

export default function ProposalFigureWorkspace({
  initialFigure = "within",
  initialTheme = "light",
}: {
  initialFigure?: FigureView;
  initialTheme?: ThemeMode;
}) {
  const [figure, setFigure] = useState<FigureView>(initialFigure);
  const [theme, setTheme] = useState<ThemeMode>(initialTheme);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const activeMeta = useMemo(() => figureTabs.find((tab) => tab.id === figure) || figureTabs[0], [figure]);

  const updateRouteState = (nextFigure: FigureView, nextTheme = theme) => {
    setFigure(nextFigure);
    setTheme(nextTheme);
    const params = new URLSearchParams(window.location.search);
    params.set("figure", nextFigure);
    params.set("theme", nextTheme);
    window.history.replaceState(null, "", `${window.location.pathname}?${params.toString()}`);
  };

  if (theme === "light") {
    return <ScientificFigureCanvas figure={figure} onFigureChange={(nextFigure) => updateRouteState(nextFigure, "light")} />;
  }

  const darkTheme: ThemeMode = "dark";
  const pageClass = "bg-slate-950 text-slate-100";
  const sidebarClass = "border-slate-800 bg-slate-900 text-slate-300";

  return (
    <main className={cn("flex min-h-screen overflow-hidden", pageClass)}>
      {sidebarOpen && (
        <aside className={cn("hidden w-[292px] shrink-0 border-r px-4 py-4 lg:flex lg:flex-col", sidebarClass)}>
          <div className="flex items-center gap-3">
            <div className="flex size-9 items-center justify-center rounded-lg border border-blue-200 bg-white text-blue-700 shadow-sm">
              <Sparkles className="size-4" />
            </div>
            <div>
              <div className="text-base font-semibold text-slate-950 dark:text-white">PRS Agent</div>
              <div className="text-xs text-slate-500 dark:text-slate-400">local figure workspace</div>
            </div>
          </div>

          <section className="mt-6">
            <SectionLabel>Preliminary screenshots</SectionLabel>
            <div className="mt-2 flex flex-col gap-2">
              {figureTabs.map((tab) => (
                <FigureTab
                  key={tab.id}
                  tab={tab}
                  active={figure === tab.id}
                  theme={darkTheme}
                  onClick={() => updateRouteState(tab.id)}
                />
              ))}
            </div>
          </section>

          <section className="mt-6">
            <SectionLabel>Example traits</SectionLabel>
            <div className="mt-3 space-y-3 text-sm">
              <TraitRoute
                title="Breast carcinoma"
                subtitle="within-phenotype report"
                active={figure === "within"}
                onClick={() => updateRouteState("within")}
              />
              <TraitRoute
                title="Bipolar disorder"
                subtitle="cross-phenotype transfer report"
                active={figure === "cross"}
                onClick={() => updateRouteState("cross")}
              />
              <TraitRoute
                title="Selected PRS model"
                subtitle="downstream analysis workspace"
                active={figure === "downstream"}
                onClick={() => updateRouteState("downstream")}
              />
            </div>
          </section>

          <section className="mt-6">
            <SectionLabel>Local application status</SectionLabel>
            <div className="mt-3 space-y-2">
              <SidebarStatus icon={ShieldCheck} label="Individual-level data stays local" />
              <SidebarStatus icon={Database} label="Recommendation record exportable" />
              <SidebarStatus icon={Download} label="Figure state URL is reproducible" />
            </div>
          </section>

          <div className="mt-auto rounded-lg border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-600 shadow-sm dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
            Screenshot route: <span className="font-mono text-slate-900 dark:text-slate-100">/workplace?figure={figure}&theme={theme}</span>
          </div>
        </aside>
      )}

      <section className="flex min-w-0 flex-1 flex-col">
        <header
          className={cn(
            "flex h-14 shrink-0 items-center border-b px-4",
            "border-slate-800 bg-slate-950"
          )}
        >
          <button
            type="button"
            onClick={() => setSidebarOpen((open) => !open)}
            className={cn(
              "mr-3 flex size-8 items-center justify-center rounded-md border",
              "border-slate-800 text-slate-300 hover:bg-slate-900"
            )}
            title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
          >
            <PanelLeft className="size-4" />
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <activeMeta.icon className="size-4 text-blue-700" />
              <span>{activeMeta.label}</span>
              <span className="text-slate-400">/</span>
              <span className="truncate text-slate-600 dark:text-slate-300">{activeMeta.caption}</span>
            </div>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              onClick={() => updateRouteState(figure, "light")}
              className={cn(
                "flex h-8 items-center gap-2 rounded-md border px-3 text-xs font-medium",
                "border-slate-800 bg-slate-900 text-slate-200 hover:bg-slate-800"
              )}
            >
              <Moon className="size-3.5" />
              Dark
            </button>
            <button
              type="button"
              className="hidden h-8 items-center gap-2 rounded-md bg-slate-950 px-3 text-xs font-medium text-white hover:bg-slate-800 md:flex"
            >
              <ArrowDownToLine className="size-3.5" />
              Export report
            </button>
          </div>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto bg-slate-950">
          {figure === "within" && <WithinPhenotypeReport theme={darkTheme} />}
          {figure === "cross" && <CrossPhenotypeReport theme={darkTheme} />}
          {figure === "downstream" && <DownstreamWorkspace theme={darkTheme} />}
        </div>
      </section>
    </main>
  );
}

function FigureTab({
  tab,
  active,
  theme,
  onClick,
}: {
  tab: (typeof figureTabs)[number];
  active: boolean;
  theme: ThemeMode;
  onClick: () => void;
}) {
  const Icon = tab.icon;
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 rounded-lg border px-3 py-3 text-left transition-colors",
        active
          ? "border-blue-200 bg-blue-50 text-blue-950"
          : theme === "light"
            ? "border-transparent text-slate-600 hover:border-slate-200 hover:bg-white"
            : "border-transparent text-slate-300 hover:border-slate-700 hover:bg-slate-800"
      )}
    >
      <div className={cn("flex size-8 items-center justify-center rounded-md", active ? "bg-blue-700 text-white" : "bg-slate-200 text-slate-600")}>
        <Icon className="size-4" />
      </div>
      <div className="min-w-0">
        <div className="text-sm font-semibold">{tab.label}</div>
        <div className="truncate text-xs opacity-75">{tab.caption}</div>
      </div>
    </button>
  );
}

function ScientificFigureCanvas({
  figure,
  onFigureChange,
}: {
  figure: FigureView;
  onFigureChange: (figure: FigureView) => void;
}) {
  return (
    <main className="h-screen overflow-hidden bg-white text-slate-950">
      <div className="mx-auto flex h-full w-full max-w-[1646px] flex-col">
        <div className="sr-only">
          {figureTabs.map((tab) => (
            <button key={tab.id} type="button" onClick={() => onFigureChange(tab.id)}>
              {tab.label}
            </button>
          ))}
        </div>
        <section className="min-h-0 flex-1">
          {figure === "within" && <ScientificWithinFigure />}
          {figure === "cross" && <ScientificCrossFigure />}
          {figure === "downstream" && <ScientificDownstreamFigure />}
        </section>
      </div>
    </main>
  );
}

function ScientificFigureShell({
  children,
}: {
  figure: string;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-full flex-col border border-slate-900 bg-white p-2.5 shadow-[0_2px_10px_rgba(15,23,42,0.10)]">
      <div className="min-h-0 flex-1">{children}</div>
    </div>
  );
}

function PanelFigure({
  label,
  title,
  children,
  className,
}: {
  label: string;
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("relative min-h-0 border border-slate-400 bg-white", className)}>
      <div className="absolute -left-px -top-px z-10 flex size-7 items-center justify-center bg-slate-950 text-sm font-bold text-white">
        {label}
      </div>
      <div className="border-b border-slate-300 bg-slate-100 px-3 py-1.5 pl-9 text-[13px] font-bold text-slate-950">{title}</div>
      <div className="h-[calc(100%-32px)] p-2">{children}</div>
    </section>
  );
}

function ScientificWithinFigure() {
  return <WithinPhenotypeScientificPlate />;
}

function WithinPhenotypeScientificPlate() {
  const distributions = [
    {
	      label: "GWAS sample size",
	      count: "122/163",
	      min: "404",
	      median: "12.5k",
	      max: "391k",
	      dots: withinDistributionDots.sample,
	      selected: 50,
	      color: "#a8a29e",
	    },
    {
	      label: "Reported AUC",
	      count: "143/163",
	      min: "0.520",
	      median: "0.611",
	      max: "0.780",
	      dots: withinDistributionDots.auc,
	      selected: 63.4,
	      color: "#9ca66b",
	    },
	    {
	      label: "Reported R2",
	      count: "91/163",
	      min: "0.0022",
	      median: "0.0285",
	      max: "0.146",
	      dots: withinDistributionDots.r2,
	      selected: 67.9,
	      color: "#a78bfa",
	    },
    {
      label: "Variant count",
      count: "163/163",
      min: "9",
	      median: "330",
	      max: "6.49M",
	      dots: withinDistributionDots.variants,
	      selected: 86.2,
	      color: "#de9b4a",
	    },
  ];

  return (
    <div className="h-full w-full bg-white">
      <svg viewBox="0 0 1646 900" className="h-full w-full" role="img" aria-label="Within-phenotype PRS Agent recommendation figure">
        <defs>
          <marker id="smallArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
            <path d="M 0 0 L 8 4 L 0 8 Z" fill="#8aa3bf" />
          </marker>
          <filter id="panelSoftShadow" x="-5%" y="-5%" width="110%" height="120%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#0f172a" floodOpacity="0.08" />
          </filter>
          <filter id="nodeSoftShadow" x="-35%" y="-35%" width="170%" height="170%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#0f172a" floodOpacity="0.12" />
          </filter>
          <linearGradient id="figurePanelWash" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#f8fbff" />
          </linearGradient>
          <linearGradient id="pennPrsWash" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#e3f2fd" />
            <stop offset="100%" stopColor="#ffffff" />
          </linearGradient>
          <linearGradient id="primaryWash" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#e3f2fd" />
            <stop offset="100%" stopColor="#ffffff" />
          </linearGradient>
          <clipPath id="riskBandClip">
            <rect x="1462" y="855" width="118" height="22" rx="6" />
          </clipPath>
        </defs>
        <rect x="0" y="0" width="1646" height="900" fill="#ffffff" />

        <g transform="translate(0 -68)">
          <rect x="16" y="74" width="1066" height="888" rx="8" fill="url(#figurePanelWash)" stroke="#bbdefb" strokeWidth="1.2" filter="url(#panelSoftShadow)" />
          <rect x="1088" y="74" width="540" height="888" rx="8" fill="#ffffff" stroke="#d7e3f7" strokeWidth="1.2" filter="url(#panelSoftShadow)" />
          <ScientificPanelFrame x={22} y={82} width={1054} label="A" title="Target disease and PRS evidence" />
          <ScientificPanelFrame x={1094} y={82} width={528} label="B" title="Recommended model details" />

          <PanelBModelSummary distributions={distributions} />
          <PanelCRecommendation />
        </g>
      </svg>
    </div>
  );
}

function ScientificPanelFrame({
  x,
  y,
  width,
  label,
  title,
}: {
  x: number;
  y: number;
  width: number;
  label: string;
  title: string;
}) {
  return (
    <g>
      <text x={x} y={y + 29} fontFamily="Inter, SF Pro Text, -apple-system, BlinkMacSystemFont, Arial, Helvetica, sans-serif" fontSize="32" fontWeight="800" fill="#020617">
        {label}
      </text>
      <text x={x + 42} y={y + 29} fontFamily="Inter, SF Pro Text, -apple-system, BlinkMacSystemFont, Arial, Helvetica, sans-serif" fontSize="24" fontWeight="800" fill="#020617">
        {title}
      </text>
      <line x1={x + 42} y1={y + 42} x2={x + width} y2={y + 42} stroke="#94a3b8" strokeWidth="1.2" />
    </g>
  );
}

function PanelBModelSummary({
  distributions,
}: {
  distributions: Array<{
    label: string;
    count: string;
    min: string;
    median: string;
    max: string;
    dots: number[];
    selected: number;
    color: string;
  }>;
}) {
  const targetCards = [
    ["Target disease", "Breast cancer", ""],
    ["Heritability estimate", "0.11 (0.10 - 0.14)", ""],
  ];
	  const statCards = [
	    { label: "Candidate models", value: "163", details: ["within phenotype"] },
	    { label: "Maximal reported AUC", value: "0.780", details: ["reported in 143/163"] },
	    { label: "Maximal GWAS sample size", value: "391k", details: ["total sample size"] },
	    { label: "Maximal number of variants", value: "6.49M", details: ["reported in 163/163"] },
	  ];
  const statAccentColors = ["#0d47a1", "#6d89a5", "#a56a43", "#6f7c42"];

  return (
    <g fontFamily="Inter, SF Pro Text, -apple-system, BlinkMacSystemFont, Arial, Helvetica, sans-serif">
      {targetCards.map(([label, value, sublabel], index) => {
        const x = 42 + index * 516;
        return (
          <g key={label}>
            <rect x={x} y="126" width="500" height="82" rx="8" fill="#ffffff" stroke="#bbdefb" strokeWidth="1.1" filter="url(#nodeSoftShadow)" />
            <line x1={x + 16} y1="144" x2={x + 16} y2="192" stroke={index === 0 ? "#0d47a1" : "#6f7c42"} strokeWidth="4" strokeLinecap="round" />
            <text x={x + 34} y="154" fontSize="17" fontWeight="800" fill="#64748b">
              {label}
            </text>
            <text x={x + 34} y={index === 0 ? "190" : "190"} fontSize={index === 0 ? "28" : "28"} fontWeight="800" fill="#020617">
              {value}
            </text>
            {sublabel && (
              <text x={x + 34} y="202" fontSize="13.4" fontWeight="800" fill="#64748b">
                {sublabel}
              </text>
            )}
          </g>
        );
      })}

      {statCards.map(({ label, value, details }, index) => {
        const x = 42 + index * 258;
        const inlineDetail = index === 2 ? details[0] : null;
        const lowerDetails = index === 2 ? details.slice(1) : details;
        return (
          <g key={label}>
            <rect x={x} y="220" width="252" height="104" rx="8" fill="#f8fafc" stroke="#e2e8f0" strokeWidth="1" />
            <line x1={x + 16} y1="316" x2={x + 68} y2="316" stroke={statAccentColors[index]} strokeWidth="2.4" strokeLinecap="round" />
            <text x={x + 16} y="247" fontSize={label.length > 23 ? "14.8" : "15.5"} fontWeight="800" fill="#64748b">
              {label}
            </text>
            <text x={x + 16} y="279" fontSize={index === 2 ? "28" : "30"} fontWeight="800" fill="#020617">
              {value}
            </text>
            {inlineDetail && (
              <text x={x + 90} y="278" fontSize="15.2" fontWeight="800" fill="#64748b">
                {inlineDetail}
              </text>
            )}
            {lowerDetails.map((detail, detailIndex) => (
              <text key={detail} x={x + 16} y={lowerDetails.length > 1 ? 296 + detailIndex * 16 : 305} fontSize={index === 2 ? "14" : "15.2"} fontWeight="800" fill="#64748b">
                {detail}
              </text>
            ))}
          </g>
        );
      })}

      <line x1="42" y1="342" x2="1068" y2="342" stroke="#94a3b8" strokeWidth="1.2" />
      <text x="60" y="376" fontSize="17" fontWeight="800" fill="#020617">
        PRS model landscape
      </text>
      {distributions.map((dist, index) => (
        <DistributionAxisRow key={dist.label} dist={dist} y={408 + index * 73} />
      ))}
      <MethodProfileRow y={755} />
      <AncestryProfileRow y={865} />
    </g>
  );
}

function DistributionAxisRow({
  dist,
  y,
}: {
  dist: {
    label: string;
    count: string;
    min: string;
    median: string;
    max: string;
    dots: number[];
    selected: number;
    color: string;
  };
  y: number;
}) {
  const axisX = 320;
  const axisWidth = 700;
  const xScale = scaleLinear().domain([0, 100]).range([axisX, axisX + axisWidth]).clamp(true);
  const selectedX = xScale(dist.selected);

  return (
    <g>
      <text x="60" y={y + 23} fontSize="20" fontWeight="800" fill="#020617">
        {dist.label}
      </text>
      <text x="60" y={y + 47} fontSize="17" fontWeight="800" fill="#64748b">
        {dist.count} reported
      </text>
      <line x1={axisX} y1={y + 34} x2={axisX + axisWidth} y2={y + 34} stroke="#94a3b8" strokeWidth="1.2" />
      <line x1={axisX} y1={y + 24} x2={axisX} y2={y + 44} stroke="#94a3b8" />
      <line x1={axisX + axisWidth / 2} y1={y + 21} x2={axisX + axisWidth / 2} y2={y + 47} stroke="#cbd5e1" strokeDasharray="4 4" />
      <line x1={axisX + axisWidth} y1={y + 24} x2={axisX + axisWidth} y2={y + 44} stroke="#94a3b8" />
      {dist.dots.map((left, index) => (
        <circle
          key={`${dist.label}-${left}-${index}`}
          cx={xScale(left)}
          cy={y + 34 + ((index % 5) - 2) * 2.4}
          r="3.2"
          fill={dist.color}
          opacity="0.46"
        />
      ))}
      <line x1={selectedX} y1={y + 18} x2={selectedX} y2={y + 50} stroke="#0d47a1" strokeWidth="2.2" strokeLinecap="round" />
      <circle cx={selectedX} cy={y + 34} r="7" fill="#ffffff" stroke="#0d47a1" strokeWidth="2.2" />
      <circle cx={selectedX} cy={y + 34} r="2.8" fill="#0d47a1" />
      <text x={axisX} y={y + 65} textAnchor="middle" fontSize="16" fontWeight="800" fill="#64748b">
        min {dist.min}
      </text>
      <text x={axisX + axisWidth / 2} y={y + 65} textAnchor="middle" fontSize="16" fontWeight="800" fill="#0d47a1">
        median {dist.median}
      </text>
      <text x={axisX + axisWidth} y={y + 65} textAnchor="middle" fontSize="16" fontWeight="800" fill="#64748b">
        max {dist.max}
      </text>
    </g>
  );
}

function MethodProfileRow({ y }: { y: number }) {
	  const categories = [
	    { label: ["Pruning +", "thresholding"], count: 54, x: 320, color: "#475569" },
	    { label: ["Penalized", "regression"], count: 17, x: 435, color: "#64748b" },
	    { label: "PRS-CS", count: 19, x: 550, color: "#6d89a5" },
	    { label: "lassosum", count: 17, x: 655, color: "#8b5cf6" },
	    { label: "LDpred2", count: 5, x: 755, color: "#a56a43" },
	    { label: "LDpred", count: 2, x: 840, color: "#b7791f" },
	    { label: "Ensemble", count: 3, x: 920, color: "#0d47a1" },
	    { label: "Other", count: 46, x: 1005, color: "#6f7c42" },
	  ];

  return <CategoricalProfileRow y={y} title="Development methods" subtitle="163 models" categories={categories} />;
}

function AncestryProfileRow({ y }: { y: number }) {
	  const categories = [
	    { label: "European", count: 142, x: 320, color: "#6d89a5" },
	    { label: "Multi-ancestry", count: 11, x: 540, color: "#0d47a1" },
	    { label: "East Asian", count: 7, x: 760, color: "#0f172a" },
	    { label: "African", count: 3, x: 960, color: "#a56a43" },
	  ];

  return <CategoricalProfileRow y={y} title="Training ancestry" subtitle="" categories={categories} />;
}

function CategoricalProfileRow({
  y,
  title,
  subtitle,
  categories,
}: {
  y: number;
  title: string;
  subtitle: string;
  categories: Array<{ label: string | string[]; count: number; x: number; color: string; selected?: boolean; markerX?: number }>;
}) {
  return (
    <g>
      <line x1="42" y1={y - 22} x2="1068" y2={y - 22} stroke="#cbd5e1" />
      <text x="60" y={y + 22} fontSize="20" fontWeight="800" fill="#020617">
        {title}
      </text>
      {subtitle && (
        <text x="60" y={y + 46} fontSize="17" fontWeight="800" fill="#64748b">
          {subtitle}
        </text>
      )}
      {categories.map((category) => (
        <g key={Array.isArray(category.label) ? category.label.join(" ") : category.label}>
          <text x={category.x} y={y + 25} fontSize="30" fontWeight="800" fontFamily="Menlo, Consolas, monospace" fill="#020617">
            {category.count}
          </text>
          {Array.isArray(category.label) ? (
            category.label.map((line, lineIndex) => (
              <text key={line} x={category.x} y={y + 51 + lineIndex * 17} fontSize="17" fontWeight="800" fill="#64748b">
                {line}
              </text>
            ))
          ) : (
            <text x={category.x} y={y + 51} fontSize="17" fontWeight="800" fill="#64748b">
              {category.label}
            </text>
          )}
          <line
            x1={category.x}
            y1={Array.isArray(category.label) ? y + 72 : y + 58}
            x2={category.x + 48}
            y2={Array.isArray(category.label) ? y + 72 : y + 58}
            stroke={category.color}
            strokeWidth="2.2"
            opacity="0.9"
          />
          {category.selected && (
            <g>
              <line
                x1={category.markerX ?? category.x + 48}
                y1={y + 2}
                x2={category.markerX ?? category.x + 48}
                y2={y + 26}
                stroke="#0d47a1"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <circle cx={category.markerX ?? category.x + 48} cy={y + 14} r="6" fill="#ffffff" stroke="#0d47a1" strokeWidth="2" />
              <circle cx={category.markerX ?? category.x + 48} cy={y + 14} r="2.4" fill="#0d47a1" />
            </g>
          )}
        </g>
      ))}
    </g>
  );
}

function PanelCRecommendation() {
  const metricColumns = [
    ["AUC", "0.663", "#0d47a1"],
    ["R2", "0.076", "#7c3aed"],
    ["Development n", "12.5k", "#266798"],
    ["Validation n", "49.0k", "#1560bd"],
    ["Variants", "1.13M", "#d97706"],
  ];
  const contextRows = [
    { label: "Method", value: "Ensemble PRS (MultiPRS-CV)", color: "#0f172a" },
    { label: "Training", value: "European", color: "#0f172a" },
    { label: "Evaluation", value: "European / South Asian", color: "#0f172a" },
    {
      label: "Publication",
      value: "Monti et al., AJHG 2024",
      color: "#0f172a",
      href: "https://doi.org/10.1016/j.ajhg.2024.06.003",
    },
    {
      label: "Download",
      value: "PGS Catalog scoring file",
      color: "#0f172a",
      href: "https://ftp.ebi.ac.uk/pub/databases/spot/pgs/scores/PGS004153/ScoringFiles/PGS004153.txt.gz",
    },
  ];
  return (
    <g fontFamily="Inter, SF Pro Text, -apple-system, BlinkMacSystemFont, Arial, Helvetica, sans-serif">
      <rect x="1118" y="120" width="490" height="138" rx="8" fill="url(#primaryWash)" stroke="#bbdefb" strokeWidth="1.1" />
      <line x1="1128" y1="142" x2="1128" y2="244" stroke="#0d47a1" strokeWidth="5" />
      <text x="1148" y="158" fontSize="17.5" fontWeight="800" fill="#0d47a1">
        Recommended PRS model
      </text>
      <text x="1148" y="204" fontSize="38" fontWeight="800" fontFamily="Menlo, Consolas, monospace" fill="#020617">
        PGS004153
      </text>
      <text x="1148" y="238" fontSize="17" fontWeight="800" fill="#1e293b">
        Breast cancer
      </text>

      <line x1="1128" y1="276" x2="1608" y2="276" stroke="#94a3b8" strokeWidth="1.2" />
      <text x="1128" y="312" fontSize="19" fontWeight="800" fill="#475569">
        Reported evidence on the PGS Catalog
      </text>
      {metricColumns.map(([label, value, color], index) => {
        const x = [1152, 1250, 1364, 1482, 1580][index];
        return (
          <g key={label}>
            <circle cx={x} cy="346" r="4.5" fill={color} />
            <line x1={x + 10} y1="346" x2={x + 45} y2="346" stroke={color} strokeWidth="1.6" opacity="0.75" />
            <text x={x} y="331" textAnchor="middle" fontSize="14.8" fontWeight="800" fill="#64748b">
              {label}
            </text>
            <text x={x} y="377" textAnchor="middle" fontSize="20" fontWeight="800" fontFamily="Menlo, Consolas, monospace" fill="#020617">
              {value}
            </text>
          </g>
        );
      })}

      <line x1="1128" y1="396" x2="1608" y2="396" stroke="#cbd5e1" />
      <text x="1128" y="430" fontSize="19" fontWeight="800" fill="#475569">
        Model details
      </text>
      {contextRows.map(({ label, value, color, href }, index) => (
        <g key={label}>
          <circle cx="1132" cy={468 + index * 31} r="3.5" fill={color} />
          <text x="1148" y={472 + index * 31} fontSize="16.5" fontWeight="800" fill="#64748b">
            {label}
          </text>
          {href ? (
            <a href={href} target="_blank" rel="noreferrer">
              <text x="1258" y={472 + index * 31} fontSize={label === "Download" ? "15" : "15.8"} fontWeight="800" fill="#0d47a1" textDecoration="underline">
                {value}
              </text>
            </a>
          ) : (
            <text x="1258" y={472 + index * 31} fontSize={label === "Method" ? "15" : "15.8"} fontWeight="800" fill="#020617">
              {value}
            </text>
          )}
        </g>
      ))}
      <line x1="1128" y1="645" x2="1608" y2="645" stroke="#cbd5e1" />

      <text x="1128" y="670" fontSize="19" fontWeight="800" fill="#475569">
        Downstream tasks
      </text>
      {[
        {
          title: ["New model training with PennPRS"],
          detail: "Single-, multi-ancestry, or ensemble training plan",
          y: 686,
          accent: "#266798",
          type: "training",
        },
        {
          title: ["Cohort validation"],
          detail: "Selected PRS + target cohort validation report",
          y: 762,
          accent: "#1560bd",
          type: "validation",
        },
        {
          title: ["Risk stratification"],
          detail: "Risk groups in target cohort",
          y: 838,
          accent: "#0d47a1",
          type: "risk",
        },
      ].map((task) => (
        <g key={task.title.join(" ")}>
          <rect x="1128" y={task.y} width="480" height="64" rx="8" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1.1" filter="url(#nodeSoftShadow)" />
          <line x1="1128" y1={task.y} x2="1128" y2={task.y + 64} stroke={task.accent} strokeWidth="4" />
          {task.title.map((line, lineIndex) => (
            <text key={line} x="1144" y={task.y + 21 + lineIndex * 17} fontSize="15.8" fontWeight="800" fill="#020617">
              {line}
            </text>
          ))}
          <text x="1144" y={task.y + (task.title.length > 1 ? 56 : 45)} fontSize="14.6" fontWeight="800" fill="#475569">
            {task.detail}
          </text>
          {task.type === "risk" && (
            <>
              <g clipPath="url(#riskBandClip)">
                {[
                  { width: 49, fill: "#e2e8f0" },
                  { width: 32, fill: "#bbdefb" },
                  { width: 22, fill: "#1560bd" },
                  { width: 15, fill: "#0d47a1" },
                ].map((tier, index) => {
                  const x = 1460 + [0, 49, 81, 103][index];
                  return <rect key={`${task.title}-${index}`} x={x} y={task.y + 22} width={tier.width} height="22" fill={tier.fill} stroke="#ffffff" strokeWidth="1" />;
                })}
              </g>
              <text x="1460" y={task.y + 16} fontSize="13" fontWeight="800" fill="#64748b">
                lower
              </text>
              <text x="1550" y={task.y + 16} fontSize="13" fontWeight="800" fill="#64748b">
                higher
              </text>
              <circle cx="1560" cy={task.y + 33} r="5.5" fill="#ffffff" stroke="#0d47a1" strokeWidth="2" />
            </>
          )}
        </g>
      ))}
    </g>
  );
}

function ScientificCrossFigure() {
  return (
    <ScientificFigureShell
      figure="Figure 2"
      title="Cross-phenotype PRS Agent recommendation report"
      subtitle="Delusional disorders example. No direct PRS model is available, so the report recommends a related schizophrenia PRS for cohort validation."
    >
      <div className="grid h-full grid-cols-[0.72fr_1.45fr_0.83fr] gap-2.5">
        <PanelFigure label="A" title="Target and model gap">
          <CrossTargetGapPanel />
        </PanelFigure>

        <PanelFigure label="B" title="Related phenotype evidence">
          <CrossEvidenceMap />
        </PanelFigure>

        <PanelFigure label="C" title="Recommended source PRS">
          <CompactRecommendationPanel
            outcome="PGS000136"
            trait="Schizophrenia PRS for delusional disorders"
            primaryMetric="AUC 0.6105"
            secondaryMetric="cohort validation"
            bars={[
              ["related trait", 92],
              ["shared biology", 86],
              ["PRS model", 78],
              ["cohort check", 60],
            ]}
            footer={["8 related traits", "no direct PRS", "cohort validation"]}
          />
        </PanelFigure>
      </div>
    </ScientificFigureShell>
  );
}

function ScientificDownstreamFigure() {
  return (
    <ScientificFigureShell
      figure="Figure 3"
      title="Downstream analysis workspace"
      subtitle="Local application workspace. Individual-level data stay local while validation, risk stratification, export, and PennPRS handoff are prepared."
    >
      <div className="grid h-full grid-cols-[0.8fr_1.35fr_0.85fr] gap-2.5">
        <PanelFigure label="A" title="Local analysis boundary">
          <LeanLocalBoundary />
        </PanelFigure>

        <PanelFigure label="B" title="Validation and risk workspace">
          <LeanDownstreamWorkspace />
        </PanelFigure>

        <PanelFigure label="C" title="Export and PennPRS handoff">
          <LeanExportHandoff />
        </PanelFigure>
      </div>
    </ScientificFigureShell>
  );
}

function CrossTargetGapPanel() {
  return (
    <div className="grid h-full grid-rows-[auto_auto_1fr] gap-2">
      <div className="border-2 border-slate-900 bg-slate-50 p-3">
        <div className="text-[10px] font-bold text-slate-500">Target Phenotype</div>
        <div className="mt-1 text-[22px] font-bold leading-7 text-slate-950">Delusional disorders</div>
        <div className="mt-1 font-mono text-[13px] font-bold text-slate-600">ICD-10 F22</div>
      </div>
      <div className="border border-amber-400 bg-amber-50 p-3">
        <div className="text-[10px] font-bold text-amber-700">Direct PRS Model</div>
        <div className="mt-1 text-[32px] font-bold leading-none text-slate-950">none found</div>
      </div>
      <div className="grid min-h-0 grid-rows-[auto_1fr_auto] border border-slate-300 bg-white p-3">
        <div className="text-[10px] font-bold text-slate-500">Best Related Phenotypes</div>
        <div className="my-4 grid content-center gap-4 text-[11px] font-bold text-slate-700">
          {[
            ["Schizophrenia", 100, "0.6105"],
            ["Depression", 94, "0.5748"],
            ["Alcohol use", 92, "0.5595"],
          ].map(([label, width, value], index) => (
            <div key={label} className="grid grid-cols-[82px_1fr_48px] items-center gap-2">
              <div>{label}</div>
              <div className="h-6 bg-slate-200">
                <div className={cn("h-6", index === 0 ? "bg-blue-700" : "bg-slate-400")} style={{ width: `${width}%` }} />
              </div>
              <div className="font-mono">{value}</div>
            </div>
          ))}
        </div>
        <div className="mt-5 grid grid-cols-2 gap-px bg-slate-300 text-center text-[10px] font-bold text-slate-700">
          <div className="bg-slate-50 px-1 py-2">8 related traits</div>
          <div className="bg-slate-50 px-1 py-2">direct model absent</div>
        </div>
      </div>
    </div>
  );
}

function CompactRecommendationPanel({
  outcome,
  trait,
  primaryMetric,
  secondaryMetric,
  bars,
  footer,
}: {
  outcome: string;
  trait: string;
  primaryMetric: string;
  secondaryMetric: string;
  bars: Array<[string, number]>;
  footer: string[];
}) {
  return (
    <div className="grid h-full grid-rows-[auto_auto_1fr_auto] border-2 border-blue-700 bg-blue-50 p-3">
      <div>
        <div className="text-[10px] font-bold tracking-wide text-blue-700">Recommendation</div>
        <div className="mt-1 font-mono text-[34px] font-bold leading-none text-slate-950">{outcome}</div>
        <div className="mt-2 text-[13px] font-bold leading-4 text-slate-800">{trait}</div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-px bg-blue-200 text-[11px] font-bold">
        {[primaryMetric, secondaryMetric].map((item) => (
          <div key={item} className="bg-white px-2 py-3 text-center text-slate-950">{item}</div>
        ))}
      </div>
      <div className="mt-5 flex min-h-0 flex-col justify-center border border-blue-200 bg-white p-4">
        <div className="text-[10px] font-bold text-slate-500">Supporting Evidence</div>
        <div className="mt-6 grid gap-5">
          {bars.map(([label, value], index) => (
            <div key={label} className="grid grid-cols-[106px_1fr_34px] items-center gap-2 text-[10px] font-bold text-slate-700">
              <div>{label}</div>
              <div className="h-7 bg-slate-200">
                <div className={cn("h-7", index < 3 ? "bg-blue-700" : "bg-amber-400")} style={{ width: `${value}%` }} />
              </div>
              <div className="text-right font-mono">{value}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-px bg-blue-200 text-center text-[10px] font-bold text-slate-700">
        {footer.map((item) => (
          <div key={item} className="bg-white px-1 py-2">{item}</div>
        ))}
      </div>
    </div>
  );
}

function CrossEvidenceMap() {
  return (
    <div className="grid h-full grid-cols-[1.2fr_0.8fr] gap-2.5">
      <div className="border border-slate-300 bg-slate-50 p-2.5">
        <svg viewBox="0 0 520 640" className="h-full w-full" role="img" aria-label="Related phenotype evidence map">
          <text x="24" y="38" fontSize="14" fontWeight="700" fill="#475569">related psychiatric phenotypes</text>
          <line x1="124" y1="342" x2="322" y2="132" stroke="#94a3b8" strokeWidth="3.2" />
          <line x1="124" y1="342" x2="366" y2="342" stroke="#94a3b8" strokeWidth="2.4" />
          <line x1="124" y1="342" x2="304" y2="532" stroke="#94a3b8" strokeWidth="2" />
          <circle cx="124" cy="342" r="60" fill="#1e293b" />
          <text x="124" y="337" textAnchor="middle" fontSize="19" fontWeight="700" fill="#ffffff">F22</text>
          <text x="124" y="362" textAnchor="middle" fontSize="12" fill="#cbd5e1">target</text>
          <circle cx="322" cy="132" r="60" fill="#1d4ed8" />
          <text x="322" y="125" textAnchor="middle" fontSize="13" fontWeight="700" fill="#ffffff">Schizophrenia</text>
          <text x="322" y="149" textAnchor="middle" fontSize="12" fill="#dbeafe">recommended</text>
          <circle cx="366" cy="342" r="42" fill="#059669" />
          <text x="366" y="338" textAnchor="middle" fontSize="12" fontWeight="700" fill="#ffffff">Depression</text>
          <circle cx="304" cy="532" r="36" fill="#f59e0b" />
          <text x="304" y="528" textAnchor="middle" fontSize="11" fontWeight="700" fill="#ffffff">Alcohol</text>
          <text x="304" y="544" textAnchor="middle" fontSize="11" fontWeight="700" fill="#ffffff">use</text>
        </svg>
      </div>
      <div className="grid h-full grid-rows-[auto_1fr] gap-2">
        <div className="border-2 border-blue-700 bg-blue-50 p-3">
          <div className="text-[10px] font-bold text-blue-700">Recommended Related Phenotype</div>
          <div className="mt-2 text-[25px] font-bold leading-none text-slate-950">Schizophrenia</div>
          <div className="mt-2 font-mono text-[24px] font-bold leading-none text-slate-950">0.6105</div>
        </div>
        <div className="border border-slate-300 bg-white p-3">
          <div className="text-[10px] font-bold text-slate-500">Related Phenotype Ranking</div>
          <div className="mt-4 grid gap-3 text-[10px] font-bold text-slate-700">
            {[
              ["Schizophrenia", "PGS000136", 100],
              ["Depression", "PGS002204", 94],
              ["Alcohol use", "PGS004519", 92],
              ["Anxiety", "PGS004521", 91],
            ].map(([source, model, width], index) => (
              <div key={source} className="grid grid-cols-[82px_72px_1fr] items-center gap-2">
                <div className={index === 0 ? "text-blue-700" : "text-slate-700"}>{source}</div>
                <div className="font-mono text-slate-700">{model}</div>
                <div className="h-3 bg-slate-200">
                  <div className={cn("h-3", index === 0 ? "bg-blue-700" : "bg-slate-400")} style={{ width: `${width}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function LeanLocalBoundary() {
  return (
    <div className="grid h-full grid-rows-[auto_1fr_auto] gap-2">
      <div className="border-2 border-blue-700 bg-blue-50 p-3">
        <div className="text-[10px] font-bold uppercase text-blue-700">Installable application</div>
        <div className="mt-1 text-lg font-bold text-slate-950">local runtime</div>
      </div>
      <div className="grid min-h-0 grid-cols-[0.78fr_auto_1.18fr_auto_0.78fr] items-stretch gap-1.5">
        <div className="grid gap-1.5">
          {["PGS", "genotype", "phenotype", "covariates"].map((item) => (
            <div key={item} className="flex items-center border border-slate-300 bg-white px-2 text-[12px] font-bold text-slate-900">{item}</div>
          ))}
        </div>
        <div className="flex items-center text-lg font-bold text-slate-500">-&gt;</div>
        <div className="border-2 border-blue-700 bg-blue-50 p-2">
          <div className="grid h-full grid-rows-[auto_1fr]">
            <div className="text-center text-[11px] font-bold uppercase text-blue-700">PRS Agent</div>
            <div className="mt-3 grid min-h-0 grid-rows-3 gap-2">
              {["recommend", "validate", "handoff"].map((item, index) => (
                <div key={item} className={cn("flex items-center justify-center border text-[12px] font-bold", index === 0 ? "border-blue-700 bg-blue-700 text-white" : "border-blue-200 bg-white text-slate-900")}>
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-center text-lg font-bold text-slate-500">-&gt;</div>
        <div className="grid gap-1.5">
          {["metrics", "risk", "subgroups", "plan"].map((item) => (
            <div key={item} className="flex items-center border border-slate-300 bg-slate-50 px-2 text-[12px] font-bold text-slate-900">{item}</div>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-px bg-slate-300 text-center text-[11px] font-bold text-slate-700">
        <div className="bg-slate-50 px-1 py-2">individual-level data local</div>
        <div className="bg-slate-50 px-1 py-2">only reports/configs exported</div>
      </div>
    </div>
  );
}

function LeanDownstreamWorkspace() {
  return (
    <div className="grid h-full grid-cols-[1.2fr_0.8fr] gap-2.5">
      <div className="flex h-full flex-col border border-slate-300 bg-slate-50 p-3">
        <div className="text-[13px] font-bold text-slate-950">Risk stratification</div>
        <svg viewBox="0 0 420 620" className="mt-3 min-h-0 flex-1" role="img" aria-label="Risk stratification by PRS percentile">
          <line x1="42" y1="520" x2="390" y2="520" stroke="#94a3b8" strokeWidth="2" />
          <line x1="42" y1="72" x2="42" y2="520" stroke="#94a3b8" strokeWidth="2" />
          {[21, 31, 47, 68, 96].map((height, index) => {
            const barHeight = height * 4.35;
            const x = 66 + index * 66;
            return (
              <g key={index}>
                <rect x={x} y={520 - barHeight} width="42" height={barHeight} fill="#1d4ed8" />
                <text x={x + 21} y="556" textAnchor="middle" fontSize="13" fontWeight="700" fill="#64748b">
                  {["0-20", "20-40", "40-60", "60-80", "80-100"][index]}
                </text>
              </g>
            );
          })}
          <text x="215" y="592" textAnchor="middle" fontSize="15" fontWeight="700" fill="#475569">PRS percentile bin</text>
        </svg>
        <div className="mt-4 grid grid-cols-[86px_repeat(5,1fr)] gap-px bg-slate-300 text-center text-[10px] font-bold">
          <div className="bg-slate-200 px-1 py-1.5">PRS bin</div>
          {["0-20", "20-40", "40-60", "60-80", "80-100"].map((bin) => <div key={bin} className="bg-slate-200 px-1 py-1.5">{bin}</div>)}
          <div className="bg-white px-1 py-1.5">risk ratio</div>
          {["1.0", "1.2", "1.6", "2.1", "3.0"].map((value) => <div key={value} className="bg-white px-1 py-1.5 font-mono text-blue-700">{value}</div>)}
        </div>
      </div>
      <div className="grid h-full grid-rows-[0.78fr_1.22fr] gap-2.5">
        <div className="flex min-h-0 flex-col border border-slate-300 bg-white p-3">
          <div className="text-[10px] font-bold uppercase text-slate-500">Calibration</div>
          <svg viewBox="0 0 250 150" className="mt-2 min-h-0 flex-1" role="img" aria-label="Calibration curve">
            <line x1="28" y1="120" x2="220" y2="120" stroke="#64748b" />
            <line x1="28" y1="20" x2="28" y2="120" stroke="#64748b" />
            <path d="M28 120 C76 96, 118 74, 160 48 S205 28, 220 24" fill="none" stroke="#1d4ed8" strokeWidth="5" />
            <path d="M28 120 L220 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="5 5" />
          </svg>
        </div>
        <div className="border border-slate-300 bg-slate-50 p-3">
          <div className="text-[10px] font-bold uppercase text-slate-500">Subgroup checks</div>
          <div className="mt-3 grid grid-cols-[80px_repeat(3,1fr)] gap-px bg-slate-300 text-center text-[10px] font-bold">
            {["strata", "AUC", "cal", "N"].map((item) => <div key={item} className="bg-slate-200 px-1 py-1.5">{item}</div>)}
            {["EUR", "AFR", "EAS", "sex", "site"].map((strata, row) => (
              <div key={strata} className="contents">
                <div className="bg-white px-1 py-2">{strata}</div>
                {[0, 1, 2].map((col) => (
                  <div key={`${strata}-${col}`} className={cn("bg-white px-1 py-2", row + col < 3 ? "text-emerald-700" : "text-amber-700")}>
                    {row + col < 3 ? "ready" : "check"}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function LeanExportHandoff() {
  return (
    <div className="grid h-full grid-rows-[auto_auto_1fr] gap-2.5">
      <div className="border border-slate-300 bg-white p-3">
        <div className="text-[10px] font-bold uppercase text-slate-500">Export bundle</div>
        <div className="mt-2 grid grid-cols-2 gap-1.5 text-[11px] font-mono font-bold text-slate-700">
          {["report.md", "models.csv", "metrics.json", "plan.yaml"].map((item) => (
            <div key={item} className="border border-slate-300 bg-slate-50 px-2 py-2">{item}</div>
          ))}
        </div>
      </div>
      <div className="border-2 border-blue-700 bg-blue-50 p-3">
        <div className="text-[10px] font-bold uppercase text-blue-700">PennPRS training</div>
        <div className="mt-2 grid grid-cols-3 gap-1.5 text-center text-[11px] font-bold text-slate-800">
          {["single", "multi", "ensemble"].map((item) => (
            <div key={item} className="border border-blue-200 bg-white px-1 py-3">{item}</div>
          ))}
        </div>
      </div>
      <div className="flex min-h-0 flex-col border border-slate-300 bg-slate-50 p-3">
        <div className="text-[10px] font-bold uppercase text-slate-500">Handoff path</div>
        <svg viewBox="0 0 280 420" className="mt-2 min-h-0 flex-1 w-full" role="img" aria-label="PennPRS handoff path">
          {[
            ["selected PGS", 48],
            ["local validation", 176],
            ["train config", 304],
          ].map(([label, y], index) => (
            <g key={label}>
              <rect x="28" y={Number(y)} width="224" height="54" fill={index === 2 ? "#dbeafe" : "#ffffff"} stroke={index === 2 ? "#1d4ed8" : "#cbd5e1"} strokeWidth={index === 2 ? 2 : 1.3} />
              <text x="140" y={Number(y) + 34} textAnchor="middle" fontSize="14" fontWeight="700" fill="#0f172a">{label}</text>
              {index < 2 && <line x1="140" y1={Number(y) + 54} x2="140" y2={Number(y) + 128} stroke="#64748b" strokeWidth="3" />}
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}

const withinDistributionDots = {
  sample: dotPositions(
    "47.7,38.7,38.7,47.7,38.7,38.7,70.7,12.8,57.1,83.3,83.3,83.3,83.3,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,43.2,43.2,43.2,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,43.2,71.7,89.3,89.3,78.1,94,94,83.8,79.2,36.5,28,28,50,50,50,50,50,50,50,50,50,50,50,85.4,85.4,85.4,85.4,85.4,81.3,81.3,81.3,81.3,83.7,83.7,28.7,84.9,57.7,57.7,6,62.4,62.4,62.4"
  ),
  auc: dotPositions(
    "54.4,51,36.9,62.1,62.6,45.2,94,59.4,44.7,70.6,60.2,78.4,39.8,39.8,35.5,47.6,67.4,56.8,63,55.7,58.4,52.6,56.5,54.9,86.2,50.5,50,41.8,54.2,34.5,33.1,35,37.9,37.4,35.5,42.3,44.7,33.1,34,36.9,42.3,6,48.1,40.8,48.1,43.7,27.3,24.9,34,34.5,33.1,24.9,30.7,33.1,50.8,50.5,58.3,57.6,52.6,52.6,56,55.2,53.6,52.9,60.4,60.7,56.2,54.9,57.8,58.3,42.3,39.8,47.1,49,20.5,16.6,15.2,20,19.5,19.1,18.6,19.1,43.2,43.2,50.5,50.8,43.2,44.7,49.5,48.5,48.1,45.2,52.9,53.1,49,45.6,53.4,51,29.2,33.1,34,56.8,44.7,42.9,9.4,72.5,59.6,72.1,35,44.7,52.3,52.3,43.7,37.9,61,60.8,62.7,62.7,60.9,61.7,61.5,51.8,54.4,61.2,63.4,59.7,58.1,59.4,58.9,58.7,57.9,57.6,57.9,58,64.1,57.6,35.5,48.5,33.1,44.7,44.7,52.3,42.7"
  ),
  r2: dotPositions(
    "47.5,36.4,30.3,33.8,35.1,38.8,34.6,45.3,50.6,33.4,32.9,37.8,46.5,7.1,52.3,36.1,52.3,40.1,22.4,17.2,32.3,26.7,31.3,17.2,27.7,25.9,53.7,51,61.9,56.7,55.7,52.3,59.8,54.6,56.6,52.8,64.1,59.8,59.2,54.3,61.5,57.6,45.7,43.8,50.8,52.1,18.5,10.8,9.9,11.3,17.9,12.7,18.7,12.5,50,40.5,53.7,50.7,49.3,43.3,53.2,50,52.6,43.5,55.9,52.8,52.5,44.1,56.7,51.4,94,29.1,6,60.1,64.3,64.3,66.9,67,64.7,65.9,65.4,53.8,56.3,64.9,67.9,46.7,44.8,46.4,47.9,53.6,53.6"
  ),
  variants: dotPositions(
    "32.2,32.2,32.2,49.4,49.4,49.4,60.9,60.9,60.9,62.3,33.1,32.1,33.9,33.7,27.7,25.4,30.5,41.2,43.1,30.3,50,50,50,50,50,42.6,93.9,86,48.3,45.5,48.3,48.3,16.9,86.1,30.7,70.1,21.5,86.1,37.6,58.6,15.8,86.1,24.8,61.2,18.5,29.6,33.6,29.6,32.5,26.7,26.7,86.2,86.2,44.9,26.7,68,71.5,46.9,46.9,86.2,86.2,55.5,53.6,73.3,77.2,50.1,50.1,86.2,86.2,59.9,57.2,76.2,80.1,24.5,86.2,33.3,63.6,7.3,7.3,86.2,86.2,6,11.4,47.5,59.4,33.6,33.6,86.2,86.2,49.2,42.2,75.3,66.1,36.6,36.6,86.2,86.2,50.4,33.4,67.9,63.7,42.5,42.5,42.5,41.3,39.8,52.3,43.6,12.2,59.8,82.5,94,36.7,86.3,8.5,24.8,39.2,44.4,39.2,72.1,67.6,86.2,66.4,85.9,85.9,85.1,85.1,86.1,44.4,54.9,85.4,86.2,61,53.5,61.7,56.3,58.6,49.1,39.5,32.7,34.1,54.5,85.9,85.9,86,32.1,85.9,91.5,91.5,36,36,36,85.1,18.5,18.5,24.5,72.9,70,69.8,34,25.4,18,36.5"
  ),
};

function dotPositions(value: string) {
  return value.split(",").map(Number);
}

function SectionLabel({ children }: { children: string }) {
  return <div className="text-xs font-semibold uppercase text-slate-500">{children}</div>;
}

function TraitRoute({
  title,
  subtitle,
  active,
  onClick,
}: {
  title: string;
  subtitle: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "block w-full rounded-lg border px-3 py-2 text-left",
        active ? "border-slate-300 bg-white shadow-sm" : "border-transparent hover:border-slate-200 hover:bg-white"
      )}
    >
      <div className="text-sm font-medium text-slate-900">{title}</div>
      <div className="text-xs text-slate-500">{subtitle}</div>
    </button>
  );
}

function SidebarStatus({ icon: Icon, label }: { icon: LucideIcon; label: string }) {
  return (
    <div className="flex items-center gap-2 rounded-md bg-white px-3 py-2 text-xs text-slate-700 shadow-sm dark:bg-slate-950 dark:text-slate-300">
      <Icon className="size-3.5 text-blue-700" />
      {label}
    </div>
  );
}

function WithinPhenotypeReport({ theme }: { theme: ThemeMode }) {
  return (
    <FigurePageFrame theme={theme}>
      <ReportHeader
        label="Within-phenotype PRS Agent recommendation report"
        title="Breast carcinoma"
        subtitle="Direct model selection from a breast cancer PRS landscape"
        badges={["direct phenotype match", "model landscape visible", "review-ready report"]}
      />

      <div className="grid items-start gap-4 xl:grid-cols-[0.62fr_1.38fr]">
        <OutcomeBand
          title="Recommended PRS model"
          value="PGS004153"
          detail="UKBB-EUR.MultiPRS.CV selected after comparing breast cancer candidate models."
          status="Direct use supported with cohort validation"
          icon={CheckCircle2}
        />

        <Panel title="Candidate model landscape" icon={BarChart3}>
          <ModelLandscape models={withinModels} metric="auc" />
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
        <section className="space-y-4">
          <OutcomeBand
            title="Recommendation interpretation"
            value="Direct"
            detail="The selected model is a within-phenotype recommendation, not a cross-phenotype transfer."
            status="Alternatives and caveats retained for review"
            icon={ShieldCheck}
          />

          <Panel title="Evidence supporting direct use" icon={BookOpenCheck}>
            <EvidenceGrid items={withinEvidence} />
          </Panel>
        </section>

        <section className="space-y-4">
          <Panel title="User input contract" icon={Search}>
            <div className="grid gap-3 sm:grid-cols-2">
              <InputSummary label="Target phenotype" value="Breast carcinoma" />
              <InputSummary label="Population context" value="multi-ancestry research cohort" />
              <InputSummary label="Recommendation mode" value="within-phenotype" />
              <InputSummary label="Output requested" value="model recommendation + validation plan" />
            </div>
          </Panel>

          <Panel title="Ranked candidate table" icon={Table2}>
            <ModelTable models={withinModels.slice(0, 6)} />
          </Panel>

          <Panel title="Recommendation record" icon={FileText}>
            <RecordList
              items={[
                ["Selected model", "PGS004153"],
                ["Alternatives retained", "PGS004040, PGS004025, PGS004083"],
                ["Primary caveat", "validate in user cohort before downstream use"],
                ["Export bundle", "report, model table, evidence snapshot"],
              ]}
            />
          </Panel>
        </section>
      </div>
    </FigurePageFrame>
  );
}

function CrossPhenotypeReport({ theme }: { theme: ThemeMode }) {
  return (
    <FigurePageFrame theme={theme}>
      <ReportHeader
        label="Cross-phenotype PRS Agent recommendation report"
        title="Bipolar disorder"
        subtitle="Transfer recommendation from a related psychiatric phenotype when direct evidence is weak"
        badges={["source phenotype scouting", "genetic evidence", "Open Targets support", "validation needs visible"]}
      />

      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <section className="space-y-4">
          <Panel title="Transfer decision path" icon={GitBranch}>
            <TransferPath />
          </Panel>

          <Panel title="Cross-phenotype evidence" icon={Network}>
            <EvidenceGrid items={crossEvidence} />
          </Panel>

          <OutcomeBand
            title="Transferable source model"
            value="PGS000135"
            detail="Schizophrenia PRS-CS model selected as the leading transferable candidate for prototype review."
            status="Transfer requires target-cohort validation"
            icon={BrainCircuit}
          />
        </section>

        <section className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Panel title="Direct bipolar evidence" icon={Database}>
              <CompactModelList models={crossTargetModels} />
            </Panel>
            <Panel title="Source phenotype models" icon={Layers3}>
              <CompactModelList models={crossSourceModels} />
            </Panel>
          </div>

          <Panel title="Source model landscape" icon={BarChart3}>
            <ModelLandscape models={[...crossTargetModels, ...crossSourceModels]} metric="mixed" />
          </Panel>

          <Panel title="Uncertainty and validation needs" icon={ClipboardCheck}>
            <div className="grid gap-3 md:grid-cols-3">
              <ValidationNeed title="Confirm transfer" detail="Test selected score on bipolar disorder outcomes." />
              <ValidationNeed title="Check ancestry" detail="Evaluate whether source validation transfers to the target cohort." />
              <ValidationNeed title="Retain alternatives" detail="Keep direct bipolar scores and source alternatives visible for expert review." />
            </div>
          </Panel>
        </section>
      </div>
    </FigurePageFrame>
  );
}

function DownstreamWorkspace({ theme }: { theme: ThemeMode }) {
  return (
    <FigurePageFrame theme={theme}>
      <ReportHeader
        label="Downstream analysis workspace"
        title="Selected PRS model: PGS004153"
        subtitle="Local validation and downstream analysis planning after model recommendation"
        badges={["locally installable application", "individual-level data stays local", "analysis plan export"]}
      />

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <section className="space-y-4">
          <Panel title="Local analysis workspace" icon={LockKeyhole}>
            <LocalWorkspaceDiagram />
          </Panel>

          <Panel title="Downstream analysis plan" icon={ClipboardCheck}>
            <div className="grid gap-3 md:grid-cols-2">
              {downstreamSteps.map((step) => (
                <WorkflowStep key={step.title} step={step} />
              ))}
            </div>
          </Panel>
        </section>

        <section className="space-y-4">
          <Panel title="Validation and risk stratification" icon={BarChart3}>
            <DownstreamCharts />
          </Panel>

          <Panel title="Recommendation record for user review" icon={FileText}>
            <div className="grid gap-4 md:grid-cols-[0.9fr_1.1fr]">
              <RecordList
                items={[
                  ["Target phenotype", "Breast carcinoma"],
                  ["Selected PGS", "PGS004153"],
                  ["Analysis population", "local cohort with genotype and covariate files"],
                  ["Privacy mode", "no individual-level data leaves local environment"],
                  ["Next action", "validate, stratify, export analysis plan"],
                ]}
              />
              <ExportBundle />
            </div>
          </Panel>
        </section>
      </div>
    </FigurePageFrame>
  );
}

function FigurePageFrame({ children, theme }: { children: React.ReactNode; theme: ThemeMode }) {
  return (
    <div className={cn("mx-auto w-full max-w-[1480px] px-5 py-5 lg:px-8", theme === "light" ? "bg-white" : "bg-slate-950")}>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

function ReportHeader({
  label,
  title,
  subtitle,
  badges,
}: {
  label: string;
  title: string;
  subtitle: string;
  badges: string[];
}) {
  return (
    <section className="border-b border-slate-200 pb-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-blue-700">{label}</div>
          <h1 className="mt-1 text-3xl font-semibold leading-tight text-slate-950">{title}</h1>
          <p className="mt-2 max-w-3xl text-base leading-7 text-slate-600">{subtitle}</p>
        </div>
        <div className="flex flex-wrap gap-2 lg:justify-end">
          {badges.map((badge) => (
            <span key={badge} className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1.5 text-xs font-medium text-slate-700">
              {badge}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function Panel({ title, icon: Icon, children }: { title: string; icon: LucideIcon; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
        <div className="flex items-center gap-2">
          <Icon className="size-4 text-blue-700" />
          <h2 className="text-sm font-semibold text-slate-950">{title}</h2>
        </div>
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}

function OutcomeBand({
  title,
  value,
  detail,
  status,
  icon: Icon,
}: {
  title: string;
  value: string;
  detail: string;
  status: string;
  icon: LucideIcon;
}) {
  return (
    <section className="rounded-lg border border-blue-200 bg-blue-50 p-4">
      <div className="flex items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-blue-700 text-white">
          <Icon className="size-5" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold text-blue-950">{title}</div>
          <div className="mt-1 font-mono text-2xl font-semibold text-slate-950">{value}</div>
          <p className="mt-2 text-sm leading-6 text-slate-700">{detail}</p>
          <div className="mt-3 inline-flex rounded-md border border-blue-200 bg-white px-2.5 py-1 text-xs font-medium text-blue-800">
            {status}
          </div>
        </div>
      </div>
    </section>
  );
}

function InputSummary({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-900">{value}</div>
    </div>
  );
}

function EvidenceGrid({ items }: { items: EvidenceItem[] }) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div key={item.label} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-start gap-3">
              <div
                className={cn(
                  "flex size-8 shrink-0 items-center justify-center rounded-md",
                  item.status === "selected" && "bg-blue-700 text-white",
                  item.status === "supported" && "bg-emerald-100 text-emerald-700",
                  item.status === "review" && "bg-amber-100 text-amber-700"
                )}
              >
                <Icon className="size-4" />
              </div>
              <div className="min-w-0">
                <div className="text-xs font-medium text-slate-500">{item.label}</div>
                <div className="mt-1 text-sm font-semibold text-slate-950">{item.value}</div>
                <p className="mt-1 text-xs leading-5 text-slate-600">{item.detail}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ModelLandscape({ models, metric }: { models: ModelDatum[]; metric: "auc" | "mixed" }) {
  const plotted = models.map((model, index) => {
    const xMetric = model.auc ?? 0.55 + index * 0.025;
    const yMetric = model.r2 ?? (model.auc ? model.auc / 18 : 0.012 + index * 0.002);
    const x = Math.max(8, Math.min(92, ((xMetric - 0.55) / 0.22) * 76 + 10));
    const y = Math.max(12, Math.min(86, 88 - (yMetric / 0.085) * 68));
    return { ...model, x, y };
  });

  return (
    <div className="grid gap-3">
      <div className="rounded-lg border border-slate-200 bg-white p-3">
        <div className="mb-2 flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold text-slate-950">Model landscape summary</div>
            <div className="text-xs text-slate-500">
              {metric === "auc" ? "x = AUC, y = R2, marker = candidate model" : "x = reported discrimination, y = available PRS signal"}
            </div>
          </div>
          <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600">{models.length} shown</span>
        </div>
        <svg viewBox="0 0 560 180" role="img" aria-label="PRS model landscape plot" className="h-[170px] w-full">
          <rect x="0" y="0" width="560" height="180" rx="8" fill="#f8fafc" />
          <line x1="46" y1="22" x2="46" y2="142" stroke="#cbd5e1" />
          <line x1="46" y1="142" x2="530" y2="142" stroke="#cbd5e1" />
          {[54, 86, 118].map((y) => (
            <line key={y} x1="46" y1={y} x2="530" y2={y} stroke="#e2e8f0" strokeDasharray="4 5" />
          ))}
          {[150, 270, 390].map((x) => (
            <line key={x} x1={x} y1="22" x2={x} y2="142" stroke="#e2e8f0" strokeDasharray="4 5" />
          ))}
          <text x="46" y="164" fontSize="11" fill="#64748b">lower reported performance</text>
          <text x="382" y="164" fontSize="11" fill="#64748b">higher reported performance</text>
          <text x="12" y="36" fontSize="11" fill="#64748b">stronger PRS signal</text>
          {plotted.map((model) => {
            const cx = 46 + (model.x / 100) * 484;
            const cy = 22 + (model.y / 100) * 120;
            const selected = model.role === "selected";
            return (
              <g key={model.id}>
                {selected && <circle cx={cx} cy={cy} r="16" fill="#bfdbfe" opacity="0.9" />}
                <circle
                  cx={cx}
                  cy={cy}
                  r={selected ? 8 : model.role === "alternative" ? 6 : 5}
                  fill={selected ? "#1d4ed8" : model.role === "alternative" ? "#0f766e" : "#94a3b8"}
                  stroke="#ffffff"
                  strokeWidth="2"
                />
                {selected && (
                  <text x={cx + 13} y={cy - 10} fontSize="12" fontWeight="600" fill="#1e3a8a">
                    {model.id}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        <LandscapeMetric label="Selected model" value={models.find((model) => model.role === "selected")?.id || "N/A"} />
        <LandscapeMetric label="Top reported AUC" value={formatNumber(Math.max(...models.map((model) => model.auc || 0)))} />
        <LandscapeMetric label="Visible methods" value={String(new Set(models.map((model) => model.method)).size)} />
        <LandscapeMetric label="Ancestry context" value="visible" />
      </div>
    </div>
  );
}

function LandscapeMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 truncate font-mono text-base font-semibold text-slate-950">{value}</div>
    </div>
  );
}

function ModelTable({ models }: { models: ModelDatum[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead className="bg-slate-50 text-xs text-slate-500">
          <tr>
            <th className="px-3 py-2 font-medium">Role</th>
            <th className="px-3 py-2 font-medium">PGS ID</th>
            <th className="px-3 py-2 font-medium">Trait</th>
            <th className="px-3 py-2 font-medium">Method</th>
            <th className="px-3 py-2 font-medium">AUC</th>
            <th className="px-3 py-2 font-medium">R2</th>
            <th className="px-3 py-2 font-medium">Ancestry context</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {models.map((model) => (
            <tr key={model.id} className={model.role === "selected" ? "bg-blue-50" : "bg-white"}>
              <td className="px-3 py-2">
                <RolePill role={model.role} />
              </td>
              <td className="px-3 py-2 font-mono text-xs font-semibold text-slate-950">{model.id}</td>
              <td className="max-w-[170px] truncate px-3 py-2 text-slate-700">{model.trait}</td>
              <td className="max-w-[190px] truncate px-3 py-2 text-slate-700">{model.method}</td>
              <td className="px-3 py-2 font-mono text-xs text-slate-700">{model.auc ? formatNumber(model.auc) : "N/A"}</td>
              <td className="px-3 py-2 font-mono text-xs text-slate-700">{model.r2 ? formatNumber(model.r2) : "N/A"}</td>
              <td className="max-w-[220px] truncate px-3 py-2 text-xs text-slate-500">{model.ancestry}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RolePill({ role }: { role: ModelDatum["role"] }) {
  return (
    <span
      className={cn(
        "rounded-md px-2 py-1 text-xs font-medium",
        role === "selected" && "bg-blue-700 text-white",
        role === "alternative" && "bg-teal-100 text-teal-800",
        role === "context" && "bg-slate-100 text-slate-600"
      )}
    >
      {role}
    </span>
  );
}

function RecordList({ items }: { items: Array<[string, string]> }) {
  return (
    <div className="divide-y divide-slate-200 rounded-lg border border-slate-200">
      {items.map(([label, value]) => (
        <div key={label} className="grid grid-cols-[150px_1fr] gap-3 px-3 py-2 text-sm">
          <div className="text-slate-500">{label}</div>
          <div className="min-w-0 truncate font-medium text-slate-900">{value}</div>
        </div>
      ))}
    </div>
  );
}

function TransferPath() {
  const steps = [
    ["Target", "Bipolar disorder", "direct evidence weak"],
    ["Scout", "psychiatric source phenotypes", "evidence channels queried"],
    ["Source", "Schizophrenia", "best supported transfer source"],
    ["Model", "PGS000135", "validate before use"],
  ];
  return (
    <div className="grid gap-3">
      {steps.map(([label, value, detail], index) => (
        <div key={label} className="flex items-center gap-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-blue-700 text-sm font-semibold text-white">{index + 1}</div>
          <div className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
            <div className="flex items-center justify-between gap-3">
              <div className="text-xs font-medium text-slate-500">{label}</div>
              <div className="text-xs text-slate-500">{detail}</div>
            </div>
            <div className="mt-1 truncate text-sm font-semibold text-slate-950">{value}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function CompactModelList({ models }: { models: ModelDatum[] }) {
  return (
    <div className="space-y-2">
      {models.map((model) => (
        <div key={model.id} className={cn("rounded-lg border p-3", model.role === "selected" ? "border-blue-200 bg-blue-50" : "border-slate-200 bg-white")}>
          <div className="flex items-center justify-between gap-3">
            <div className="font-mono text-sm font-semibold text-slate-950">{model.id}</div>
            <RolePill role={model.role} />
          </div>
          <div className="mt-1 text-sm text-slate-700">{model.trait}</div>
          <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
            <MiniMetric label="AUC" value={model.auc ? formatNumber(model.auc) : "N/A"} />
            <MiniMetric label="R2" value={model.r2 ? formatNumber(model.r2) : "N/A"} />
            <MiniMetric label="method" value={model.method} />
          </div>
        </div>
      ))}
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md bg-slate-50 px-2 py-1.5">
      <div className="text-[11px] text-slate-500">{label}</div>
      <div className="mt-0.5 truncate font-mono text-xs font-medium text-slate-900">{value}</div>
    </div>
  );
}

function ValidationNeed({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
      <div className="text-sm font-semibold text-amber-950">{title}</div>
      <p className="mt-1 text-xs leading-5 text-amber-900">{detail}</p>
    </div>
  );
}

function LocalWorkspaceDiagram() {
  const nodes = [
    { title: "Selected PGS", detail: "PGS004153", icon: Database },
    { title: "Local cohort", detail: "genotype + phenotype + covariates", icon: LockKeyhole },
    { title: "Analysis plan", detail: "validation, stratification, subgroup checks", icon: ClipboardCheck },
  ];
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {nodes.map((node, index) => {
        const Icon = node.icon;
        return (
          <div key={node.title} className="relative rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="flex size-10 items-center justify-center rounded-lg bg-white text-blue-700 shadow-sm">
              <Icon className="size-5" />
            </div>
            <div className="mt-3 text-sm font-semibold text-slate-950">{node.title}</div>
            <div className="mt-1 text-xs leading-5 text-slate-600">{node.detail}</div>
            {index < nodes.length - 1 && <div className="absolute -right-2 top-1/2 hidden h-px w-4 bg-slate-300 md:block" />}
          </div>
        );
      })}
    </div>
  );
}

function WorkflowStep({ step }: { step: (typeof downstreamSteps)[number] }) {
  const Icon = step.icon;
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-slate-100 text-blue-700">
            <Icon className="size-4" />
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-950">{step.title}</div>
            <p className="mt-1 text-xs leading-5 text-slate-600">{step.detail}</p>
          </div>
        </div>
        <span className="shrink-0 rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-medium text-slate-600">{step.status}</span>
      </div>
    </div>
  );
}

function DownstreamCharts() {
  const bins = [
    ["0-20", 18],
    ["20-40", 27],
    ["40-60", 36],
    ["60-80", 52],
    ["80-100", 74],
  ];
  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_0.9fr]">
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
        <div className="text-sm font-semibold text-slate-950">Risk stratification preview</div>
        <div className="mt-4 flex h-48 items-end gap-3">
          {bins.map(([label, height]) => (
            <div key={label} className="flex flex-1 flex-col items-center gap-2">
              <div className="w-full rounded-t-md bg-blue-700" style={{ height: `${Number(height) * 1.55}px` }} />
              <div className="text-xs text-slate-500">{label}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="space-y-3">
        <AnalysisMetric title="Discrimination" value="AUC / C-index" detail="computed in target cohort" />
        <AnalysisMetric title="Calibration" value="observed vs expected risk" detail="checked by risk bin" />
        <AnalysisMetric title="Subgroup review" value="ancestry, sex, age, site" detail="kept visible before export" />
      </div>
    </div>
  );
}

function AnalysisMetric({ title, value, detail }: { title: string; value: string; detail: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-1 text-sm font-semibold text-slate-950">{value}</div>
      <div className="mt-1 text-xs text-slate-600">{detail}</div>
    </div>
  );
}

function ExportBundle() {
  const exports = [
    "recommendation-report.md",
    "candidate-models.csv",
    "validation-plan.json",
    "local-analysis-config.yaml",
  ];
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-950">
        <ArrowDownToLine className="size-4 text-blue-700" />
        Export bundle
      </div>
      <div className="space-y-2">
        {exports.map((item) => (
          <div key={item} className="flex items-center gap-2 rounded-md bg-white px-3 py-2 text-xs text-slate-700 shadow-sm">
            <FileText className="size-3.5 text-slate-500" />
            <span className="font-mono">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatNumber(value: number) {
  return value.toFixed(value < 0.1 ? 3 : 3).replace(/0+$/, "").replace(/\.$/, "");
}
