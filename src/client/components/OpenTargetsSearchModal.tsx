import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Search, X, Activity, Dna, Pill, FileText, CornerDownLeft } from 'lucide-react';

// Open Targets result interface
interface OpenTargetsResult {
    id: string;
    name: string;
    entity_type: string;
    description: string;
    score: number;
    highlights: string[];
    display_label: string;
    study_type?: string;
    n_samples?: number;
    n_cases?: number;
}

// Grouped search response
interface GroupedSearchResponse {
    total: number;
    topHit: OpenTargetsResult | null;
    targets: OpenTargetsResult[];
    diseases: OpenTargetsResult[];
    drugs: OpenTargetsResult[];
    studies: OpenTargetsResult[];
    variants: OpenTargetsResult[];
}

// Entity filter type
type EntityFilter = 'all' | 'target' | 'variant' | 'study' | 'disease' | 'drug';

// Entity Icons - matching Open Targets exactly
const EntityIcons: Record<string, React.ReactNode> = {
    target: <span className="text-xs font-bold">⊠</span>,
    variant: <span className="text-xs font-bold">⬡</span>,
    study: <span className="text-xs font-bold">☰</span>,
    disease: <span className="text-xs font-bold">⚕</span>,
    drug: <span className="text-xs font-bold">⊞</span>,
};

// Search suggestions - matching Open Targets
const SEARCH_SUGGESTIONS = [
    { id: 'PCSK9', name: 'PCSK9', type: 'target' },
    { id: 'APOB', name: 'APOB', type: 'target' },
    { id: 'Rheumatoid arthritis', name: 'Rheumatoid arthritis', type: 'disease' },
    { id: 'Hypercholesterolemia', name: 'Hypercholesterolemia', type: 'disease' },
    { id: 'IVACAFTOR', name: 'IVACAFTOR', type: 'drug' },
    { id: 'METFORMIN', name: 'METFORMIN', type: 'drug' },
    { id: '19_44908822_C_T', name: '19_44908822_C_T', type: 'variant' },
    { id: '4_1804392_G_A', name: '4_1804392_G_A', type: 'variant' },
    { id: 'GCST004131', name: 'GCST004131', type: 'study' },
    { id: 'GCST90239655', name: 'GCST90239655', type: 'study' },
];

interface OpenTargetsSearchModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (query: string, result?: OpenTargetsResult) => void;
}

