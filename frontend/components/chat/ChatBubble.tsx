import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'
import { Bot, User, Activity, Layers, Dna, Download, PlusCircle } from 'lucide-react'
import ModelCard, { ModelData } from "../ModelCard"
import { ProgressBar } from "../ProgressBar"

interface ChatBubbleProps {
    role: 'user' | 'agent'
    content: string
    modelCard?: ModelData
    actions?: string[]
    progress?: {
        status: string;
        total: number;
        fetched: number;
        current_action: string;
    } | null;
    footer?: string; // New prop for text below progress bar
    onViewDetails?: (model: ModelData) => void
    onTrainNew?: () => void
    onDownstreamAction?: (action: string) => void
}

const getActionIcon = (action: string) => {
    if (action.includes("Evaluate")) return <Activity className="w-4 h-4" />;
    if (action.includes("Ensemble")) return <Layers className="w-4 h-4" />;
    if (action.includes("Proteomics")) return <Dna className="w-4 h-4" />;
    if (action.includes("Download")) return <Download className="w-4 h-4" />;
    if (action.includes("Train")) return <PlusCircle className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
}

export function ChatBubble({
    role,
    content,
    modelCard,
    actions,
    progress,
    footer,
    onViewDetails,
    onTrainNew,
    onDownstreamAction
}: ChatBubbleProps) {
    const isUser = role === 'user'

    return (
        <div className={cn("flex w-full gap-4 p-4", isUser ? "justify-end" : "justify-start")}>
            {!isUser && (
                <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border bg-background shadow-sm">
                    <Bot className="h-4 w-4" />
                </div>
            )}

            <div className={cn(
                "relative max-w-[85%] rounded-lg px-4 py-3 text-sm shadow-sm flex flex-col gap-4 font-sans",
                isUser
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground border border-border"
            )}>
                <div className={cn("prose prose-sm dark:prose-invert max-w-none break-words", isUser ? "text-primary-foreground" : "")}>
                    {/* Render Text Content */}
                    <div className="whitespace-pre-wrap leading-relaxed">
                        {isUser ? content : <ReactMarkdown>{content}</ReactMarkdown>}
                    </div>

                    {/* Render Progress Bar if present */}
                    {progress && (
                        <div className="mt-4 mb-2 bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
                            <ProgressBar
                                status={progress.status}
                                total={progress.total}
                                fetched={progress.fetched}
                                currentAction={progress.current_action}
                            />
                        </div>
                    )}

                    {/* Render Footer Text (Below Progress) */}
                    {footer && !isUser && (
                        <div className="mt-2 text-sm whitespace-pre-wrap leading-relaxed border-t border-gray-100 dark:border-gray-700 pt-2">
                            <ReactMarkdown>{footer}</ReactMarkdown>
                        </div>
                    )}
                </div>

                {/* Render Rich Content: Model Card */}
                {!isUser && modelCard && (
                    <div className="w-[320px] mt-2">
                        <ModelCard
                            model={modelCard}
                            onSelect={() => { }} // No-op for now in chat
                            onViewDetails={(m) => onViewDetails?.(m)}
                        />
                    </div>
                )}

                {/* Render Rich Content: Action Buttons - Grouped with Descriptions */}
                {!isUser && actions && actions.length > 0 && (
                    <div className="flex flex-col gap-4 mt-3 font-sans">
                        {/* Group 1: Primary Actions - Download & Train */}
                        <div className="space-y-2">
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                                If this model meets your requirements, you can download it directly. Otherwise, consider training a custom model tailored to your specific needs.
                            </p>
                            <div className="flex flex-col gap-2">
                                {actions.filter(a => a.includes("Download") || a.includes("Train")).map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => {
                                            if (action.includes("Train") && onTrainNew) {
                                                onTrainNew()
                                            } else if (action.includes("Download") && modelCard?.download_url) {
                                                window.open(modelCard.download_url, '_blank');
                                            }
                                        }}
                                        className="w-full text-left px-3 py-2 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-700/50 rounded-lg hover:bg-violet-100 dark:hover:bg-violet-900/30 transition-all text-sm font-medium text-violet-700 dark:text-violet-300 flex items-center gap-3 group"
                                    >
                                        <span className="p-1 bg-violet-100 dark:bg-violet-800/50 text-violet-600 dark:text-violet-400 rounded-md group-hover:bg-violet-200 dark:group-hover:bg-violet-700/60 transition-colors">
                                            {action.includes("Download") ? <Download className="w-3.5 h-3.5" /> : <PlusCircle className="w-3.5 h-3.5" />}
                                        </span>
                                        {action}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Group 2: Exploration Actions - Evaluate & Ensemble */}
                        <div className="space-y-2">
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                                You can also further validate or explore this model by evaluating its performance on additional cohorts, or by integrating it into an ensemble approach.
                            </p>
                            <div className="flex flex-col gap-2">
                                {actions.filter(a => a.includes("Evaluate") || a.includes("Ensemble")).map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => onDownstreamAction?.(action)}
                                        className="w-full text-left px-3 py-2 bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-700/50 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/30 transition-all text-sm font-medium text-teal-700 dark:text-teal-300 flex items-center gap-3 group"
                                    >
                                        <span className="p-1 bg-teal-100 dark:bg-teal-800/50 text-teal-600 dark:text-teal-400 rounded-md group-hover:bg-teal-200 dark:group-hover:bg-teal-700/60 transition-colors">
                                            {action.includes("Evaluate") ? <Activity className="w-3.5 h-3.5" /> : <Layers className="w-3.5 h-3.5" />}
                                        </span>
                                        {action}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {isUser && (
                <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-primary text-primary-foreground shadow-sm">
                    <User className="h-4 w-4" />
                </div>
            )}
        </div>
    )
}
