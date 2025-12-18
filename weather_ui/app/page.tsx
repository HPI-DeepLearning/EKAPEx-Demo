"use client"

import { Header } from '@/components/header'
import { WeatherSidebar } from '@/components/weather-sidebar'
import { WeatherMap } from '@/components/weather-map'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {Provider} from "react-redux";
import {store} from "@/lib/rdx/Store";
import {useState} from "react";
import Dashboard from "@/components/ModelComparisonDashboard";

const queryClient = new QueryClient()

export default function Home() {
    const [displayState,setDisplayState] = useState(false)

    const onToggleTrigger = (input:boolean):void=>{
        setDisplayState(input)
    }
  return (
 <Provider store={store}>
    <QueryClientProvider client={queryClient}>
        <div className="flex flex-col h-screen overflow-hidden">
          <Header toggleValue = {displayState}/>
          <div className="flex-1 flex flex-col sm:flex-row overflow-hidden">
              {
                  /*
                    This variable toggleValue is there to control the display to either show the comparing  dashboard
                    or show the inference. It has to change later... if its value is set to true,
                    it means users want to see the dashboard for model comparison otherwise,
                    They want to make inference...
                  */
              }
            <WeatherSidebar toggleDisplay={onToggleTrigger} toggleValue = {displayState} />
            <main className="flex-1 overflow-auto">
                {displayState ?
                    <Dashboard />
                    :
                    <WeatherMap/> }
            </main>
          </div>
        </div>
    </QueryClientProvider>
 </Provider>
  )
}

