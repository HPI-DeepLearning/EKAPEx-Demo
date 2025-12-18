"use client"
import React, {useEffect, useState} from 'react';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import {fetchTempMetrics} from "@/lib/api-client";
import {EUROPEAN_COUNTRIES} from "@/components/EuropeanCountries";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {useSelector} from "react-redux";
import { MapPin } from 'lucide-react';


const kelvinToCelsius = (k: number) => k - 273.15;

const LIneChrt: React.FC = (): React.JSX.Element => {
    const [weatherMetrics,setWeatherMetrics] = useState<any[]>([]);
    const [country, setCountry] = useState("Amsterdam");
    const [isLoading, setIsLoading] = useState(false);
    const appGlobalState = useSelector((state: any)=>state.weatherReducer);
    const {selectedBaseTime} = appGlobalState;
    
    const fetch_metrics = async(countryName:string,baseTime:number)=>{
        setIsLoading(true);
        try {
            const tempMetrics = await fetchTempMetrics(countryName,baseTime);
            const metricKeyLength = Object.keys(tempMetrics.cerrora.forecast_time).length
            const dataPoints = []
            console.log(tempMetrics.ground_truth)
            console.log(tempMetrics.cerrora.forecast_time)
            for(let i = 0; i < metricKeyLength; i++){
                const tempPoint = {
                    time: tempMetrics.ground_truth.forecast_time[i].replace("T"," "),
                    Ground_Truth: kelvinToCelsius(tempMetrics.ground_truth.temperature_2m[i]),
                    Cerrora: kelvinToCelsius(tempMetrics.cerrora.temperature_2m[i]),
                    graphcast: kelvinToCelsius(tempMetrics.graphcast.temperature_2m[i]),
                };
                dataPoints.push(tempPoint);
            }
            setWeatherMetrics(dataPoints);
        } catch (error) {
            console.error('Error fetching metrics:', error);
        } finally {
            setIsLoading(false);
        }
    }
    
    useEffect(() => {
        fetch_metrics(country,selectedBaseTime);
    },[])

    const onCountryChange = async (val: string)=>{
        console.log(val)
        setCountry(val)
        await fetch_metrics(val,selectedBaseTime);
    }
    
    // Custom tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="glass-panel rounded-lg p-3 shadow-hard border border-border/50">
                    <p className="text-xs font-semibold text-foreground mb-2">{label}</p>
                    {payload.map((entry: any, index: number) => (
                        <p key={index} className="text-xs" style={{ color: entry.color }}>
                            {entry.name}: {entry.value.toFixed(2)}°C
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };
    
    return (
        <div className="space-y-6">
            {/* Header with Country Selector */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h3 className="text-base font-semibold">Temperature Forecast Comparison</h3>
                    <p className="text-xs text-muted-foreground mt-1">Compare model predictions vs observed data</p>
                </div>
                
                <div className="flex items-center gap-2 w-full sm:w-auto">
                    <MapPin className="h-4 w-4 text-muted-foreground shrink-0" />
                    <Select value={country} onValueChange={onCountryChange}>
                        <SelectTrigger className="w-full sm:w-[200px] modern-focus">
                            <SelectValue placeholder="Select a country" />
                        </SelectTrigger>
                        <SelectContent className="max-h-72">
                            {EUROPEAN_COUNTRIES.map((country) => (
                                <SelectItem key={country} value={country}>
                                    {country}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Chart Container */}
            <div className="w-full h-[300px] sm:h-[350px] lg:h-[400px]">
                {isLoading ? (
                    <div className="flex items-center justify-center h-full">
                        <p className="text-sm text-muted-foreground">Loading chart data...</p>
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart 
                            data={weatherMetrics} 
                            margin={{ top: 10, right: 10, left: 0, bottom: 20 }}
                        >
                            <CartesianGrid 
                                stroke="hsl(var(--border))" 
                                strokeDasharray="3 3" 
                                opacity={0.3}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="Ground_Truth" 
                                stroke="hsl(221, 83%, 53%)" 
                                strokeWidth={2.5} 
                                name="Ground Truth"
                                dot={{ fill: "hsl(221, 83%, 53%)", r: 3 }}
                                activeDot={{ r: 5 }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="Cerrora" 
                                stroke="hsl(142, 76%, 36%)" 
                                strokeWidth={2.5} 
                                name="Cerrora"
                                dot={{ fill: "hsl(142, 76%, 36%)", r: 3 }}
                                activeDot={{ r: 5 }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="graphcast" 
                                stroke="hsl(0, 84%, 60%)" 
                                strokeWidth={2.5} 
                                name="GraphCast"
                                dot={{ fill: "hsl(0, 84%, 60%)", r: 3 }}
                                activeDot={{ r: 5 }}
                            />
                            <XAxis 
                                dataKey="time" 
                                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                                stroke="hsl(var(--border))"
                                angle={0}
                                textAnchor="end"
                                height={60}
                            />
                            <YAxis 
                                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                                stroke="hsl(var(--border))"
                                label={{ 
                                    value: 'Temperature (°C)', 
                                    position: 'insideLeft', 
                                    angle: -90,
                                    style: { 
                                        fill: "hsl(var(--muted-foreground))",
                                        fontSize: 12,
                                        fontWeight: 500
                                    }
                                }}
                            />
                            <Legend 
                                wrapperStyle={{
                                    paddingTop: '10px',
                                    fontSize: '12px'
                                }}
                            />
                            <Tooltip content={<CustomTooltip />} />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </div>

            {/* Legend Info */}
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground justify-center sm:justify-start">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span>Ground Truth (Observed)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-600"></div>
                    <span>Cerrora Model</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span>GraphCast Model</span>
                </div>
            </div>
        </div>
    );
};

export default LIneChrt;
