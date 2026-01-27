"use client";

import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { X } from 'lucide-react';
import { ModelData } from './ModelCard';
import ModelCard from './ModelCard';

interface BeeSwarmChartProps {
    data: ModelData[];
    width?: number;
    height?: number;
    colorScheme?: 'blue' | 'purple' | 'green' | 'orange' | 'teal';
    formatValue?: (value: number) => string;
    onViewDetails?: (model: ModelData) => void;
    onSaveModel?: (model: ModelData, event?: React.MouseEvent) => void;
    activeAncestry?: string[];
    valueAccessor?: (model: ModelData) => number | undefined | null; // New prop for generic data access
    domain?: [number, number];
    scaleType?: 'linear' | 'sqrt' | 'log';
    xAxisLabel?: string;
}

interface SimulatedPoint {
    model: ModelData;
    value: number;
    x: number;
    y: number;
    index: number;
}

const colorSchemes = {
    blue: {
        primary: '#3B82F6',
        secondary: '#93C5FD',
        highlight: '#2563EB',
        bg: 'rgba(59, 130, 246, 0.1)'
    },
    purple: {
        primary: '#8B5CF6',
        secondary: '#C4B5FD',
        highlight: '#7C3AED',
        bg: 'rgba(139, 92, 246, 0.1)'
    },
    green: {
        primary: '#10B981',
        secondary: '#6EE7B7',
        highlight: '#059669',
        bg: 'rgba(16, 185, 129, 0.1)'
    },
    orange: {
        primary: '#F59E0B',
        secondary: '#FCD34D',
        highlight: '#D97706',
        bg: 'rgba(245, 158, 11, 0.1)'
    },
    teal: {
        primary: '#14B8A6',
        secondary: '#99F6E4',
        highlight: '#0D9488',
        bg: 'rgba(20, 184, 166, 0.1)'
    }
};

