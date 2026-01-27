import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { X, Search, Database, ExternalLink, ChevronRight, Check, Loader2, AlertCircle, RotateCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export interface GWASEntry {
    database: 'gwas_catalog' | 'finngen';
    id: string;
    trait: string;
    category?: string;
    nCases?: number;
    nControls?: number;
    nTotal?: number; // Total sample size for continuous traits
    sampleInfo?: string;
    url: string;
    pubmedId?: string;
    date?: string;
}

interface GWASSearchModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (entry: GWASEntry) => void | Promise<void>;
    initialSelection?: GWASEntry | null;
}

type DatabaseTab = 'all' | 'gwas_catalog' | 'finngen';

// Parse FinnGen TSV line
function parseFinnGenLine(line: string): GWASEntry | null {
    const parts = line.split('\t');
    if (parts.length < 6) return null;

    const [phenocode, trait, category, nCases, nControls, url] = parts;
    if (!phenocode || !trait) return null;

    return {
        database: 'finngen',
        id: phenocode.trim(),
        trait: trait.trim(),
        category: category?.trim(),
        nCases: parseInt(nCases) || undefined,
        nControls: parseInt(nControls) || undefined,
        url: url?.trim() || `https://risteys.finngen.fi/endpoints/${phenocode.trim()}`,
    };
}

// Parse GWAS Catalog TSV line
function parseGWASCatalogLine(line: string): GWASEntry | null {
    const parts = line.split('\t');
    if (parts.length < 6) return null;

    const [pubmedId, trait, date, sampleInfo, studyAccession, url] = parts;
    if (!studyAccession || !trait) return null;

    // Extract sample counts from sampleInfo
    const sampleCounts = sampleInfo ? extractSampleCounts(sampleInfo) : {};

    return {
        database: 'gwas_catalog',
        id: studyAccession.trim(),
        trait: trait.trim(),
        sampleInfo: sampleInfo?.trim(),
        pubmedId: pubmedId?.trim(),
        date: date?.trim(),
        url: url?.trim() || `https://www.ebi.ac.uk/gwas/studies/${studyAccession.trim()}`,
        nCases: sampleCounts.nCases,
        nControls: sampleCounts.nControls,
        nTotal: sampleCounts.nTotal,
    };
}

// Extract case/control numbers or total individuals from sample info string
function extractSampleCounts(sampleInfo: string): { nCases?: number; nControls?: number; nTotal?: number } {
    // First try to extract cases and controls
    const casesMatch = sampleInfo.match(/([\d,]+)\s*(?:[\w\s]+)?cases/i);
    const controlsMatch = sampleInfo.match(/([\d,]+)\s*(?:[\w\s]+)?controls/i);

    if (casesMatch && controlsMatch) {
        return {
            nCases: parseInt(casesMatch[1].replace(/,/g, '')),
            nControls: parseInt(controlsMatch[1].replace(/,/g, '')),
        };
    }

    // Try to extract total individuals (for continuous traits)
    const individualsMatch = sampleInfo.match(/([\d,]+)\s*(?:[\w\s]+)?individuals/i);
    if (individualsMatch) {
        return {
            nTotal: parseInt(individualsMatch[1].replace(/,/g, '')),
        };
    }

    return {};
}

