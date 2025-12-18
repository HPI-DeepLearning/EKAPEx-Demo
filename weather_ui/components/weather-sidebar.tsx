"use client"

import React, {useState, useEffect, useCallback, useMemo, JSX} from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import {fetchBaseTimes, fetchFiles, fetchValidTimes, fetchWeatherData} from '@/lib/api-client'
import { useQuery } from '@tanstack/react-query'
import extremeEvents from '@/extreme_events_dataset.json'
import { Calendar, Clock, Layers, Zap, AlertTriangle, X, ArrowLeftRight } from 'lucide-react'

import {useDispatch, useSelector} from "react-redux";
import {
    updateAppModel,
    updateBaseTimeChanged,
    updateImageList,
    updateLoadingDone,
    updateLoadingStart, updateModelSwitchVariable,
    updateSelectedVariable, updateValidTime, updateValidTimeList
} from "@/lib/rdx/WeatherSlice";
import {VARIABLE_TYPES} from "@/lib/utils";
import {
  ExtremeEvent, fileOptions,
  TimeOption,
  typedExtremeEvents,
  ValidTimeUpdateEvent,
  WeatherData
} from "@/app/Utilities/ApplicationInterfaces";
import {timeValidator} from "@/app/Utilities/Utilities";
import {Value} from "@radix-ui/react-select";


