"use client";

import { useState, useRef, useEffect } from "react"
import { ProgressBar } from "./ProgressBar";

import { SendHorizontal, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChatBubble } from "@/components/chat/ChatBubble"
import { AnimatePresence, motion } from "framer-motion"
import { ModelData } from "./ModelCard"

export interface StructuredResponse {
    type: 'model_grid' | 'downstream_options' | 'model_update' | 'protein_grid' | 'protein_detail';
    models?: ModelData[];
    downstream?: {
        modelId: string;
        trait: string;
        options: string[];
    };
    model_update?: { model_id: string; updates: Partial<ModelData> };
    // Rich content fields (mirrored from backend)
    best_model?: ModelData;
    actions?: string[];
    // Protein-specific fields
    search_query?: string;
    platform?: string;
}

interface Message {
    role: 'user' | 'agent'
    content: string
    id: string
    modelCard?: ModelData
    actions?: string[]
    // Progress Tracking
    isProgress?: boolean
    progressData?: { status: string; total: number; fetched: number; current_action: string } | null
    footer?: string // Footer text below progress
    isWaitingForAncestry?: boolean
}

interface ChatInterfaceProps {
    initialMessage?: string;
    onResponse?: (response: StructuredResponse) => void;
    currentTrait?: string | null;
    externalTrigger?: string | null;
    // Handlers for rich actions
    onViewDetails?: (model: ModelData) => void;
    onTrainNew?: () => void;
    onDownstreamAction?: (action: string) => void;
    onModelDownload?: (model: ModelData, event?: React.MouseEvent) => void;
    onModelSave?: (model: ModelData, event?: React.MouseEvent) => void;
    // New concurrent search props
    onProgressUpdate?: (progress: { status: string; total: number; fetched: number; current_action: string } | null) => void;
    onSearchStatusChange?: (isSearching: boolean) => void;
    // Smart features
    deferAnalysis?: boolean;
    externalAgentMessage?: string | null;
    externalAgentModel?: ModelData | null;
    externalAgentActions?: string[] | null;
    // Context
    hasSelectedAncestry?: boolean;
    // For checking if model is already saved
    savedModelIds?: string[];
}