export default function GWASSearchModal({ isOpen, onClose, onSelect, initialSelection }: GWASSearchModalProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const [activeTab, setActiveTab] = useState<DatabaseTab>('all');
    const [selectedEntry, setSelectedEntry] = useState<GWASEntry | null>(initialSelection || null);

    const [finngenData, setFinngenData] = useState<GWASEntry[]>([]);
    const [gwasData, setGwasData] = useState<GWASEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isClassifying, setIsClassifying] = useState(false);

    // Ref for the results container to scroll to top when loading
    const resultsContainerRef = useRef<HTMLDivElement>(null);

    // Load data from TSV files
    useEffect(() => {
        if (!isOpen) return;

        const loadData = async () => {
            setIsLoading(true);
            setError(null);

            try {
                // Load FinnGen data
                const finngenRes = await fetch('/gwas_metadata/finngen.tsv');
                if (!finngenRes.ok) throw new Error('Failed to load FinnGen data');
                const finngenText = await finngenRes.text();
                const finngenEntries = finngenText
                    .split('\n')
                    .filter(line => line.trim())
                    .map(parseFinnGenLine)
                    .filter((entry): entry is GWASEntry => entry !== null);
                setFinngenData(finngenEntries);

                // Load GWAS Catalog data
                const gwasRes = await fetch('/gwas_metadata/gwas_catalog.tsv');
                if (!gwasRes.ok) throw new Error('Failed to load GWAS Catalog data');
                const gwasText = await gwasRes.text();
                const gwasEntries = gwasText
                    .split('\n')
                    .filter(line => line.trim())
                    .map(parseGWASCatalogLine)
                    .filter((entry): entry is GWASEntry => entry !== null);
                setGwasData(gwasEntries);

            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load data');
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, [isOpen]);

    // Debounce search query
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedQuery(searchQuery);
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    // Filter results based on search query and active tab
    const filteredResults = useMemo(() => {
        const query = debouncedQuery.toLowerCase().trim();

        let allData: GWASEntry[] = [];
        if (activeTab === 'all' || activeTab === 'gwas_catalog') {
            allData = [...allData, ...gwasData];
        }
        if (activeTab === 'all' || activeTab === 'finngen') {
            allData = [...allData, ...finngenData];
        }

        if (!query) {
            // Return first 100 entries if no search query
            return allData.slice(0, 100);
        }

        const filtered = allData.filter(entry => {
            const traitMatch = entry.trait.toLowerCase().includes(query);
            const idMatch = entry.id.toLowerCase().includes(query);
            const categoryMatch = entry.category?.toLowerCase().includes(query);
            return traitMatch || idMatch || categoryMatch;
        });

        // Limit results for performance
        return filtered.slice(0, 100);
    }, [debouncedQuery, activeTab, finngenData, gwasData]);

    // Get counts for tabs
    const counts = useMemo(() => {
        const query = debouncedQuery.toLowerCase().trim();

        const filterFn = (entry: GWASEntry) => {
            if (!query) return true;
            const traitMatch = entry.trait.toLowerCase().includes(query);
            const idMatch = entry.id.toLowerCase().includes(query);
            const categoryMatch = entry.category?.toLowerCase().includes(query);
            return traitMatch || idMatch || categoryMatch;
        };

        return {
            all: gwasData.filter(filterFn).length + finngenData.filter(filterFn).length,
            gwas_catalog: gwasData.filter(filterFn).length,
            finngen: finngenData.filter(filterFn).length,
        };
    }, [debouncedQuery, finngenData, gwasData]);

    // Clear error when tab or search changes
    useEffect(() => {
        setError(null);
    }, [debouncedQuery, activeTab]);

    const handleConfirm = useCallback(async () => {
        if (selectedEntry) {
            // Scroll to top to ensure loading overlay is visible
            if (resultsContainerRef.current) {
                resultsContainerRef.current.scrollTop = 0;
            }
            setIsClassifying(true);
            setError(null);
            try {
                await onSelect(selectedEntry);
                onClose();
            } catch (err: any) {
                // Handled error - display to user
                setError(err.message || 'Selection failed');
            } finally {
                setIsClassifying(false);
            }
        }
    }, [selectedEntry, onSelect, onClose]);

    const handleEntryClick = useCallback((entry: GWASEntry) => {
        setSelectedEntry(entry);
    }, []);

    // Reset state when modal opens
    useEffect(() => {
        if (isOpen) {
            setSearchQuery('');
            setDebouncedQuery('');
            setActiveTab('all');
            setSelectedEntry(initialSelection || null);
        }
    }, [isOpen, initialSelection]);

    const formatSampleSize = (entry: GWASEntry) => {
        if (entry.database === 'finngen') {
            if (entry.nCases && entry.nControls) {
                return `${entry.nCases.toLocaleString()} cases, ${entry.nControls.toLocaleString()} controls`;
            }
        } else if (entry.sampleInfo) {
            return entry.sampleInfo.length > 80
                ? entry.sampleInfo.substring(0, 80) + '...'
                : entry.sampleInfo;
        }
        return null;
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/50 backdrop-blur-[2px]"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 10 }}
                        className="relative w-full max-w-3xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 flex flex-col max-h-[85vh] overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-5 border-b border-gray-100 dark:border-gray-800 shrink-0">
                            <div className="flex items-center gap-3">
                                <span className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white p-2 rounded-xl">
                                    <Database className="w-5 h-5" />
                                </span>
                                <div>
                                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                                        Search GWAS Database
                                    </h2>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        Find and select GWAS summary statistics
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Search & Filters */}
                        <div className="p-4 border-b border-gray-100 dark:border-gray-800 space-y-4 shrink-0">
                            {/* Search Input */}
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search for disease or trait..."
                                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    autoFocus
                                />
                            </div>

                            {/* Database Tabs */}
                            <div className="flex gap-2">
                                {[
                                    { key: 'all' as DatabaseTab, label: 'All', count: counts.all },
                                    { key: 'gwas_catalog' as DatabaseTab, label: 'GWAS Catalog', count: counts.gwas_catalog },
                                    { key: 'finngen' as DatabaseTab, label: 'FinnGen', count: counts.finngen },
                                ].map(tab => (
                                    <button
                                        key={tab.key}
                                        onClick={() => setActiveTab(tab.key)}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${activeTab === tab.key
                                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                                            }`}
                                    >
                                        {tab.label}
                                        <span className={`text-xs px-1.5 py-0.5 rounded-full ${activeTab === tab.key
                                            ? 'bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200'
                                            : 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                                            }`}>
                                            {tab.count > 1000 ? `${(tab.count / 1000).toFixed(1)}k` : tab.count}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Results */}
                        <div ref={resultsContainerRef} className="flex-1 overflow-y-auto relative">
                            {/* Loading Overlay - Shows when classifying */}
                            <AnimatePresence>
                                {isClassifying && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="absolute inset-0 z-20 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm flex flex-col items-center justify-center"
                                    >
                                        {/* Animated circles */}
                                        <div className="relative w-24 h-24 mb-6">
                                            <motion.div
                                                className="absolute inset-0 rounded-full border-4 border-blue-500/20"
                                                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
                                                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                                            />
                                            <motion.div
                                                className="absolute inset-2 rounded-full border-4 border-indigo-500/30"
                                                animate={{ scale: [1.1, 0.9, 1.1], opacity: [0.3, 0.6, 0.3] }}
                                                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut", delay: 0.2 }}
                                            />
                                            <motion.div
                                                className="absolute inset-4 rounded-full border-4 border-purple-500/40"
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                                            />
                                            {/* Center spinner */}
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <motion.div
                                                    animate={{ rotate: -360 }}
                                                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                                                >
                                                    <Database className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                                                </motion.div>
                                            </div>
                                        </div>

                                        {/* Status text */}
                                        <motion.h3
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.1 }}
                                            className="text-lg font-semibold text-gray-900 dark:text-white mb-2"
                                        >
                                            Analyzing Study
                                        </motion.h3>
                                        <motion.p
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.2 }}
                                            className="text-sm text-gray-500 dark:text-gray-400 text-center max-w-xs"
                                        >
                                            Fetching study metadata from GWAS Catalog and classifying trait type...
                                        </motion.p>

                                        {/* Selected study info */}
                                        {selectedEntry && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: 0.3 }}
                                                className="mt-6 px-4 py-3 bg-gray-100 dark:bg-gray-800 rounded-xl"
                                            >
                                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Selected Study</p>
                                                <p className="text-sm font-medium text-gray-900 dark:text-white">
                                                    {selectedEntry.id}
                                                </p>
                                                <p className="text-xs text-gray-600 dark:text-gray-300 truncate max-w-[200px]">
                                                    {selectedEntry.trait}
                                                </p>
                                            </motion.div>
                                        )}

                                        {/* Progress indicator */}
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: "100%" }}
                                            transition={{ duration: 3, ease: "easeInOut" }}
                                            className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-full"
                                        />
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {isLoading ? (
                                <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                                    <Loader2 className="w-8 h-8 animate-spin mb-3" />
                                    <p className="text-sm">Loading GWAS data...</p>
                                </div>
                            ) : error ? (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="h-full flex flex-col items-center justify-center p-8 text-center"
                                >
                                    <div className="w-full max-w-sm p-8 rounded-3xl bg-pink-50/50 dark:bg-red-900/10 border border-pink-100 dark:border-red-900/30 shadow-sm relative overflow-hidden group">
                                        {/* Background Decoration */}
                                        <div className="absolute top-0 right-0 -transtale-y-1/2 translate-x-1/2 w-32 h-32 bg-pink-200/20 dark:bg-pink-500/10 rounded-full blur-3xl pointer-events-none" />

                                        <div className="relative z-10 space-y-6">
                                            <div className="w-16 h-16 rounded-2xl bg-white dark:bg-gray-800 shadow-sm flex items-center justify-center mx-auto mb-2 border border-pink-50 dark:border-red-900/20">
                                                <AlertCircle className="w-8 h-8 text-pink-500" />
                                            </div>

                                            <div className="space-y-2">
                                                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Selection Conflict</h3>
                                                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                                                    {error}
                                                </p>
                                            </div>

                                            <button
                                                onClick={() => setError(null)}
                                                className="w-full py-3.5 px-6 rounded-2xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-sm font-semibold hover:bg-gray-800 dark:hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl active:scale-[0.98] flex items-center justify-center gap-2"
                                            >
                                                <RotateCcw className="w-4 h-4" />
                                                Return to Search
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            ) : filteredResults.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                                    <Database className="w-12 h-12 mb-3 opacity-50" />
                                    <p className="text-sm">No results found</p>
                                    <p className="text-xs mt-1">Try a different search term</p>
                                </div>
                            ) : (
                                <div className="divide-y divide-gray-100 dark:divide-gray-800">
                                    {filteredResults.map((entry, index) => (
                                        <button
                                            key={`${entry.database}-${entry.id}-${index}`}
                                            onClick={() => handleEntryClick(entry)}
                                            disabled={isClassifying}
                                            className={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors flex items-start gap-3 disabled:pointer-events-none disabled:opacity-50 ${selectedEntry?.id === entry.id && selectedEntry?.database === entry.database
                                                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-2 border-blue-500'
                                                : ''
                                                }`}
                                        >
                                            {/* Selection indicator */}
                                            <div className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${selectedEntry?.id === entry.id && selectedEntry?.database === entry.database
                                                ? 'border-blue-500 bg-blue-500'
                                                : 'border-gray-300 dark:border-gray-600'
                                                }`}>
                                                {selectedEntry?.id === entry.id && selectedEntry?.database === entry.database && (
                                                    <Check className="w-3 h-3 text-white" />
                                                )}
                                            </div>

                                            {/* Entry content */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="flex-1 min-w-0">
                                                        <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                                            {entry.trait}
                                                        </h4>
                                                        <div className="flex items-center gap-2 mt-1">
                                                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                                                                {entry.id}
                                                            </span>
                                                            <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${entry.database === 'finngen'
                                                                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                                                                : 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                                                                }`}>
                                                                {entry.database === 'finngen' ? 'FinnGen' : 'GWAS Catalog'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <a
                                                        href={entry.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        onClick={(e) => e.stopPropagation()}
                                                        className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors shrink-0"
                                                    >
                                                        <ExternalLink className="w-4 h-4" />
                                                    </a>
                                                </div>
                                                {formatSampleSize(entry) && (
                                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                                                        {formatSampleSize(entry)}
                                                    </p>
                                                )}
                                                {/* Show Date and PubMed for GWAS Catalog */}
                                                {entry.database === 'gwas_catalog' && (entry.date || entry.pubmedId) && (
                                                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-400 dark:text-gray-500">
                                                        {entry.date && (
                                                            <span>Date: {entry.date}</span>
                                                        )}
                                                        {entry.pubmedId && (
                                                            <span>PMID: {entry.pubmedId}</span>
                                                        )}
                                                    </div>
                                                )}
                                                {entry.category && (
                                                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">
                                                        {entry.category}
                                                    </p>
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-gray-100 dark:border-gray-800 shrink-0 flex items-center justify-between bg-gray-50 dark:bg-gray-900/50">
                            <div className="text-xs text-gray-500">
                                {!isLoading && !error && (
                                    <>
                                        Showing {Math.min(filteredResults.length, 100)} of {counts.all > 1000 ? `${(counts.all / 1000).toFixed(1)}k` : counts.all} results
                                    </>
                                )}
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={onClose}
                                    className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors disabled:opacity-50"
                                    disabled={isClassifying}
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleConfirm}
                                    disabled={!selectedEntry || isClassifying}
                                    className={`px-5 py-2 text-sm font-medium rounded-lg transition-all flex items-center gap-2 ${selectedEntry && !isClassifying
                                        ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                                        : 'bg-gray-200 text-gray-400 dark:bg-gray-700 dark:text-gray-500 cursor-not-allowed'
                                        }`}
                                >
                                    {isClassifying ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            Confirm Selection
                                            <ChevronRight className="w-4 h-4" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
