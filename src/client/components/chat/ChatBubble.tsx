import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'
import { Bot, User, Activity, Layers, Dna, Download, PlusCircle, Bookmark, CheckCircle2, Loader2 } from 'lucide-react'
import ModelCard, { ModelData } from "../ModelCard"
import { ProgressBar } from "../ProgressBar"

interface ChatBubbleProps {
    role: 'user' | 'agent'
    content: string
    modelCard?: ModelData
    customCard?: React.ReactNode
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
    onModelDownload?: (model: ModelData, event?: React.MouseEvent) => void
    onModelSave?: (model: ModelData, event?: React.MouseEvent) => void
    isModelSaved?: boolean;
    isLoading?: boolean;
}

const getActionIcon = (action: string) => {
    if (action.includes("Evaluate")) return <Activity className="w-4 h-4" />;
    if (action.includes("Ensemble")) return <Layers className="w-4 h-4" />;
    if (action.includes("Proteomics")) return <Dna className="w-4 h-4" />;
    if (action.includes("Download")) return <Download className="w-4 h-4" />;
    if (action.includes("Save")) return <Bookmark className="w-4 h-4" />;
    if (action.includes("Train")) return <PlusCircle className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
}

export function ChatBubble({
    role,
    content,
    modelCard,
    customCard,
    actions,
    progress,
    footer,
    onViewDetails,
    onTrainNew,
    onDownstreamAction,
    onModelDownload,
    onModelSave,
    isModelSaved,
    isLoading
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
                    <div className="whitespace-pre-wrap leading-relaxed flex flex-col gap-2">
                        {isUser ? content : (
                            <div className="flex flex-col gap-2">
                                {isLoading && (
                                    <div className="flex items-center gap-2 text-blue-500 font-medium animate-pulse mb-1">
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        <span>Searching and analyzing...</span>
                                    </div>
                                )}
                                <ReactMarkdown>{content}</ReactMarkdown>
                            </div>
                        )}
                    </div>

                    {/* Render Footer Text (Below Progress) */}
                    {footer && !isUser && (
                        <div className="mt-2 text-sm whitespace-pre-wrap leading-relaxed border-t border-gray-100 dark:border-gray-700 pt-2">
                            <ReactMarkdown>{footer}</ReactMarkdown>
                        </div>
                    )}
                </div>

                {/* Render Rich Content: Custom Card or Model Card */}
                {!isUser && (customCard || modelCard) && (
                    <div className="w-[320px] mt-2">
                        {customCard || (
                            <ModelCard
                                model={modelCard!}
                                onSelect={() => { }} // No-op for now in chat
                                onViewDetails={(m) => onViewDetails?.(m)}
                            />
                        )}
                    </div>
                )}

                {/* Render Rich Content: Action Buttons - Download/Save (Teal) & Train (Purple) */}
                {!isUser && actions && actions.length > 0 && (
                    <div className="flex flex-col gap-4 mt-3 font-sans">
                        {/* Group 1: Download & Save Actions - Teal Theme */}
                        {actions.some(a => a.includes("Download")) && (
                            <div className="space-y-2">
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                    Download this model to use it, or save it for later access. Both options will bookmark the model for easy retrieval.
                                </p>
                                <div className="flex flex-col gap-2">
                                    {/* Download Button */}
                                    <button
                                        onClick={(e) => {
                                            if (onModelDownload && modelCard) {
                                                onModelDownload(modelCard, e);
                                            } else if (modelCard?.download_url) {
                                                window.open(modelCard.download_url, '_blank');
                                            }
                                        }}
                                        className="w-full text-left px-3 py-2 bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-700/50 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/30 transition-all text-sm font-medium text-teal-700 dark:text-teal-300 flex items-center gap-3 group"
                                    >
                                        <span className="p-1 bg-teal-100 dark:bg-teal-800/50 text-teal-600 dark:text-teal-400 rounded-md group-hover:bg-teal-200 dark:group-hover:bg-teal-700/60 transition-colors">
                                            <Download className="w-3.5 h-3.5" />
                                        </span>
                                        Download this Model
                                    </button>
                                    {/* Save Button */}
                                    <button
                                        onClick={(e) => {
                                            if (onModelSave && modelCard) {
                                                onModelSave(modelCard, e);
                                            }
                                        }}
                                        disabled={isModelSaved}
                                        className={`w-full text-left px-3 py-2 rounded-lg transition-all text-sm font-medium flex items-center gap-3 group ${isModelSaved
                                            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700/50 text-green-700 dark:text-green-300 cursor-default'
                                            : 'bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-700/50 hover:bg-teal-100 dark:hover:bg-teal-900/30 text-teal-700 dark:text-teal-300'
                                            }`}
                                    >
                                        <span className={`p-1 rounded-md transition-colors ${isModelSaved
                                            ? 'bg-green-100 dark:bg-green-800/50 text-green-600 dark:text-green-400'
                                            : 'bg-teal-100 dark:bg-teal-800/50 text-teal-600 dark:text-teal-400 group-hover:bg-teal-200 dark:group-hover:bg-teal-700/60'
                                            }`}>
                                            {isModelSaved ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Bookmark className="w-3.5 h-3.5" />}
                                        </span>
                                        {isModelSaved ? 'Model Saved' : 'Save this Model'}
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Group 2: Train Custom - Purple Theme */}
                        {actions.some(a => a.includes("Train")) && (
                            <div className="space-y-2">
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                    Want a model tailored to your specific needs? Train a custom model with your own data.
                                </p>
                                <button
                                    onClick={() => onTrainNew?.()}
                                    className="w-full text-left px-3 py-2 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-700/50 rounded-lg hover:bg-violet-100 dark:hover:bg-violet-900/30 transition-all text-sm font-medium text-violet-700 dark:text-violet-300 flex items-center gap-3 group"
                                >
                                    <span className="p-1 bg-violet-100 dark:bg-violet-800/50 text-violet-600 dark:text-violet-400 rounded-md group-hover:bg-violet-200 dark:group-hover:bg-violet-700/60 transition-colors">
                                        <PlusCircle className="w-3.5 h-3.5" />
                                    </span>
                                    Train a Custom Model
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {
                isUser && (
                    <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-primary text-primary-foreground shadow-sm">
                        <User className="h-4 w-4" />
                    </div>
                )
            }
        </div >
    )
}