export default function ChatInterface(props: ChatInterfaceProps) {
    const {
        initialMessage,
        onResponse,
        currentTrait,
        externalTrigger,
        onViewDetails,
        onTrainNew,
        onDownstreamAction,
        onModelDownload,
        onModelSave,
        onProgressUpdate,
        onSearchStatusChange,
        hasSelectedAncestry,
        savedModelIds
    } = props;
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "agent",
            content: "Welcome to PennPRS Lab! I'm your research assistant — here to help you navigate and leverage this platform. I can answer questions, design research workflows, and analyze results. Let me know what you need help with! To begin, you can type in the chat box or select a disease of interest from the side panel, and I'll recommend the most suitable PRS models for you."
        }
    ])
    const [input, setInput] = useState("")

    const [loading, setLoading] = useState(false)
    const [searchProgress, setSearchProgress] = useState<{ status: string; total: number; fetched: number; current_action: string } | null>(null);
    const [showSuggestions, setShowSuggestions] = useState(false)
    const scrollRef = useRef<HTMLDivElement>(null)
    const initialized = useRef(false);

    // Track the current progress message ID to inject live updates
    const currentProgressMsgId = useRef<string | null>(null);

    // REF to track latest progress for async access in handleSend
    const searchProgressRef = useRef<{ status: string; total: number; fetched: number; current_action: string } | null>(null);

    // Update messages when ancestry is submitted
    useEffect(() => {
        if (props.hasSelectedAncestry) {
            setMessages(prev => prev.map(m =>
                m.isWaitingForAncestry ? { ...m, isWaitingForAncestry: false } : m
            ));
        }
    }, [props.hasSelectedAncestry]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [messages, searchProgress]) // Scroll on progress update too

    // Handle external triggers (e.g. from Canvas "Select" or "Train" actions)
    useEffect(() => {
        if (externalTrigger) {
            handleSend(externalTrigger);
        }
    }, [externalTrigger])

    const handleSend = async (text: string = input) => {
        if (!text.trim() || loading) return

        const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text }

        // Create Progress Message immediately
        const progressId = `prog-${Date.now()}`;
        const progressMsg: Message = {
            id: progressId,
            role: 'agent',
            content: "Initializing search...",
            isProgress: true,
            progressData: null,
            isWaitingForAncestry: !props.hasSelectedAncestry
        };
        currentProgressMsgId.current = progressId;

        setMessages(prev => [...prev, userMsg, progressMsg])
        setInput("")
        setLoading(true)
        onSearchStatusChange?.(true);
        setSearchProgress(null);
        searchProgressRef.current = null; // Reset Ref
        onProgressUpdate?.(null);

        // Generate Request ID
        const requestId = crypto.randomUUID();

        // Start Polling
        const pollInterval = setInterval(async () => {
            try {
                const pRes = await fetch(`http://localhost:8000/agent/search_progress/${requestId}`);
                if (pRes.ok) {
                    const progress = await pRes.json();
                    if (progress.status !== 'unknown') {
                        setSearchProgress(progress);
                        searchProgressRef.current = progress; // Update Ref
                        onProgressUpdate?.(progress);
                    }
                }
            } catch (e) {
                // ignore polling errors
            }
        }, 500);

        try {
            const res = await fetch("http://localhost:8000/agent/invoke", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMsg.content, request_id: requestId })
            })

            // Stop polling
            clearInterval(pollInterval);

            if (!res.ok) throw new Error("API Error")

            const data = await res.json()

            // Extract Structured Data
            const sr = data.full_state?.structured_response;

            // CORRECT TOTAL Calculation from Response (Priority: Response > Ref > State)
            let finalCount = 0;
            const progressSnapshot = searchProgressRef.current as { status: string; total: number; fetched: number; current_action: string } | null;
            if (sr && sr.type === 'model_grid' && sr.models) {
                finalCount = sr.models.length;
            } else if (progressSnapshot && progressSnapshot.total) {
                finalCount = progressSnapshot.total;
            }

            // Final Progress State (Done - 100% Full)
            const finalProgress = {
                status: 'completed',
                total: finalCount,
                fetched: finalCount,
                current_action: 'Search Complete'
            };
            setSearchProgress(finalProgress);

            if (sr && onResponse) {
                // ... (handling callbacks unchanged)
                if (sr.type === 'model_grid') {
                    onResponse({
                        type: 'model_grid',
                        models: sr.models,
                        best_model: sr.best_model,
                        actions: sr.actions
                    });
                } else if (sr.type === 'downstream_options') {
                    onResponse({
                        type: 'downstream_options',
                        downstream: { modelId: sr.model_id, trait: sr.trait, options: sr.options }
                    });
                } else if (sr.type === 'model_update') {
                    onResponse({
                        type: 'model_update',
                        model_update: { model_id: sr.model_id, updates: sr.updates }
                    });
                }
            }

            // Determine deferral
            const isModelGrid = sr && sr.type === 'model_grid';
            const shouldDefer = isModelGrid && props.deferAnalysis;

            // Update the Progress Message to Final State
            setMessages(prev => prev.map(m => {
                if (m.id === progressId) {
                    // 1. Top Text
                    let finalContent = "Search completed successfully.";

                    // 2. Bottom Text (Footer)
                    let footerContent = `Found **${finalCount}** models.`;

                    return {
                        ...m,
                        content: finalContent,
                        footer: footerContent, // New Footer
                        progressData: finalProgress, // Bake in final progress (Full)
                        isProgress: true
                    };
                }
                return m;
            }));

            // If NOT deferred, append the agent Analysis message
            if (!shouldDefer) {
                const agentMsg: Message = {
                    id: (Date.now() + 1).toString(),
                    role: 'agent',
                    content: data.response || "Sorry, I didn't get a response.",
                    modelCard: sr?.best_model,
                    actions: sr?.actions
                }
                setMessages(prev => [...prev, agentMsg])
            }

        } catch (error) {
            clearInterval(pollInterval);
            setSearchProgress(null);
            console.error(error)

            // Update progress message to error
            setMessages(prev => prev.map(m => {
                if (m.id === progressId) return { ...m, content: "Search failed. Please try again." };
                return m;
            }));

        } finally {
            setLoading(false)
            currentProgressMsgId.current = null; // Detach live updates
            onSearchStatusChange?.(false);
        }
    }

    // Auto-send initial message
    useEffect(() => {
        if (initialMessage && !initialized.current) {
            initialized.current = true;
            handleSend(initialMessage);
        }
    }, [initialMessage]);

    // Handle External Agent Messages (Smart Recommendations)
    useEffect(() => {
        if (props.externalAgentMessage) {
            const agentMsg: Message = {
                id: `ext-${Date.now()}`,
                role: 'agent',
                content: props.externalAgentMessage,
                modelCard: props.externalAgentModel ?? undefined,
                actions: props.externalAgentActions || ["View Details", "Use this Model", "Train Custom Model"]
            };
            setMessages(prev => [...prev, agentMsg]);
        }
    }, [props.externalAgentMessage, props.externalAgentModel, props.externalAgentActions]);

    return (
        <div className="flex flex-col h-full relative bg-white dark:bg-gray-900">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 scroll-smooth" ref={scrollRef}>
                <div className="space-y-6">
                    <AnimatePresence initial={false}>
                        {messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <ChatBubble
                                    role={msg.role}
                                    content={msg.isWaitingForAncestry ? "Action Required: Please select your target ancestry from the panel on the left to specific model recommendations." : msg.content}
                                    modelCard={msg.modelCard}
                                    actions={msg.actions}
                                    // Inject live progress if this is the active progress message
                                    progress={msg.isWaitingForAncestry ? null : (msg.id === currentProgressMsgId.current ? searchProgress : msg.progressData)}
                                    footer={msg.isWaitingForAncestry ? undefined : msg.footer}
                                    onViewDetails={onViewDetails}
                                    onTrainNew={onTrainNew}
                                    onDownstreamAction={onDownstreamAction}
                                    onModelDownload={onModelDownload}
                                    onModelSave={onModelSave}
                                    isModelSaved={msg.modelCard ? savedModelIds?.includes(msg.modelCard.id) : false}
                                />
                            </motion.div>
                        ))}
                    </AnimatePresence>
                    {/* Floating loader removed - fully integrated into bubbles */}
                </div>
            </div>


            {/* Input Area */}
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
                                {["I want to search for models for Alzheimer's disease", "I want to search for models for Type 2 Diabetes", "I want to search for models for Breast Cancer", "I want to search for models for Coronary Artery Disease"].map((suggestion, idx) => (
                                    <button
                                        key={idx}
                                        className="w-full text-left px-4 py-3 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 text-gray-700 dark:text-gray-200"
                                        onMouseDown={(e) => {
                                            e.preventDefault(); // Prevent blur
                                            setInput(suggestion);
                                            setShowSuggestions(false);
                                            // Optional: immediately focus back or keep focus? Input keeps focus if we prevent default on mousedown?
                                            // Actually prompt says "automatically jump out recommended options".
                                            // Clicking one usually fills it.
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
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        onFocus={() => setShowSuggestions(true)}
                        onBlur={() => setShowSuggestions(false)}
                        disabled={loading}
                        className="flex-1"
                    />
                    <Button onClick={() => handleSend()} disabled={loading || !input.trim()}>
                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
                    </Button>
                </div>
                <div className="text-center text-xs text-muted-foreground mt-2">
                    PennPRS Lab &copy; 2025
                </div>
            </div>
        </div >
    )
}