export function WeatherSidebar({toggleDisplay,toggleValue,onDisplayChangedImg}):JSX.Element {
  const [baseTime, setBaseTime] = useState<string>('')
  const [validTime, setValidTime] = useState<string>('')

  const [selectedVariable, setSelectedVariable] =useState("sea_level") // useState('temp_wind')

  const [selectedEventType, setSelectedEventType] = useState<string>('')
  const [selectedEvent, setSelectedEvent] = useState<string>('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [queryTime, setQueryTime] = useState<string | undefined>(undefined)
  const [selectedModel,setSelectedModel] = useState<string>("")
  const [selectedEventDetails, setSelectedEventDetails] = useState<ExtremeEvent | null>(null)
  const [loading,setLoading] = useState<boolean>(false);
  const [onFirstLoad,setOnFirstLoad] = useState<boolean>(true)

  const dispatcher = useDispatch();
  const appGlobalState = useSelector((state)=>state.weatherReducer);
  const {selectedBaseTime,app_model,selectedValidTime,currentSelectedVariable} = appGlobalState;

  const weatherState:boolean = useSelector((state)=>state.weatherReducer.loadingState)

  const formatTime = useCallback((timestamp: string | undefined) => {
      return timeValidator(timestamp)
  }, []);

  // Add safe event dispatch helper
  const safeDispatchEvent = useCallback((eventName: string, detail: any) => {
    if (typeof window === 'undefined') return;
    try {
      const event = new CustomEvent(eventName, { detail });
      window.dispatchEvent(event);
    } catch (error) {
      console.warn(`Failed to dispatch ${eventName} event:`, error);
    }
  }, []);

  // Get unique event types
  const eventTypes = Array.from(
    new Set(
      Object.values(typedExtremeEvents).flatMap(event => event.type)
    )
  ).sort()

  // Get events for selected type
  const eventsForType = Object.entries(typedExtremeEvents)
    .filter(([_, event]) => event.type.includes(selectedEventType))
    .sort((a, b) => b[1].year - a[1].year) // Sort by year descending

  // Fetch base times based on selected variable and query time
  const { data: baseTimes = [], refetch: refetchBaseTimes } = useQuery<TimeOption[]>({
    queryKey: ['baseTimes', selectedVariable, queryTime],
    queryFn: async () => {
      try {
          let currentModelValue = app_model;
          if(!onFirstLoad){
              console.log("I here onFirstLoad>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
              if(currentModelValue ==="cerrora"){
                  currentModelValue = "graphcast"
              }
              else{
                  currentModelValue = "cerrora"
              }
          }else{
              setOnFirstLoad(false);
          }
          const data = await fetchBaseTimes(selectedVariable,currentModelValue);
        return data;
      } catch (error) {
          console.error('Error fetching base times:', error);
        return [];
      }
    }
  });

  // Fetch valid times when base time changes
  const { data: validTimes = [], refetch: refetchValidTimes,isLoading,
    error } = useQuery<TimeOption[], Error>({
    queryKey: ['validTimes', baseTime, selectedVariable],
    queryFn: async () => {
      if (!baseTime || !selectedVariable) return [];

      return fetchValidTimes(app_model,selectedVariable, parseInt(baseTime));
    },
    enabled: !!baseTime && !!selectedVariable
  });

  // Fetch weather data when valid times are available
  const { data: weatherData,isFetching } = useQuery<WeatherData | null>({
    queryKey: ['weatherData', selectedVariable, baseTime, validTimes],
    queryFn: async () => {
      if (!validTimes.length || !baseTime) return null;

      const validTimeValues = validTimes.map(vt => parseInt(vt.value));
      dispatcher(updateValidTimeList(validTimeValues))

      const data = await fetchWeatherData(app_model,`data/${selectedVariable}`, {
        baseTime: parseInt(baseTime),
        validTime: validTimeValues
      });

      if (data?.images) {
          console.log(`VALID TIMES ❌❌ ${validTimeValues}`)
          console.log(`VALID TIMES✅ ${validTime}`)
        safeDispatchEvent('weatherDataUpdate', {
          ...data,
          selectedValidTime: validTime || validTimeValues[0].toString()
        });
      }
      return data;
    },
    enabled: validTimes.length > 0 && !!selectedVariable && !!baseTime
  });

  // Set initial valid time when valid times change
  useEffect(() => {
    if (validTimes.length > 0 && !validTime) {
      const firstValidTime = validTimes[0].value;
      setValidTime(firstValidTime);
      safeDispatchEvent('validTimeSelect', { validTime: firstValidTime });
    }
  }, [validTimes, validTime, safeDispatchEvent]);

  // Simplify event selection handler
  const handleEventSelect = useCallback((eventId: string) => {
    setSelectedEvent(eventId);
    const event = typedExtremeEvents[eventId];
    if (event) {
      setSelectedEventDetails(event);
      const startTimestamp = Math.floor(new Date(event.start_time).getTime() / 1000).toString();
      setBaseTime(startTimestamp);
      setValidTime(startTimestamp); // Set valid time immediately to match event start
      safeDispatchEvent('validTimeSelect', { validTime: startTimestamp });
    }
  }, [safeDispatchEvent]);

  // Clear event selection and reset filters
  const clearEventSelection = useCallback(() => {
    setSelectedEvent('');
    setSelectedEventType('');
    setSelectedEventDetails(null);
    setQueryTime(undefined);
    setBaseTime('');
    setValidTime('');
    refetchBaseTimes();
  }, [refetchBaseTimes]);

  // Handle event selection confirmation
  const handleEventConfirm = useCallback(() => {
    setDialogOpen(false);
    if (selectedEventDetails) {
      // No need for complex time calculations - just use the event times directly
      refetchValidTimes();
    }
  }, [selectedEventDetails, refetchValidTimes]);

  // Handle valid time selection
  const handleValidTimeSelect = useCallback((value: string) => {

      setValidTime(value);
      // Notify the map component to update the displayed frame
      safeDispatchEvent('validTimeSelect', { validTime: value });
  }, [safeDispatchEvent]);

  // Listen for valid time updates from weather map
  useEffect(() => {
    window.addEventListener("modelChange",(event)=>{
      console.log("☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️☕️️️️️️☕️onModelChange", event);
      const currentModel = event.detail.model;
      setSelectedModel(currentModel)
        dispatcher(updateAppModel(currentModel))
      refetchBaseTimes()
    })
    const handleValidTimeUpdate = (event: ValidTimeUpdateEvent) => {
      try {
        setValidTime(event.detail.validTime);
      } catch (error) {
        console.warn('Error handling valid time update:', error);
      }
    };
    window.addEventListener('validTimeUpdate', handleValidTimeUpdate as EventListener);
    return () => {
      window.removeEventListener('validTimeUpdate', handleValidTimeUpdate as EventListener);
    };
  }, []);

  // Helper function to format locations
  const formatLocations = useCallback((locations: string[], limit: number = 3) => {
    if (locations.length <= limit) {
      return locations.join(', ');
    }
    return `${locations.slice(0, limit).join(', ')} +${locations.length - limit} more`;
  }, []);

  useEffect(() => {
    if (loading) {
      dispatcher(updateLoadingStart(true));
    }else{
      dispatcher(updateLoadingDone(false))
    }
  }, [loading]);

  useEffect(() => {
    if (isLoading || isFetching) {
      setLoading(true);
    } else {
      setLoading(false);
    }
  }, [isLoading, isFetching]);

  const forecastVariables = [VARIABLE_TYPES.DESCRIPTION,VARIABLE_TYPES.GEOPOTENTIAL,VARIABLE_TYPES.SEALEVELPRESSURE,VARIABLE_TYPES.TEMPWIND];
  const [selectedForecastVariable, setSelectedForecastVariable] = useState<string>(VARIABLE_TYPES.DESCRIPTION)

  const onChangeVariable = async (model_variable: string) => {

      if(model_variable !== VARIABLE_TYPES.DESCRIPTION){

        let selectedModelVariable = "";
        switch (model_variable) {
            case "geo":
                selectedModelVariable = "geopotential";
                //setSelectedVariable("geo")
                break;
            case "temp_wind":
                selectedModelVariable = "tempWind";
                //setSelectedVariable("temp_wind")
                break;
            case "sea_level":
                selectedModelVariable = "seaLevelPressure";
                //setSelectedVariable("sea_level")
                break;
            default:
                selectedModelVariable = "rain";
        }
      setSelectedForecastVariable(model_variable)

        setSelectedVariable(model_variable)

      dispatcher(updateSelectedVariable(selectedModelVariable))



        if(selectedBaseTime != -320){
            const fileParams:fileOptions = {
                variable:model_variable,
                baseTime:selectedBaseTime,
                modelType: app_model
            }

            console.log("FILE_PARAMS_VALUE FROM ONCHANGEVARIABLE() FUNCTION 🚨🚨🚨🚨🚨🚨🚨🚨",fileParams)
            const data = await fetchFiles(fileParams);
            const cerrora_img_list = data[0];
            const graphcast_img_list = data[2];
            const ground_truth_img_list = data[4];
            dispatcher(updateImageList({cerrora_img_list,graphcast_img_list,ground_truth_img_list}))

        }


    }
  }

  const onBaseTimeChange = async(value:string):void=>{

      dispatcher(updateBaseTimeChanged(value))
      if(toggleValue){
      // NOw in Compare mode----
      setBaseTime(value);

      const fileParams:fileOptions = {
        variable:selectedVariable,
        baseTime:parseInt(value),
          modelType: app_model
      }
      console.log("FILE_PARAMS_VALUE FROM ONCHANGEBASETIME() FUNCTION 🚨🚨🚨🚨🚨🚨🚨🚨",fileParams)
      try {
          const data = await fetchFiles(fileParams);
          const cerrora_img_list = data[0];
          const graphcast_img_list = data[2];
          const ground_truth_img_list = data[4];
          dispatcher(updateImageList({cerrora_img_list,graphcast_img_list,ground_truth_img_list}))
      }catch (e) {
          console.log(e)
      }
    }
    else{
      // NOw in Inference mode
      setBaseTime(value);
      setValidTime(''); // Reset valid time when base time changes
    }

  }

  const onValidTimeChange = (value:string):void=>{
    toggleValue ? dispatcher(updateValidTime(value)) : handleValidTimeSelect(value);
  }
  // INtegration...
  return (
      <aside className="w-full sm:w-72 lg:w-80 border-r border-border/40 bg-muted/30 custom-scrollbar overflow-y-auto" suppressHydrationWarning>
        <div className="p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-5 lg:space-y-6">
          
          {/* Page Title */}
          <div>
            <h2 className="text-lg sm:text-xl font-semibold tracking-tight">Forecast Controls</h2>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">Configure visualization parameters</p>
          </div>

          {/* Selected Event Card */}
          {selectedEventDetails && (
              <div className="modern-card p-4 animate-in border-l-4 border-l-primary">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-primary" />
                    <h4 className="font-semibold text-sm">Active Event</h4>
                  </div>
                  <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearEventSelection}
                      className="h-7 w-7 p-0 hover:bg-destructive/10 hover:text-destructive"
                  >
                    <X className="h-3.5 w-3.5" />
                  </Button>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium text-foreground break-words">
                    📍 {selectedEventDetails.location.join(', ')}
                  </div>
                  <p className="text-xs text-muted-foreground break-words leading-relaxed">
                    {selectedEventDetails.description}
                  </p>
                  <div className="pt-2 mt-2 border-t border-border/50 space-y-1 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Clock className="h-3 w-3" />
                      <span>Start: {formatTime(selectedEventDetails.start_time)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-3 w-3" />
                      <span>End: {formatTime(selectedEventDetails.end_time)}</span>
                    </div>
                  </div>
                </div>
              </div>
          )}

          {/* Base Time Selector */}
          <div className="modern-card p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-primary" />
              <label className="text-sm font-semibold">Base Time</label>
            </div>
            <Select
                onOpenChange={() => {
                  //toggleDisplay(false)
                }}
                value={baseTime}
                onValueChange={(value) => {
                  onBaseTimeChange(value)
                }}
                disabled={!!selectedEventDetails || weatherState}
            >
              <SelectTrigger className="w-full h-10 modern-focus">
                <SelectValue placeholder="Select base time">
                  {baseTime && formatTime(baseTime)}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {baseTimes?.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label || formatTime(option.value)}
                    </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Valid Time Selector */}
          {(validTimes.length > 0 && !toggleValue) && (
              <div className="modern-card p-4 space-y-3 animate-in">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-primary" />
                  <label className="text-sm font-semibold">Valid Time</label>
                </div>
                <Select
                    onOpenChange={() => {
                     // toggleDisplay(false)
                    }}
                    disabled={weatherState}
                    value={validTime}
                    onValueChange={onValidTimeChange}
                >
                  <SelectTrigger className="w-full h-10 modern-focus">
                    <SelectValue placeholder="Select valid time">
                      {validTime && formatTime(validTime)}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {validTimes.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label || formatTime(option.value)}
                        </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
          )}
          
          {/* Variable Selector */}
          <div className="modern-card p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" />
              <label className="text-sm font-semibold">Weather Variable</label>
            </div>
            {toggleValue ? (
                <Select value={selectedForecastVariable} onValueChange={onChangeVariable}>
                  <SelectTrigger className="w-full h-10 modern-focus">
                    <SelectValue placeholder="Select Model Variable"/>
                  </SelectTrigger>
                  <SelectContent>
                    {forecastVariables.map((variable) => (
                        <SelectItem value={variable} key={variable}>
                          {variable}
                        </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Select
                    onOpenChange={() => {
                      toggleDisplay(false)
                    }}
                    disabled={weatherState} 
                    value={selectedVariable} 
                    onValueChange={(value:string)=>{
                      console.log(value,":: MY VALUE MY VALUE...")
                      dispatcher(updateModelSwitchVariable(value))
                      setSelectedVariable(value)
                    }}
                >
                  <SelectTrigger className="w-full h-10 modern-focus">
                    <SelectValue placeholder="Select a variable"/>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="temp_wind">
                      <div className="flex items-center gap-2">
                        <span>🌡️</span>
                        <span>Temperature & Wind</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="geo">
                      <div className="flex items-center gap-2">
                        <span>📊</span>
                        <span>Geopotential Height</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="sea_level">
                      <div className="flex items-center gap-2">
                        <span>🌊</span>
                        <span>Sea Level Pressure</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              )}
          </div>
          {/* Event Selector */}
          <div className="modern-card p-4 space-y-3">
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="w-full h-10 gap-2 hover:bg-primary/5 hover:border-primary smooth-transition">
                  <Zap className="h-4 w-4" />
                  <span>Select Weather Event</span>
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-primary" />
                    Select Weather Event
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold">Event Type</label>
                    <Select
                        disabled={weatherState}
                        value={selectedEventType}
                        onValueChange={(value) => {
                          setSelectedEventType(value);
                          setSelectedEvent('');
                        }}
                    >
                      <SelectTrigger className="w-full modern-focus">
                        <SelectValue placeholder="Select event type"/>
                      </SelectTrigger>
                      <SelectContent>
                        {eventTypes.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {selectedEventType && (
                      <div className="space-y-2 animate-in">
                        <label className="block text-sm font-semibold">Event</label>
                        <Select
                            value={selectedEvent}
                            onValueChange={handleEventSelect}
                        >
                          <SelectTrigger className="w-full modern-focus">
                            <SelectValue placeholder="Select event"/>
                          </SelectTrigger>
                          <SelectContent>
                            {eventsForType.map(([id, event]) => (
                                <SelectItem key={id} value={id} className="break-all">
                            <span className="inline-flex flex-wrap gap-1">
                              <span className="whitespace-nowrap">{event.start_time}</span>
                              <span className="whitespace-nowrap">-</span>
                              <span className="break-words">{formatLocations(event.location)}</span>
                            </span>
                                </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                  )}

                  {selectedEventDetails && (
                      <div className="mt-4 p-4 rounded-xl bg-muted border border-border animate-in">
                        <h4 className="font-semibold mb-3 flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-primary" />
                          Event Details
                        </h4>
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-foreground break-words">
                            📍 {selectedEventDetails.location.join(', ')}
                          </div>
                          <p className="text-xs text-muted-foreground break-words leading-relaxed">
                            {selectedEventDetails.description}
                          </p>
                          <div className="pt-2 mt-2 border-t border-border/50 space-y-1 text-xs text-muted-foreground">
                            <div className="flex items-center gap-2">
                              <Clock className="h-3 w-3" />
                              <span>Start: {formatTime(selectedEventDetails.start_time)}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Clock className="h-3 w-3" />
                              <span>End: {formatTime(selectedEventDetails.end_time)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                  )}
                </div>
                <DialogFooter className="mt-6">
                  <Button onClick={handleEventConfirm} className="w-full">
                    Confirm Selection
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Mode Toggle Button */}
          <Button 
            onClick={() => {
              toggleDisplay(!toggleValue)
            }} 
            className="w-full h-11 gap-2 font-semibold shadow-soft hover:shadow-medium smooth-transition" 
            variant="default"
          >
            <ArrowLeftRight className="h-4 w-4" />
            {toggleValue ? "Switch to Inference" : "Switch to Comparison"}
          </Button>

        </div>
      </aside>
  )
}