export default function OpenTargetsSearchModal({ isOpen, onClose, onSelect }: OpenTargetsSearchModalProps) {
    const [searchInput, setSearchInput] = useState('');
    const [activeFilter, setActiveFilter] = useState<EntityFilter>('all');
    const [groupedResults, setGroupedResults] = useState<GroupedSearchResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [recentSearches, setRecentSearches] = useState<string[]>([]);

    const inputRef = useRef<HTMLInputElement>(null);
    const debounceRef = useRef<NodeJS.Timeout | null>(null);
    const resultsCache = useRef<Record<string, GroupedSearchResponse>>({});

    // Load recent searches from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('openTargetsRecentSearches');
        if (saved) {
            try {
                setRecentSearches(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to parse recent searches');
            }
        }
    }, []);

    // Focus input when modal opens
    useEffect(() => {
        if (isOpen && inputRef.current) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    // Handle ESC key
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    // Debounced search
    const performSearch = useCallback(async (query: string) => {
        if (query.length < 2) {
            setGroupedResults(null);
            return;
        }

        // Check cache
        if (resultsCache.current[query]) {
            setGroupedResults(resultsCache.current[query]);
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/opentargets/grouped_search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, size: 25 }),
            });
            if (!response.ok) throw new Error('Search failed');
            const data: GroupedSearchResponse = await response.json();

            // Store in cache
            resultsCache.current[query] = data;
            setGroupedResults(data);
        } catch (error) {
            console.error('Search error:', error);
            setGroupedResults(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Handle input change
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearchInput(value);

        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => performSearch(value), 300);
    };

    // Save to recent searches
    const saveRecentSearch = (query: string) => {
        const updated = [query, ...recentSearches.filter(s => s !== query)].slice(0, 7);
        setRecentSearches(updated);
        localStorage.setItem('openTargetsRecentSearches', JSON.stringify(updated));
    };

    // Handle selection
    const handleSelect = (query: string, result?: OpenTargetsResult) => {
        saveRecentSearch(query);
        onSelect(query, result);
        onClose();
    };

    // Remove recent search
    const removeRecentSearch = (search: string, e: React.MouseEvent) => {
        e.stopPropagation();
        const updated = recentSearches.filter(s => s !== search);
        setRecentSearches(updated);
        localStorage.setItem('openTargetsRecentSearches', JSON.stringify(updated));
    };

    // Clear all recent searches
    const clearAllRecent = () => {
        setRecentSearches([]);
        localStorage.removeItem('openTargetsRecentSearches');
    };

    // Filter buttons
    const filterButtons: { key: EntityFilter; label: string; icon?: React.ReactNode }[] = [
        { key: 'all', label: 'All' },
        { key: 'target', label: 'Target', icon: EntityIcons.target },
        { key: 'variant', label: 'Variant', icon: EntityIcons.variant },
        { key: 'study', label: 'Study', icon: EntityIcons.study },
        { key: 'disease', label: 'Disease', icon: EntityIcons.disease },
        { key: 'drug', label: 'Drug', icon: EntityIcons.drug },
    ];

    if (!isOpen) return null;

    const hasQuery = searchInput.length >= 2;
    const hasResults = groupedResults && (
        groupedResults.topHit ||
        groupedResults.targets.length > 0 ||
        groupedResults.diseases.length > 0 ||
        groupedResults.drugs.length > 0 ||
        groupedResults.studies.length > 0 ||
        (groupedResults.variants && groupedResults.variants.length > 0)
    );

    return (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-start justify-center pt-[10vh]">
            {/* Modal Container */}
            <div className="w-full max-w-2xl bg-white dark:bg-gray-900 rounded-lg shadow-2xl overflow-hidden max-h-[80vh] flex flex-col">

                {/* Search Input Header */}
                <div className="px-4 pt-4 pb-3 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3">
                        <Search className="w-5 h-5 text-gray-400" />
                        <input
                            ref={inputRef}
                            type="text"
                            value={searchInput}
                            onChange={handleInputChange}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && searchInput.trim()) {
                                    handleSelect(searchInput.trim());
                                }
                            }}
                            placeholder="Search for a target, drug, disease, or phenotype..."
                            className="flex-1 text-base bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-500"
                            autoFocus
                        />
                        <button
                            onClick={onClose}
                            className="px-2 py-1 text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700"
                        >
                            esc
                        </button>
                    </div>

                    {/* Filter Pills */}
                    <div className="flex items-center gap-2 mt-4">
                        {filterButtons.map((btn) => (
                            <button
                                key={btn.key}
                                onClick={() => setActiveFilter(btn.key)}
                                className={`px-3 py-1.5 text-sm rounded-full border transition-colors flex items-center gap-1.5 ${activeFilter === btn.key
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400'
                                    }`}
                            >
                                {btn.icon}
                                {btn.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Scrollable Content Area */}
                <div className="flex-1 overflow-y-auto">

                    {/* Search For Row - when typing */}
                    {searchInput.trim() && (
                        <button
                            onClick={() => handleSelect(searchInput.trim())}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 border-b border-gray-100 dark:border-gray-800"
                        >
                            <span className="text-gray-700 dark:text-gray-300">
                                Search for: <span className="font-medium text-gray-900 dark:text-white">{searchInput}</span>
                            </span>
                            <CornerDownLeft className="w-4 h-4 text-gray-400" />
                        </button>
                    )}

                    {/* Loading State */}
                    {isLoading && (
                        <div className="py-8 text-center text-gray-500">
                            <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                        </div>
                    )}

                    {/* Results Display */}
                    {hasQuery && hasResults && groupedResults && !isLoading && (
                        <div className="divide-y divide-gray-100 dark:divide-gray-800">

                            {/* TOP HIT */}
                            {groupedResults.topHit && (
                                <div>
                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                                        <span className="text-amber-500">★</span> TOPHIT
                                    </div>
                                    <button
                                        onClick={() => handleSelect(groupedResults.topHit!.name, groupedResults.topHit!)}
                                        className="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800"
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="font-medium text-blue-600 dark:text-blue-400">
                                                {groupedResults.topHit.name}
                                            </span>
                                            <span className="text-xs text-gray-400 font-mono">
                                                {groupedResults.topHit.id}
                                            </span>
                                        </div>
                                        {groupedResults.topHit.description && (
                                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                                                {groupedResults.topHit.description}
                                            </p>
                                        )}
                                    </button>
                                </div>
                            )}

                            {/* TARGETS */}
                            {groupedResults.targets.length > 0 && (
                                <div>
                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                                        {EntityIcons.target} TARGETS
                                    </div>
                                    {groupedResults.targets.map((result) => (
                                        <button
                                            key={result.id}
                                            onClick={() => handleSelect(result.name, result)}
                                            className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between"
                                        >
                                            <div>
                                                <span className="font-medium text-gray-900 dark:text-white">
                                                    {result.name}
                                                </span>
                                                {result.description && (
                                                    <span className="text-gray-500 dark:text-gray-400 ml-1">
                                                        - {result.description}
                                                    </span>
                                                )}
                                            </div>
                                            <span className="text-xs text-gray-400 font-mono">
                                                {result.id}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* DISEASES */}
                            {groupedResults.diseases.length > 0 && (
                                <div>
                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                                        {EntityIcons.disease} DISEASES
                                    </div>
                                    {groupedResults.diseases.map((result) => (
                                        <button
                                            key={result.id}
                                            onClick={() => handleSelect(result.name, result)}
                                            className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between"
                                        >
                                            <span className="text-gray-900 dark:text-white">
                                                {result.name}
                                            </span>
                                            <span className="text-xs text-gray-400 font-mono">
                                                {result.id}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* GWAS STUDIES */}
                            {groupedResults.studies.length > 0 && (
                                <div>
                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                                        {EntityIcons.study} GWAS STUDIES
                                        <span className="px-1.5 py-0.5 text-[10px] bg-blue-500 text-white rounded font-bold">NEW</span>
                                    </div>
                                    {groupedResults.studies.map((result) => (
                                        <button
                                            key={result.id}
                                            onClick={() => handleSelect(result.name, result)}
                                            className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800"
                                        >
                                            <div className="flex items-center justify-between">
                                                <span className="text-gray-900 dark:text-white">
                                                    {result.name}
                                                </span>
                                                <span className="text-xs text-gray-400 font-mono">
                                                    {result.id}
                                                </span>
                                            </div>
                                            {(result.study_type || result.n_samples) && (
                                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                                    Study type: {result.study_type?.toUpperCase() || 'GWAS'}
                                                    {result.n_samples && ` • Sample size: ${result.n_samples.toLocaleString()}`}
                                                </p>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* VARIANTS */}
                            {groupedResults.variants && groupedResults.variants.length > 0 && (
                                <div>
                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                                        {EntityIcons.variant} VARIANTS
                                    </div>
                                    {groupedResults.variants.map((result) => (
                                        <button
                                            key={result.id}
                                            onClick={() => handleSelect(result.name, result)}
                                            className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between"
                                        >
                                            <span className="text-gray-900 dark:text-white">
                                                {result.name}
                                            </span>
                                            <span className="text-xs text-gray-400 font-mono">
                                                {result.id}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* DRUGS */}
                            {groupedResults.drugs.length > 0 && (
                                <div>
                                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                                        {EntityIcons.drug} DRUGS
                                    </div>
                                    {groupedResults.drugs.map((result) => (
                                        <button
                                            key={result.id}
                                            onClick={() => handleSelect(result.name, result)}
                                            className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between"
                                        >
                                            <span className="text-gray-900 dark:text-white">
                                                {result.name}
                                            </span>
                                            <span className="text-xs text-gray-400 font-mono">
                                                {result.id}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Initial State - Recent + Suggestions */}
                    {!hasQuery && !isLoading && (
                        <div>
                            {/* RECENT Section */}
                            {recentSearches.length > 0 && (
                                <div>
                                    <div className="px-4 py-2 flex items-center justify-between">
                                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                            RECENT
                                        </span>
                                        <button
                                            onClick={clearAllRecent}
                                            className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                        >
                                            clear all
                                        </button>
                                    </div>
                                    {recentSearches.map((search) => (
                                        <div
                                            key={search}
                                            onClick={() => {
                                                setSearchInput(search);
                                                performSearch(search);
                                            }}
                                            role="button"
                                            tabIndex={0}
                                            className="w-full px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between group cursor-pointer"
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className="text-gray-400">↺</span>
                                                <span className="text-gray-700 dark:text-gray-300">{search}</span>
                                            </div>
                                            <button
                                                onClick={(e) => removeRecentSearch(search, e)}
                                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 opacity-0 group-hover:opacity-100"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* SEARCH SUGGESTIONS */}
                            <div className="px-4 py-3">
                                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                                    SEARCH SUGGESTIONS
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {SEARCH_SUGGESTIONS.map((suggestion) => (
                                        <button
                                            key={suggestion.id}
                                            onClick={() => {
                                                setSearchInput(suggestion.name);
                                                performSearch(suggestion.name);
                                            }}
                                            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full border border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 flex items-center gap-1.5"
                                        >
                                            {EntityIcons[suggestion.type]}
                                            {suggestion.name}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* No Results */}
                    {hasQuery && !hasResults && !isLoading && (
                        <div className="py-12 text-center text-gray-500">
                            <Search className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                            <p>No results found for &quot;{searchInput}&quot;</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
