"use client"
import React, {useState} from 'react';
import ImageInferenceSlider from "@/components/ImageInferenceSlider";
import ImageInferenceSliderGT from "@/components/ImageInferenceSliderGT";
import LIneChrt from "@/components/LIneChrt";
import BarChrt from "@/components/BarChrt";
import ModelMetricsReportCard from "@/components/ModelMetricsReportCard";
import {useSelector} from "react-redux";
import {MoonLoader} from "react-spinners";
import MetricsReporting from "@/components/MetricsReporting";
import { TrendingUp, Target, Activity, Bike, Coffee } from 'lucide-react';

const Dashboard: React.FC = (): React.JSX.Element => {

    const  globalState = useSelector((state: any)=>state.weatherReducer)
    const weatherState:boolean = useSelector((state: any)=>state.weatherReducer.loadingState)

    const {baseTime,validTime,currentSelectedVariable} = globalState

    return (
        <div className="h-full w-full bg-gradient-to-br from-background via-muted/20 to-background overflow-auto">
            {
                weatherState ? (
                    <div className="flex items-center justify-center h-full min-h-[400px] sm:min-h-[600px]">
                        <div className="flex flex-col items-center gap-4">
                            <MoonLoader
                                color="hsl(var(--primary))"
                                size={64}/>
                            <p className="text-xs sm:text-sm text-muted-foreground font-medium">Loading comparison data...</p>
                        </div>
                    </div>
                ) : (
                    <div className="w-full p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8">
                        
                        {/* Header Section */}
                        <div className="space-y-2">
                            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Model Comparison</h1>
                            <p className="text-sm sm:text-base text-muted-foreground">
                                Compare forecast accuracy across AI models and ground truth data
                            </p>
                        </div>

                        {/* Model Comparison Section */}
                        <div className="space-y-4">
                            <h2 className="text-lg sm:text-xl font-semibold tracking-tight flex items-center gap-2">
                                <Target className="h-5 w-5 text-primary" />
                                Visual Comparison
                            </h2>
                            
                            {/* AI Models Comparison */}
                            <div className="modern-card p-4 sm:p-6 space-y-4 animate-in">
                                <div className="flex items-center justify-between flex-wrap gap-2">
                                    <div>
                                        <h3 className="text-base sm:text-lg font-semibold">AI Model Predictions</h3>
                                        <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
                                            Compare GraphCast and Cerrora model outputs
                                        </p>
                                    </div>
                                    <div className="flex gap-2">
                                        <span className="px-2.5 py-1 rounded-full bg-red-500/10 text-red-600 dark:text-red-400 text-xs font-semibold border border-red-500/20">
                                            GraphCast
                                        </span>
                                        <span className="px-2.5 py-1 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 text-xs font-semibold border border-green-500/20">
                                            Cerrora
                                        </span>
                                    </div>
                                </div>
                                <div className="w-full overflow-hidden rounded-xl border border-border bg-muted/30">
                                    <ImageInferenceSlider />
                                </div>
                            </div>

                            {/* Ground Truth */}
                            <div className="modern-card p-4 sm:p-6 space-y-4 animate-in" style={{animationDelay: '0.1s'}}>
                                <div className="flex items-center justify-between flex-wrap gap-2">
                                    <div>
                                        <h3 className="text-base sm:text-lg font-semibold">Ground Truth</h3>
                                        <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
                                            Observed weather data for validation
                                        </p>
                                    </div>
                                    <span className="px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 text-xs font-semibold border border-blue-500/20">
                                        Actual Data
                                    </span>
                                </div>
                                <div className="w-full overflow-hidden rounded-xl border border-border bg-muted/30">
                                    <ImageInferenceSliderGT />
                                </div>
                            </div>
                        </div>

                        {/* Metrics & Chart Section */}
                        <div className="space-y-4">
                            <h2 className="text-lg sm:text-xl font-semibold tracking-tight flex items-center gap-2">
                                <TrendingUp className="h-5 w-5 text-primary" />
                                Performance Metrics
                            </h2>
                            
                            <div className="modern-card p-4 sm:p-6 space-y-6 animate-in">
                                {/* Chart Container */}
                                <div className="w-full">
                                    <LIneChrt />
                                </div>
                            </div>
                        </div>

                        {/* Additional Metrics Section (if needed) */}
                        <div className="space-y-4">
                            <h2 className="text-lg sm:text-xl font-semibold tracking-tight flex items-center gap-2">
                                <Activity className="h-5 w-5 text-primary" />
                                Statistical Analysis
                            </h2>
                            
                            <div className="modern-card p-4 sm:p-6 animate-in">
                                <BarChrt />
                            </div>
                        </div>

                        

                    </div>
                )
            }
        </div>
    );
};

export default Dashboard;
