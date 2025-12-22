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
    switch (action) {
        case "Evaluate on Cohort": return <Activity className="w-4 h-4" />;
        case "Build Ensemble Model": return <Layers className="w-4 h-4" />;
        case "Integrate Proteomics Data": return <Dna className="w-4 h-4" />;
        case "Download Model": return <Download className="w-4 h-4" />;
        case "Train Custom Model": return <PlusCircle className="w-4 h-4" />;
        default: return <Activity className="w-4 h-4" />;
    }
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
                "relative max-w-[85%] rounded-lg px-4 py-3 text-sm shadow-sm flex flex-col gap-4",
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
                    <div className="w-full max-w-sm mt-2">
                        <ModelCard
                            model={modelCard}
                            onSelect={() => { }} // No-op for now in chat
                            onViewDetails={(m) => onViewDetails?.(m)}
                            compact={true}
                        />
                    </div>
                )}

                {/* Render Rich Content: Action Buttons */}
                {!isUser && actions && actions.length > 0 && (
                    <div className="flex flex-col gap-2 mt-2">
                        {actions.map((action, idx) => (
                            <button
                                key={idx}
                                onClick={() => {
                                    if (action === "Train Custom Model" && onTrainNew) {
                                        onTrainNew()
                                    } else if (action === "Download Model" && modelCard?.download_url) {
                                        window.open(modelCard.download_url, '_blank');
                                    } else if (onDownstreamAction) {
                                        onDownstreamAction(action)
                                    }
                                }}
                                className="w-full text-left px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all shadow-sm hover:shadow text-sm font-medium text-gray-700 dark:text-gray-200 flex items-center gap-3 group"
                            >
                                <span className="p-1.5 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-md group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                                    {getActionIcon(action)}
                                </span>
                                {action}
                            </button>
                        ))}
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
