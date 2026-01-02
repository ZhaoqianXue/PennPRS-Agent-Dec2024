"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Search, X, Dna, Pill, Activity, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";

// Open Targets search result interface
export interface OpenTargetsResult {
    id: string;
    name: string;
    entity_type: "disease" | "target" | "drug";
    description: string;
    display_label: string;
}

interface OpenTargetsSearchProps {
    entityTypes?: ("disease" | "target" | "drug")[];
    onSelect: (result: OpenTargetsResult) => void;
    placeholder?: string;
    className?: string;
    autoFocus?: boolean;
}

// Entity type icons
const EntityIcon = ({ type }: { type: string }) => {
    switch (type) {
        case "disease":
            return <Activity className="w-4 h-4 text-rose-500" />;
        case "target":
            return <Dna className="w-4 h-4 text-blue-500" />;
        case "drug":
            return <Pill className="w-4 h-4 text-green-500" />;
        default:
            return <Search className="w-4 h-4 text-gray-400" />;
    }
};

// Entity type badge colors
const getEntityBadgeClass = (type: string) => {
    switch (type) {
        case "disease":
            return "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300";
        case "target":
            return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300";
        case "drug":
            return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300";
        default:
            return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300";
    }
};

export default function OpenTargetsSearch({
    entityTypes,
    onSelect,
    placeholder = "Search diseases, genes, or proteins...",
    className = "",
    autoFocus = false,
}: OpenTargetsSearchProps) {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<OpenTargetsResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const [totalResults, setTotalResults] = useState(0);

    const inputRef = useRef<HTMLInputElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const debounceRef = useRef<NodeJS.Timeout | null>(null);

    // Debounced search function
    const performSearch = useCallback(async (searchQuery: string) => {
        if (searchQuery.length < 2) {
            setResults([]);
            setTotalResults(0);
            setIsOpen(false);
            return;
        }

        setIsLoading(true);

        try {
            const endpoint = entityTypes?.length === 1
                ? `/opentargets/search/${entityTypes[0]}`
                : "/opentargets/search";

            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: searchQuery,
                    entity_types: entityTypes,
                    size: 10,
                }),
            });

            if (!response.ok) throw new Error("Search failed");

            const data = await response.json();
            setResults(data.hits || []);
            setTotalResults(data.total || 0);
            setIsOpen(true);
            setSelectedIndex(-1);
        } catch (error) {
            console.error("Open Targets search error:", error);
            setResults([]);
            setTotalResults(0);
        } finally {
            setIsLoading(false);
        }
    }, [entityTypes]);

    // Handle input change with debounce
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setQuery(value);

        // Clear existing debounce
        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        // Set new debounce (300ms)
        debounceRef.current = setTimeout(() => {
            performSearch(value);
        }, 300);
    };

    // Handle result selection
    const handleSelect = (result: OpenTargetsResult) => {
        setQuery(result.name);
        setIsOpen(false);
        onSelect(result);
    };

    // Handle keyboard navigation
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (!isOpen || results.length === 0) return;

        switch (e.key) {
            case "ArrowDown":
                e.preventDefault();
                setSelectedIndex((prev) =>
                    prev < results.length - 1 ? prev + 1 : prev
                );
                break;
            case "ArrowUp":
                e.preventDefault();
                setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
                break;
            case "Enter":
                e.preventDefault();
                if (selectedIndex >= 0 && results[selectedIndex]) {
                    handleSelect(results[selectedIndex]);
                }
                break;
            case "Escape":
                setIsOpen(false);
                setSelectedIndex(-1);
                break;
        }
    };

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(e.target as Node) &&
                inputRef.current &&
                !inputRef.current.contains(e.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Cleanup debounce on unmount
    useEffect(() => {
        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current);
            }
        };
    }, []);

    // Clear search
    const clearSearch = () => {
        setQuery("");
        setResults([]);
        setIsOpen(false);
        inputRef.current?.focus();
    };

    return (
        <div className={`relative w-full ${className}`}>
            {/* Search Input */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    onFocus={() => query.length >= 2 && setIsOpen(true)}
                    placeholder={placeholder}
                    autoFocus={autoFocus}
                    className="pl-10 pr-10 h-12 text-base border-2 border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-blue-400 rounded-lg"
                />
                {isLoading && (
                    <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-blue-500 animate-spin" />
                )}
                {!isLoading && query && (
                    <button
                        onClick={clearSearch}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            {/* Dropdown Results */}
            {isOpen && results.length > 0 && (
                <div
                    ref={dropdownRef}
                    className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl max-h-80 overflow-y-auto"
                >
                    {/* Results Header */}
                    <div className="px-3 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                        {totalResults.toLocaleString()} results found
                    </div>

                    {/* Results List */}
                    {results.map((result, index) => (
                        <button
                            key={result.id}
                            onClick={() => handleSelect(result)}
                            onMouseEnter={() => setSelectedIndex(index)}
                            className={`w-full px-3 py-3 text-left flex items-start gap-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${index === selectedIndex ? "bg-blue-50 dark:bg-blue-900/20" : ""
                                } ${index !== results.length - 1 ? "border-b border-gray-100 dark:border-gray-800" : ""}`}
                        >
                            {/* Entity Icon */}
                            <div className="mt-0.5">
                                <EntityIcon type={result.entity_type} />
                            </div>

                            {/* Result Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="font-medium text-gray-900 dark:text-white truncate">
                                        {result.name}
                                    </span>
                                    <span className={`px-1.5 py-0.5 text-xs font-medium rounded ${getEntityBadgeClass(result.entity_type)}`}>
                                        {result.entity_type}
                                    </span>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 font-mono">
                                    {result.id}
                                </div>
                                {result.description && (
                                    <div className="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                                        {result.description}
                                    </div>
                                )}
                            </div>
                        </button>
                    ))}

                    {/* "Powered by" Footer */}
                    <div className="px-3 py-2 text-xs text-center text-gray-400 dark:text-gray-500 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                        Powered by <span className="font-medium">Open Targets Platform</span>
                    </div>
                </div>
            )}

            {/* No Results Message */}
            {isOpen && query.length >= 2 && results.length === 0 && !isLoading && (
                <div
                    ref={dropdownRef}
                    className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl p-4 text-center"
                >
                    <Search className="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-500 dark:text-gray-400">
                        No results found for &quot;{query}&quot;
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                        Try a different search term
                    </p>
                </div>
            )}
        </div>
    );
}
