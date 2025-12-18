"use client"
import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { BarChart3 } from 'lucide-react';

const data = [
    { name: 'Temperature @ 2m', GraphCast: 2.21, Cerrora: 0.90 },
    { name: 'Wind U @ 10m', GraphCast: 1.94, Cerrora: 1.34 },
    { name: 'Wind V @ 10m', GraphCast: 1.97, Cerrora: 1.36 },
    { name: 'Humidity @ 850hPa', GraphCast: 2.47, Cerrora: 2.35 },
    { name: 'Temperature @ 850hPa', GraphCast: 0.5, Cerrora: 0.4 }
];

const BarChrt = () => {
    // Custom tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="glass-panel rounded-lg p-3 shadow-hard border border-border/50">
                    <p className="text-xs font-semibold text-foreground mb-2">{label}</p>
                    {payload.map((entry: any, index: number) => (
                        <p key={index} className="text-xs" style={{ color: entry.fill }}>
                            {entry.name}: {entry.value.toFixed(2)}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h3 className="text-base font-semibold flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-primary" />
                    Error Metrics by Variable 
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                    Mean Squared Error (MSE) across weather variables
                </p>
            </div>

            {/* Chart Container */}
            <div className="w-full h-[300px] sm:h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={data}
                        margin={{
                            top: 10,
                            right: 10,
                            left: 0,
                            bottom: 20,
                        }}
                    >
                        <CartesianGrid 
                            stroke="hsl(var(--border))" 
                            strokeDasharray="3 3" 
                            opacity={0.3}
                        />
                        <XAxis 
                            dataKey="name" 
                            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                            stroke="hsl(var(--border))"
                            angle={-0}
                            textAnchor="end"
                            height={80}
                        />
                        <YAxis  
                            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                            stroke="hsl(var(--border))"
                            label={{ 
                                value: 'Error Value', 
                                position: 'insideLeft', 
                                angle: -90,
                                style: { 
                                    fill: "hsl(var(--muted-foreground))",
                                    fontSize: 12,
                                    fontWeight: 500
                                }
                            }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend 
                            wrapperStyle={{
                                paddingTop: '10px',
                                fontSize: '12px'
                            }}
                        />
                        <Bar 
                            dataKey="GraphCast" 
                            fill="hsl(0, 84%, 60%)" 
                            radius={[6, 6, 0, 0]}
                            name="GraphCast"
                        />
                        <Bar 
                            dataKey="Cerrora" 
                            fill="hsl(142, 76%, 36%)" 
                            radius={[6, 6, 0, 0]}
                            name="Cerrora"
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            
        </div>
    );
};

export default BarChrt;
