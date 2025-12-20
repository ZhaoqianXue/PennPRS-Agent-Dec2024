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
    type: 'model_grid' | 'downstream_options' | 'model_update';
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
}

interface Message {
    role: 'user' | 'agent'
    content: string
    id: string
    modelCard?: ModelData
    actions?: string[]
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
}

export default function ChatInterface({ initialMessage, onResponse, currentTrait, externalTrigger, onViewDetails, onTrainNew, onDownstreamAction }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "agent",
            content: "Welcome to PennPRS! I'm PennPRS Agent — here to help you navigate and use this platform. I can answer questions, design research workflows, and analyze results. Let me know what you need help with! First, you can type in the chat box or select a disease of interest from the side panel, and I can recommend the corresponding PRS Model for you!"
        }
    ])
    const [input, setInput] = useState("")

    const [loading, setLoading] = useState(false)
    const [searchProgress, setSearchProgress] = useState<{ status: string; total: number; fetched: number; current_action: string } | null>(null);
    const [showSuggestions, setShowSuggestions] = useState(false)
    const scrollRef = useRef<HTMLDivElement>(null)
    const initialized = useRef(false);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [messages])

    // Handle external triggers (e.g. from Canvas "Select" or "Train" actions)
    useEffect(() => {
        if (externalTrigger) {
            handleSend(externalTrigger);
        }
    }, [externalTrigger])

    const handleSend = async (text: string = input) => {
        if (!text.trim() || loading) return

        const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text }
        setMessages(prev => [...prev, userMsg])
        setInput("")
        setLoading(true)
        setSearchProgress(null); // Reset progress

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

            // Stop polling immediately on response
            clearInterval(pollInterval);
            setSearchProgress(null);

            if (!res.ok) throw new Error("API Error")

            const data = await res.json()

            // Extract Structured Data
            const sr = data.full_state?.structured_response;
            if (sr && onResponse) {
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
                        downstream: {
                            modelId: sr.model_id,
                            trait: sr.trait,
                            options: sr.options
                        }
                    });
                } else if (sr.type === 'model_update') {
                    onResponse({
                        type: 'model_update',
                        model_update: {
                            model_id: sr.model_id,
                            updates: sr.updates
                        }
                    });
                }
            }

            const agentMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'agent',
                content: data.response || "Sorry, I didn't get a response.",
                modelCard: sr?.best_model,
                actions: sr?.actions
            }
            setMessages(prev => [...prev, agentMsg])

        } catch (error) {
            clearInterval(pollInterval);
            setSearchProgress(null);
            console.error(error)
            // ... (error handling)
        } finally {
            setLoading(false)
        }
    }

    // Auto-send initial message
    useEffect(() => {
        if (initialMessage && !initialized.current) {
            initialized.current = true;
            handleSend(initialMessage);
        }
    }, [initialMessage]);

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
                                    content={msg.content}
                                    modelCard={msg.modelCard}
                                    actions={msg.actions}
                                    onViewDetails={onViewDetails}
                                    onTrainNew={onTrainNew}
                                    onDownstreamAction={onDownstreamAction}
                                />
                            </motion.div>
                        ))}
                    </AnimatePresence>
                    {loading && (
                        <div className="ml-12 mb-4">
                            {searchProgress ? (
                                <ProgressBar
                                    status={searchProgress.status}
                                    total={searchProgress.total}
                                    fetched={searchProgress.fetched}
                                    currentAction={searchProgress.current_action}
                                />
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex items-center gap-2 text-muted-foreground text-sm p-4"
                                >
                                    <Loader2 className="h-4 w-4 animate-spin" /> Thinking and Searching...
                                </motion.div>
                            )}
                        </div>
                    )}
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
                    PennPRS Agent &copy; 2025
                </div>
            </div>
        </div >
    )
}
