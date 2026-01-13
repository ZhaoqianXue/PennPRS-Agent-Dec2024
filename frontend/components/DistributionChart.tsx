"use client";

import React, { useEffect, useRef, useMemo, useState } from 'react';
import * as d3 from 'd3';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface DistributionChartProps {
    data: { label: string; count: number }[];
    type: 'bar' | 'donut';
    height?: number;
    colorScheme?: 'blue' | 'purple' | 'green' | 'orange' | 'amber' | 'teal';
    color?: string;
    onBarClick?: (label: string) => void;
}

const colorSchemes = {
    blue: ['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE'],
    purple: ['#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE', '#EDE9FE'],
    green: ['#10B981', '#34D399', '#6EE7B7', '#A7F3D0', '#D1FAE5'],
    orange: ['#F59E0B', '#FBBF24', '#FCD34D', '#FDE68A', '#FEF3C7'],
    amber: ['#D97706', '#F59E0B', '#FBBF24', '#FCD34D', '#FEF3C7'],
    teal: ['#059669', '#10B981', '#34D399', '#6EE7B7', '#A7F3D0'],
};

export default function DistributionChart({
    data,
    type,
    height: fixedHeight, // Optional fixed height override
    colorScheme = 'blue',
    color,
    onBarClick
}: DistributionChartProps) {
    const svgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [width, setWidth] = useState(600);
    const [hoveredItem, setHoveredItem] = useState<{ label: string; count: number; percent: number } | null>(null);
    const [isExpanded, setIsExpanded] = useState(false);

    // Config
    const limit = 6;
    const barHeight = 28;
    const gap = 12;
    const margin = { top: 10, right: 60, bottom: 20, left: 160 };

    // Process data (Sort)
    const processedData = useMemo(() => {
        return [...data].sort((a, b) => b.count - a.count);
    }, [data]);

    // Data to display based on expansion
    const displayData = useMemo(() => {
        if (type !== 'bar') return processedData;
        return isExpanded ? processedData : processedData.slice(0, limit);
    }, [processedData, isExpanded, type]);

    const hasMore = processedData.length > limit;

    // Calculate dynamic height
    const dynamicHeight = type === 'bar'
        ? displayData.length * (barHeight + gap) + margin.top + margin.bottom
        : (fixedHeight || 300);

    const chartHeight = fixedHeight || dynamicHeight;

    // Responsive width
    useEffect(() => {
        const updateWidth = () => {
            if (containerRef.current) {
                setWidth(containerRef.current.clientWidth);
            }
        };
        updateWidth();
        window.addEventListener('resize', updateWidth);
        return () => window.removeEventListener('resize', updateWidth);
    }, []);

    const total = useMemo(() => processedData.reduce((acc, curr) => acc + curr.count, 0), [processedData]);

    useEffect(() => {
        if (!svgRef.current || displayData.length === 0) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const baseColors = colorSchemes[colorScheme];
        // const colorScale = d3.scaleOrdinal() // This was unused in the original code for bar chart
        //     .range(baseColors); // Reuse colors if more items than colors

        if (type === 'bar') {
            renderBarChart(svg, displayData, width, chartHeight, color || baseColors[0]);
        } else {
            renderDonutChart(svg, displayData, width, chartHeight);
        }

    }, [displayData, type, width, chartHeight, colorScheme]); // Depend on displayData

    const renderBarChart = (
        svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
        data: { label: string; count: number }[],
        w: number,
        h: number,
        primaryColor: string
    ) => {
        // const margin = { top: 10, right: 50, bottom: 20, left: 160 }; // Large left margin for labels - REMOVED
        const innerWidth = w - margin.left - margin.right;
        // const innerHeight = h - margin.top - margin.bottom; // REMOVED

        // Take top 8 only for bars to avoid clutter, or fit height - REMOVED
        // If height is fixed, we might need scrolling or logic.
        // Let's assume passed height is dynamic or handled by parent,
        // OR we fit top N items.
        // const barHeight = 25; // MOVED TO COMPONENT LEVEL
        // const gap = 10; // MOVED TO COMPONENT LEVEL
        // Dynamic height based on data length if needed, but here we fit into `h`
        // Actually for bar chart, let's fix the dataset to top items that fit
        // const maxItems = Math.floor(innerHeight / (barHeight + gap)); // REMOVED
        // const displayData = data.slice(0, maxItems); // REMOVED

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        const xScale = d3.scaleLinear()
            .domain([0, d3.max(processedData, d => d.count) || 0]) // Scale domain based on TOTAL data max, not just visible
            .range([0, innerWidth]);

        const yScale = d3.scaleBand()
            .domain(data.map(d => d.label))
            .range([0, data.length * (barHeight + gap)]) // Adjusted range to fit all data
            .padding(0.2);

        // Bars background (optional track)
        g.selectAll('.bg-bar')
            .data(data, (d: any) => d.label) // Key by label for smooth updates
            .enter()
            .append('rect')
            .attr('class', 'bg-bar')
            .attr('y', d => yScale(d.label) || 0)
            .attr('height', yScale.bandwidth())
            .attr('x', 0)
            .attr('width', innerWidth)
            .attr('fill', '#f3f4f6') // gray-100
            .attr('opacity', 0.5)
            .attr('rx', 4);

        // Bars
        g.selectAll('.bar')
            .data(data, (d: any) => d.label) // Key by label for smooth updates
            .enter()
            .append('rect')
            .attr('class', 'bar')
            .attr('y', d => yScale(d.label) || 0)
            .attr('height', yScale.bandwidth())
            .attr('x', 0)
            .attr('width', 0) // Animate from 0
            .attr('fill', primaryColor)
            .attr('rx', 4)
            .style('cursor', 'pointer')
            .on('mouseenter', function (event, d) {
                d3.select(this).attr('opacity', 0.8);
                const percent = (d.count / total) * 100;
                setHoveredItem({ label: d.label, count: d.count, percent });
            })
            .on('mouseleave', function () {
                d3.select(this).attr('opacity', 1);
                setHoveredItem(null);
            })
            .transition()
            .duration(800)
            .attr('width', d => Math.max(xScale(d.count), 4)); // Min width visibility

        // Labels (Y Axis)
        g.append('g')
            .call(d3.axisLeft(yScale).tickSize(0))
            .call(g => g.select('.domain').remove())
            .selectAll('text')
            .attr('font-size', '13px')
            .attr('font-weight', '500')
            .attr('fill', '#374151') // gray-700
            .style('text-anchor', 'end')
            .attr('transform', 'translate(-10, 0)') // Adjusted position
            .each(function (d) {
                // simple truncation for extremely long text
                const self = d3.select(this);
                let text = self.text();
                if (text.length > 22) {
                    self.text(text.substring(0, 20) + '...');
                    self.append('title').text(text); // native tooltip
                }
            });

        // Count labels at end of bars
        g.selectAll('.count-label')
            .data(data, (d: any) => d.label) // Key by label for smooth updates
            .enter()
            .append('text')
            .attr('class', 'count-label')
            .attr('y', d => (yScale(d.label) || 0) + yScale.bandwidth() / 2 + 5) // Adjusted y position
            .attr('x', d => xScale(d.count) + 8) // Adjusted x position
            .text(d => d.count)
            .attr('font-size', '12px')
            .attr('font-weight', '600') // Added font weight
            .attr('fill', '#4b5563') // Adjusted fill color
            .attr('opacity', 0)
            .transition()
            .delay(500)
            .duration(300)
            .attr('opacity', 1);
    };

    const renderDonutChart = (
        svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
        data: { label: string; count: number }[],
        w: number,
        h: number
    ) => {
        const radius = Math.min(w, h) / 2;
        const innerRadius = radius * 0.6; // Donut thickness
        const g = svg.append('g').attr('transform', `translate(${w / 2},${h / 2})`);

        const color = d3.scaleOrdinal()
            // Use our custom palette or D3 scheme
            .range(['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#EC4899']);

        const pie = d3.pie<{ label: string; count: number }>()
            .value(d => d.count)
            .sort(null); // Keep order or sort? typically sorting desc is better
        // .sort((a, b) => b.value - a.value);

        const arc = d3.arc<d3.PieArcDatum<{ label: string; count: number }>>()
            .innerRadius(innerRadius)
            .outerRadius(radius);

        const arcHover = d3.arc<d3.PieArcDatum<{ label: string; count: number }>>()
            .innerRadius(innerRadius)
            .outerRadius(radius + 5);

        // Group small slices into "Others" if too many?
        // For simplicity, let's just render top 8.
        const topData = data.slice(0, 8);
        const othersCount = data.slice(8).reduce((acc, curr) => acc + curr.count, 0);
        const finalData = othersCount > 0 ? [...topData, { label: 'Others', count: othersCount }] : topData;

        const arcs = g.selectAll('path')
            .data(pie(finalData))
            .enter()
            .append('path')
            .attr('d', arc)
            .attr('fill', (d, i) => color(i.toString()) as string)
            .attr('stroke', 'white')
            .style('stroke-width', '2px')
            .style('cursor', 'pointer')
            .on('mouseenter', function (event, d) {
                d3.select(this)
                    .transition().duration(200)
                    .attr('d', (d: any) => arcHover(d));

                const percent = (d.data.count / total) * 100;
                setHoveredItem({ label: d.data.label, count: d.data.count, percent });
            })
            .on('mouseleave', function () {
                d3.select(this)
                    .transition().duration(200)
                    .attr('d', (d: any) => arc(d));
                setHoveredItem(null);
            })
            .transition() // Entry animation
            .duration(1000)
            .attrTween('d', function (d) {
                const i = d3.interpolate(d.startAngle + 0.1, d.endAngle);
                return function (t) {
                    d.endAngle = i(t);
                    return arc(d) || '';
                }
            });
    };

    return (
        <div ref={containerRef} className="relative w-full flex flex-col items-center animate-in fade-in duration-300">
            {/* Legend / Hover Info Overlay for Donut */}
            {type === 'donut' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    {hoveredItem ? (
                        <>
                            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 animate-in fade-in zoom-in">
                                {hoveredItem.count}
                            </div>
                            <div className="text-xs text-gray-500 font-medium max-w-[120px] text-center truncate px-2">
                                {hoveredItem.label}
                            </div>
                            <div className="text-xs text-gray-400">
                                {hoveredItem.percent.toFixed(1)}%
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                {total}
                            </div>
                            <div className="text-xs text-gray-500">Total</div>
                        </>
                    )}
                </div>
            )}

            <svg ref={svgRef} width={width} height={chartHeight} className="overflow-visible transition-all duration-500 ease-in-out" />

            {/* Tooltip for Bar Chart - simpler to use standard HTML positioned absolute relative to chart if needed,
                but our Donut center text handles that.
                For Bar chart, we might want a floating tooltip or just stick to the text labels we added.
            */}

            {/* Toggle Button for Bar Chart */}
            {type === 'bar' && hasMore && (
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="mt-2 flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-full transition-colors border border-gray-200 dark:border-gray-700"
                >
                    {isExpanded ? (
                        <>
                            Show Less <ChevronUp className="w-3 h-3" />
                        </>
                    ) : (
                        <>
                            Show {processedData.length - limit} More <ChevronDown className="w-3 h-3" />
                        </>
                    )}
                </button>
            )}
        </div>
    );
}