function formatNumber(n: number): string {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(0)}k`;
    return n.toLocaleString();
}

export default function BeeSwarmChart({
    data,
    width = 600,
    height = 180,
    colorScheme = 'blue',
    formatValue = formatNumber,
    onViewDetails,
    onSaveModel,
    activeAncestry,
    valueAccessor = (m) => m.sample_size, // Default to sample_size
    domain,
    scaleType = 'sqrt',
    xAxisLabel = 'Sample Size'
}: BeeSwarmChartProps) {
    const svgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [selectedModel, setSelectedModel] = useState<ModelData | null>(null);
    const [popupPos, setPopupPos] = useState({ x: 0, y: 0 });
    const [popupAlign, setPopupAlign] = useState<'left' | 'center' | 'right'>('center');
    const [containerWidth, setContainerWidth] = useState(width);
    const [hasAnimated, setHasAnimated] = useState(false);

    const colors = colorSchemes[colorScheme];
    const margin = { top: 20, right: 30, bottom: 40, left: 30 };

    // Filter data with valid values
    const validData = useMemo(() => {
        return data.filter(m => {
            const val = valueAccessor(m);
            return typeof val === 'number' && !isNaN(val) && val > 0; // Filter 0 or invalid
        }).sort((a, b) => (valueAccessor(a) || 0) - (valueAccessor(b) || 0));
    }, [data, valueAccessor]);

    // Responsive width
    useEffect(() => {
        const updateWidth = () => {
            if (containerRef.current) {
                const newWidth = containerRef.current.clientWidth;
                if (Math.abs(newWidth - containerWidth) > 10) {
                    setContainerWidth(newWidth);
                    setHasAnimated(false);
                }
            }
        };
        updateWidth();
        window.addEventListener('resize', updateWidth);
        return () => window.removeEventListener('resize', updateWidth);
    }, [containerWidth]);

    // Close popup when clicking outside
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            const target = e.target as HTMLElement;
            if (selectedModel && !target.closest('.model-popup') && !target.closest('circle')) {
                setSelectedModel(null);
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, [selectedModel]);

    // Calculate statistics
    const stats = useMemo(() => {
        if (validData.length === 0) return null;
        const values = validData.map(d => valueAccessor(d) as number).sort((a, b) => a - b);
        const q1 = d3.quantile(values, 0.25) || 0;
        const median = d3.quantile(values, 0.5) || 0;
        const q3 = d3.quantile(values, 0.75) || 0;
        const min = d3.min(values) || 0;
        const max = d3.max(values) || 0;
        return { min, q1, median, q3, max };
    }, [validData, valueAccessor]);

    // Pre-calculate simulated positions (cached)
    const simulatedData = useMemo(() => {
        if (validData.length === 0 || !stats) return [];

        const innerWidth = containerWidth - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        let xScale: any;
        if (scaleType === 'linear') {
            xScale = d3.scaleLinear()
                .domain(domain || [0, stats.max * 1.1])
                .range([0, innerWidth]);
        } else if (scaleType === 'log') {
            xScale = d3.scaleLog()
                .domain(domain || [Math.max(1, stats.min), stats.max * 1.5])
                .nice() // Nicer ticks for log
                .range([0, innerWidth]);
        } else {
            xScale = d3.scaleSqrt()
                .domain(domain || [0, stats.max * 1.1])
                .range([0, innerWidth]);
        }

        // Create simulation nodes
        const nodes = validData.map((model, i) => ({
            model,
            value: valueAccessor(model) as number,
            x: xScale(valueAccessor(model) as number),
            y: innerHeight / 2,
            index: i
        }));

        // Run force simulation synchronously
        const simulation = d3.forceSimulation(nodes)
            .force('x', d3.forceX((d: any) => xScale(d.value)).strength(1))
            .force('y', d3.forceY(innerHeight / 2).strength(0.1))
            .force('collide', d3.forceCollide(6))
            .stop();

        for (let i = 0; i < 120; i++) simulation.tick();

        return nodes as SimulatedPoint[];
    }, [validData, containerWidth, height, stats, margin, valueAccessor, domain, scaleType]);

    // D3 rendering
    useEffect(() => {
        if (!svgRef.current || simulatedData.length === 0 || !stats) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const innerWidth = containerWidth - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const g = svg
            .attr('width', containerWidth)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        let xScale: any;
        if (scaleType === 'linear') {
            xScale = d3.scaleLinear()
                .domain(domain || [0, stats.max * 1.1])
                .range([0, innerWidth]);
        } else if (scaleType === 'log') {
            xScale = d3.scaleLog()
                .domain(domain || [Math.max(1, stats.min), stats.max * 1.5])
                .nice()
                .range([0, innerWidth]);
        } else {
            xScale = d3.scaleSqrt()
                .domain(domain || [0, stats.max * 1.1])
                .range([0, innerWidth]);
        }

        // Draw IQR box
        g.append('rect')
            .attr('x', xScale(stats.q1))
            .attr('y', innerHeight / 2 - 25)
            .attr('width', Math.max(xScale(stats.q3) - xScale(stats.q1), 2))
            .attr('height', 50)
            .attr('fill', colors.bg)
            .attr('rx', 6);

        // Draw median line
        g.append('line')
            .attr('x1', xScale(stats.median))
            .attr('y1', innerHeight / 2 - 45) // Make it taller to stick out
            .attr('x2', xScale(stats.median))
            .attr('y2', innerHeight / 2 + 45)
            .attr('stroke', '#1e3a8a') // Much darker blue (blue-900)
            .attr('stroke-width', 3)   // Thicker
            .attr('opacity', 0.8);     // Slight opacity for blend

        // Draw points
        const points = g.selectAll('circle')
            .data(simulatedData)
            .enter()
            .append('circle')
            .attr('cx', (d) => d.x)
            .attr('cy', (d) => Math.min(Math.max(d.y, 10), innerHeight - 10))
            .attr('r', hasAnimated ? 5 : 0)
            .attr('fill', (d) => {
                // Color interpolation based on position in domain
                const [minDom, maxDom] = xScale.domain();
                const val = d.value;
                let percentile = 0;

                if (scaleType === 'sqrt') {
                    const maxSqrt = Math.sqrt(maxDom);
                    const valSqrt = Math.sqrt(val);
                    percentile = valSqrt / maxSqrt;
                } else if (scaleType === 'log') {
                    const minLog = Math.log(Math.max(1, minDom));
                    const maxLog = Math.log(maxDom);
                    const valLog = Math.log(Math.max(1, val));
                    percentile = (valLog - minLog) / (maxLog - minLog || 1);
                } else {
                    percentile = (val - minDom) / (maxDom - minDom);
                }
                // Clamp percentile
                percentile = Math.max(0, Math.min(1, percentile));

                return d3.interpolateRgb(colors.secondary, colors.primary)(percentile);
            })
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .style('cursor', 'pointer')
            .style('filter', 'drop-shadow(0 1px 2px rgba(0,0,0,0.1))')
            .on('mouseenter', function () {
                d3.select(this)
                    .attr('r', 7)
                    .attr('stroke-width', 2);
            })
            .on('mouseleave', function () {
                d3.select(this)
                    .attr('r', 5)
                    .attr('stroke-width', 1.5);
            })
            .on('click', function (event, d) {
                event.stopPropagation();
                const rect = containerRef.current!.getBoundingClientRect();
                const clickX = event.clientX - rect.left;
                const clickY = event.clientY - rect.top;

                const cardWidth = 280;
                const padding = 10;

                // Determine alignment based on click position
                let align: 'left' | 'center' | 'right' = 'center';
                let popX = clickX;

                if (clickX < cardWidth / 2 + padding) {
                    // Too close to left edge - align left
                    align = 'left';
                    popX = Math.max(padding, clickX);
                } else if (clickX > containerWidth - cardWidth / 2 - padding) {
                    // Too close to right edge - align right
                    align = 'right';
                    popX = Math.min(containerWidth - padding, clickX);
                } else {
                    // Center is fine
                    align = 'center';
                    popX = clickX;
                }

                setPopupPos({ x: popX, y: clickY + 15 });
                setPopupAlign(align);
                setSelectedModel(d.model);
            });

        // Animate entrance only once
        if (!hasAnimated) {
            points.transition()
                .duration(600)
                .delay((_, i) => i * 3)
                .attr('r', 5)
                .on('end', () => setHasAnimated(true));
        }

        // X-axis Generation
        let xAxis;
        if (scaleType === 'linear') {
            xAxis = d3.axisBottom(xScale)
                .ticks(6)
                .tickFormat((d) => formatValue(d as number));
        } else if (scaleType === 'log') {
            xAxis = d3.axisBottom(xScale)
                .ticks(5)
                .tickFormat((d) => formatValue(d as number));
        } else {
            // Generate visually equidistant ticks for Sqrt scale
            const tickCount = 6;
            const [minDom, maxDom] = xScale.domain();
            const tickValues: number[] = [];

            for (let i = 0; i <= tickCount; i++) {
                const ratio = i / tickCount;
                // Value = max * ratio^2 (inverse of sqrt) keeps ticks physically evenly spaced (approx for 0 base)
                const val = maxDom * (ratio * ratio);

                // Round nicely for sample sizes
                let rounded = val;
                if (val > 1000000) rounded = Math.round(val / 500000) * 500000;      // 0.5M steps
                else if (val > 100000) rounded = Math.round(val / 50000) * 50000;    // 50k steps
                else if (val > 10000) rounded = Math.round(val / 10000) * 10000;     // 10k steps
                else if (val > 1000) rounded = Math.round(val / 1000) * 1000;        // 1k steps

                if (i === 0 || rounded > (tickValues[tickValues.length - 1] || -1)) {
                    tickValues.push(rounded);
                }
            }

            xAxis = d3.axisBottom(xScale)
                .tickValues(tickValues)
                .tickFormat((d) => formatValue(d as number));
        }

        g.append('g')
            .attr('transform', `translate(0,${innerHeight + 5})`)
            .call(xAxis)
            .call(g => g.select('.domain').attr('stroke', '#e5e7eb'))
            .call(g => g.selectAll('.tick line').attr('stroke', '#e5e7eb'))
            .call(g => g.selectAll('.tick text')
                .attr('fill', '#6b7280')
                .attr('font-size', '11px'));

        g.append('text')
            .attr('x', innerWidth / 2)
            .attr('y', innerHeight + 35)
            .attr('text-anchor', 'middle')
            .attr('fill', '#9ca3af')
            .attr('font-size', '11px')
            .text(xAxisLabel);

    }, [simulatedData, containerWidth, height, stats, colors, margin, formatValue, hasAnimated, domain, scaleType, xAxisLabel]);

    if (validData.length === 0) {
        return (
            <div className="text-gray-400 italic text-sm p-4">
                No {xAxisLabel.toLowerCase()} data available
            </div>
        );
    }

    const handleViewDetails = (model: ModelData) => {
        setSelectedModel(null);
        if (onViewDetails) {
            onViewDetails(model);
        }
    };

    return (
        <div ref={containerRef} className="relative w-full">
            <svg ref={svgRef} className="w-full" />

            {/* Model Card Popup */}
            {selectedModel && (
                <div
                    className="model-popup absolute z-50"
                    style={{
                        left: popupPos.x,
                        top: popupPos.y,
                        transform: popupAlign === 'left'
                            ? 'translateX(0)'
                            : popupAlign === 'right'
                                ? 'translateX(-100%)'
                                : 'translateX(-50%)',
                        width: '280px'
                    }}
                >
                    <div className="relative animate-in fade-in zoom-in-95 duration-200">
                        {/* Close button */}
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedModel(null);
                            }}
                            className="absolute -top-2 -right-2 z-10 w-6 h-6 bg-gray-800 hover:bg-gray-700 text-white rounded-full flex items-center justify-center shadow-lg transition-colors"
                        >
                            <X size={14} />
                        </button>

                        {/* ModelCard */}
                        <div className="shadow-2xl rounded-xl overflow-hidden ring-1 ring-gray-200 dark:ring-gray-700">
                            <ModelCard
                                model={selectedModel}
                                onSelect={() => { }}
                                onViewDetails={handleViewDetails}
                                onSaveModel={(model: ModelData) => {
                                    setSelectedModel(null);
                                    onSaveModel?.(model);
                                }}
                                activeAncestry={activeAncestry}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-2 text-xs text-gray-500">
                <div className="flex items-center gap-1.5">
                    <div
                        className="w-3 h-3 rounded-sm"
                        style={{ backgroundColor: colors.bg, border: `1px solid ${colors.secondary}` }}
                    />
                    <span>IQR (25%-75%)</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div
                        className="w-0.5 h-3 rounded"
                        style={{ backgroundColor: colors.highlight }}
                    />
                    <span>Median</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: colors.primary }}
                    />
                    <span>Click to preview ({validData.length} models)</span>
                </div>
            </div>
        </div>
    );
}

