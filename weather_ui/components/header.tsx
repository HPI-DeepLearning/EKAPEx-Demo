"use client"

import {useCallback, useEffect, useState} from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { MessageSquare, Cloud, FileText, Settings } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { useToast } from '@/hooks/use-toast'
import {useDispatch, useSelector} from "react-redux";
import Link from "next/link";
import {updateAppModel} from "@/lib/rdx/WeatherSlice";
import {fetchWeatherData} from "@/lib/api-client";

interface IHeader{
  toggleValue: boolean
}
export function Header({toggleValue}:IHeader) {
  const [selectedModel, setSelectedModel] = useState('graphcast')
  const { toast } = useToast()
  const dispatcher = useDispatch();
    const weatherState:boolean = useSelector((state: any)=>state.weatherReducer.loadingState)
    const appGlobalState = useSelector((state: any)=>state.weatherReducer);
    const {selectedBaseTime,modelSwitchVariable,app_model,validTimeList} = appGlobalState;

  const checkCurrentModel = async()=>{
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/current-model`);
    const curModel = await response.json();
    setSelectedModel(curModel);
  }

  useEffect(() => {
    checkCurrentModel().then(e=>{})
  }, [selectedModel]);
    const safeDispatchEvent = useCallback((eventName: string, detail: any) => {
        if (typeof window === 'undefined') return;
        try {
            const event = new CustomEvent(eventName, { detail });
            window.dispatchEvent(event);
        } catch (error) {
            console.warn(`Failed to dispatch ${eventName} event:`, error);
        }
    }, []);

  const handleModelChange = async (value: string) => {
        dispatcher(updateAppModel(value))
    try {
        /*
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/switch-model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model_type: value }),
      })

      if (!response.ok) {
        throw new Error('Failed to switch model')
      }
      const data = await response.json();
      console.log(data)
        */
      setSelectedModel(value)

      // Dispatch event to notify other components
      window.dispatchEvent(new CustomEvent('modelChange', { detail: { model: value } }))

      toast({
        title: 'Model Updated',
        description: `Switched to ${value} model successfully`,
      })
        if(selectedBaseTime !== -320 && validTimeList.length > 0){
            const data = await fetchWeatherData(value,`data/${modelSwitchVariable}`, {
                baseTime: parseInt(selectedBaseTime),
                validTime: validTimeList
            });
            console.log(data)

            if (data?.images) {
                safeDispatchEvent('weatherDataUpdate', {
                    ...data,
                    selectedValidTime: validTimeList[0].toString()
                });
            }

        }



    } catch (error) {
      console.error('Error switching model:', error)
      toast({
        title: 'Error',
        description: 'Failed to switch model. Please try again.',
        variant: 'destructive',
      })
    }
  }

  const handleFeedbackClick = () => {
    window.location.href = 'mailto:feedback@weatherapp.com?subject=Weather App Feedback'
  }





  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 sm:h-16 items-center justify-between px-4 sm:px-6 gap-2 sm:gap-4">
        {/* Logo and App Name */}
        <Link href={"/"} className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity shrink-0">
          <div className="flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-br from-primary to-primary/80 shadow-soft">
            <Cloud className="h-4 w-4 sm:h-5 sm:w-5 text-primary-foreground" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-base sm:text-lg font-semibold tracking-tight leading-none">EKAPEx Weather</h1>
            <span className="text-xs text-muted-foreground hidden md:inline">AI-Powered Forecasting</span>
          </div>
        </Link>

        {/* Center - Model Selector (only when not in toggle mode) */}
        <div className="flex-1 flex justify-center min-w-0">
          {!toggleValue && (
            <div className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-muted/50 border border-border/50 max-w-full">
              <Settings className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-muted-foreground shrink-0" />
              <span className="text-xs sm:text-sm font-medium text-muted-foreground hidden lg:inline">Model:</span>
              <Select disabled={weatherState} value={app_model} onValueChange={handleModelChange}>
                <SelectTrigger className="w-[120px] sm:w-[160px] h-7 sm:h-8 text-xs sm:text-sm border-0 bg-transparent shadow-none focus:ring-0 font-medium">
                  <SelectValue placeholder="Select model"/>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="graphcast">GraphCast</SelectItem>
                  <SelectItem value="cerrora">Cerrora</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {/* Right Side - Actions */}
        <div className="flex items-center gap-1 sm:gap-2 shrink-0">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link href={"/api-docs"}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 sm:h-9 gap-1 sm:gap-2 text-muted-foreground hover:text-foreground px-2 sm:px-3"
                  >
                    <FileText className="h-4 w-4"/>
                    <span className="hidden xl:inline text-xs sm:text-sm">API Docs</span>
                  </Button>
                </Link>
              </TooltipTrigger>
              <TooltipContent>
                <p>View API Documentation</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleFeedbackClick}
                    aria-label="Send feedback"
                    className="h-8 sm:h-9 gap-1 sm:gap-2 text-muted-foreground hover:text-foreground px-2 sm:px-3"
                >
                  <MessageSquare className="h-4 w-4"/>
                  <span className="hidden xl:inline text-xs sm:text-sm">Feedback</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Share your feedback with us</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </header>
  )
}

