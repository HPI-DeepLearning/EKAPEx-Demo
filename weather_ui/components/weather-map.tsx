"use client"

import React, { useEffect, useState, useCallback } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import {useSelector} from "react-redux"
import {MoonLoader} from "react-spinners";
import {fetchRandomImage} from "@/lib/api-client";

interface WeatherImage {
    timestamp: string  // Format: "baseTime_validTime"
    url: string
    exists?: boolean
}

interface WeatherData {
    images: WeatherImage[]
    selectedValidTime?: string
    baseTime?: string
}

// Update the getAbsoluteUrl function to better handle weather image URLs
function getAbsoluteUrl(relativeUrl: string) {
    //console.log('Getting absolute URL for:', relativeUrl);
    // If it's already an absolute URL, return it as is
    if (relativeUrl.startsWith('http')) {
        return relativeUrl;
    }

    // Remove any leading slashes from the relative URL
    const cleanRelativeUrl = relativeUrl.replace(/^\/+/, '');

    // Use the environment variable for the image base URL
    const backendUrl = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;

    if (!backendUrl) {
        console.warn('NEXT_PUBLIC_IMAGE_BASE_URL is not defined');
        return relativeUrl;
    }

    // Remove any trailing slashes from the backend URL
    const cleanBackendUrl = backendUrl.replace(/\/+$/, '');

    // Construct and return the full URL
    const fullUrl = `${cleanBackendUrl}/${cleanRelativeUrl}`;
    console.log('Constructed full URL:', fullUrl);
    return fullUrl;
}

// Add type safety for custom events
interface ValidTimeSelectEvent extends CustomEvent {
    detail: { validTime: string };
}

interface WeatherFrameSelectEvent extends CustomEvent {
    detail: { timestamp: string };
}

export function WeatherMap() {
    //console.log('WeatherMap component rendered');
    const [images, setImages] = useState<WeatherImage[]>([])
    const [currentIndex, setCurrentIndex] = useState(0)
    const [isPlaying, setIsPlaying] = useState(false)
    const [playbackSpeed, setPlaybackSpeed] = useState(500)
    const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({})
    const [imageErrors, setImageErrors] = useState<Record<string, number>>({})
    const [mounted, setMounted] = useState(false)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [initRandomImagePath,setInitRandomImagePath] = useState("");
    const [imageLoadErrors, setImageLoadErrors] = useState<Record<string, boolean>>({})

    const BACKEND_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;

    const { toast } = useToast()

    const weatherState:boolean = useSelector((state)=>state.weatherReducer.loadingState)
    const appGlobalState = useSelector((state)=>state.weatherReducer);
    const {app_model,modelSwitchVariable} = appGlobalState;


    const fetchImage = async()=>{
        const urlInferencedPath: string = await fetchRandomImage(app_model,modelSwitchVariable);
        setInitRandomImagePath(urlInferencedPath)
    }
    useEffect(() => {
        fetchImage()

    }, [initRandomImagePath]);

    useEffect(() => {
        setMounted(true)
    }, [])

    const MAX_RETRIES = 3
    const RETRY_DELAY = 2000 // 2 seconds

    // Handle image errors in useEffect
    useEffect(() => {
        const errorUrls = Object.entries(imageLoadErrors)
            .filter(([_, hasError]) => hasError)
            .map(([url]) => url)

        if (errorUrls.length > 0) {
            toast({
                title: "Image Load Error",
                description: "Failed to load weather image. Please try refreshing the page.",
                variant: "destructive",
            })
            // Clear the errors after showing toast
            setImageLoadErrors({})
        }
    }, [imageLoadErrors, toast])

    const handleImageError = useCallback((url: string) => {
        setImageErrors(prev => {
            const retryCount = (prev[url] || 0) + 1
            if (retryCount <= MAX_RETRIES) {
                setTimeout(() => {
                    setLoadingStates(prev => ({ ...prev, [url]: false }))
                }, RETRY_DELAY)
                return { ...prev, [url]: retryCount }
            } else {
                setImageLoadErrors(prev => ({ ...prev, [url]: true }))
                return prev
            }
        })
    }, [])

    // Animation loop using requestAnimationFrame for smoother playback
    useEffect(() => {
        if (!mounted) return;
        let animationFrameId: number;
        let lastUpdate = 0;

        const animate = (timestamp: number) => {
            if (!lastUpdate) lastUpdate = timestamp;

            const elapsed = timestamp - lastUpdate;

            if (elapsed >= playbackSpeed) {
                setCurrentIndex(prevIndex => {
                    if (prevIndex === images.length - 1) {
                        setIsPlaying(false);
                        return prevIndex;
                    }
                    return prevIndex + 1;
                });
                lastUpdate = timestamp;
            }

            if (isPlaying) {
                animationFrameId = requestAnimationFrame(animate);
            }
        };

        if (isPlaying && images.length > 0) {
            animationFrameId = requestAnimationFrame(animate);
        }

        return () => {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
        };
    }, [isPlaying, images.length, playbackSpeed, mounted]);

    // Update weather data handling
    useEffect(() => {
        if (!mounted) return;
        //console.log('Setting up weatherDataUpdate listener');

        const handleWeatherDataUpdate = (event: CustomEvent<WeatherData>) => {
            console.log('WeatherDataUpdate event received:', event.detail);
            try {
                if (event.detail.images && event.detail.images.length > 0) {
                    console.log('Processing images:', event.detail.images);
                    // Process images
                    const processedImages = event.detail.images.map(img => ({
                        ...img,
                        url: img.url.startsWith('/') ? img.url.slice(1) : img.url,
                        exists: true
                    }));

                    console.log('Processed images:', processedImages);

                    // Initialize loading states for all images
                    const initialLoadingStates = processedImages.reduce((acc, img) => {
                        const absoluteUrl = getAbsoluteUrl(img.url);
                        acc[absoluteUrl] = false;
                        console.log('Setting initial loading state for:', absoluteUrl);
                        return acc;
                    }, {} as Record<string, boolean>);

                    setLoadingStates(initialLoadingStates);
                    setImages(processedImages);
                    setCurrentIndex(0);
                    setIsAnalyzing(true);
                }
            } catch (error) {
                console.error('Error in weather data update:', error);
                setIsAnalyzing(false);
            }
        };

        window.addEventListener('weatherDataUpdate', handleWeatherDataUpdate as EventListener);
        return () => {
            window.removeEventListener('weatherDataUpdate', handleWeatherDataUpdate as EventListener);
        };
    }, [mounted]);

    // Update valid time selection handling
    useEffect(() => {
        if (!mounted) return;

        const handleValidTimeSelect = (event: ValidTimeSelectEvent) => {
            try {
                const selectedValidTime = event.detail.validTime;
                const index = images.findIndex(img => img.timestamp.split('_')[1] === selectedValidTime);

                if (index !== -1) {
                    if (!images[index].exists) {
                        toast({
                            title: "Frame Unavailable",
                            description: "The selected frame is not available.",
                            variant: "destructive",
                        });
                        return;
                    }

                    setCurrentIndex(index);
                    setIsPlaying(false);

                    // Get absolute URL for the image
                    const imageUrl = getAbsoluteUrl(images[index].url);

                    // Only set analyzing state if image isn't already loaded
                    if (!loadingStates[imageUrl]) {
                        setIsAnalyzing(true);
                        setLoadingStates(prev => ({ ...prev, [imageUrl]: false }));
                    }
                } else {
                    toast({
                        title: "Invalid Selection",
                        description: "The selected time frame is not available.",
                        variant: "destructive",
                    });
                }
            } catch (error) {
                console.warn('Error handling valid time select:', error);
                setIsAnalyzing(false);
            }
        };

        window.addEventListener('validTimeSelect', handleValidTimeSelect as EventListener);
        return () => {
            window.removeEventListener('validTimeSelect', handleValidTimeSelect as EventListener);
        };
    }, [images, loadingStates, mounted, toast]);

    // Update preload images handling with better state management
    useEffect(() => {
        if (!mounted || !images.length) return;

        let isMounted = true;
        let processedCount = 0;
        let successCount = 0;
        let failedCount = 0;
        const totalImages = images.length;

        const checkAllImagesProcessed = () => {
            console.log(`Images processed: ${processedCount}/${totalImages} (success: ${successCount}, failed: ${failedCount})`);
            if (processedCount >= totalImages && isMounted) {
                console.log('All images processed, stopping analysis state');
                setIsAnalyzing(false);
                
                // Only show success toast if most images loaded successfully
                if (successCount > 0 && successCount > failedCount) {
                    toast({
                        title: "Ready to play",
                        description: `${successCount} of ${totalImages} frames loaded`,
                        duration: 2000,
                    });
                } else if (failedCount > 0) {
                    toast({
                        title: "Connection Issues",
                        description: "Unable to load forecast images. Please check your backend server.",
                        variant: "destructive",
                        duration: 3000,
                    });
                }
            }
        };

        const handleImageLoaded = (imageUrl: string) => {
            if (!isMounted) return;
            console.log('Image loaded successfully:', imageUrl);
            setLoadingStates(prev => ({ ...prev, [imageUrl]: true }));
            processedCount++;
            successCount++;
            checkAllImagesProcessed();
        };

        const handleImageFailed = (imageUrl: string) => {
            if (!isMounted) return;
            console.log('Image failed to load:', imageUrl);
            // Mark as "loaded" (even though it failed) so the overlay doesn't get stuck
            setLoadingStates(prev => ({ ...prev, [imageUrl]: true }));
            processedCount++;
            failedCount++;
            checkAllImagesProcessed();
        };

        // Preload all images
        images.forEach(image => {
            const imageUrl = getAbsoluteUrl(image.url);
            const img = new (window.Image as any)();

            img.onload = () => handleImageLoaded(imageUrl);
            img.onerror = () => handleImageFailed(imageUrl);

            img.src = imageUrl;
        });

        // Safety timeout - stop analyzing after 5 seconds regardless
        const timeoutId = setTimeout(() => {
            if (isMounted) {
                console.log('Timeout reached, forcing stop of analysis state');
                setIsAnalyzing(false);
                // Mark all remaining images as processed
                images.forEach(image => {
                    const imageUrl = getAbsoluteUrl(image.url);
                    setLoadingStates(prev => ({ ...prev, [imageUrl]: true }));
                });
            }
        }, 5000);

        return () => {
            isMounted = false;
            clearTimeout(timeoutId);
        };
    }, [images, toast, handleImageError, mounted]);

    // Add safe event dispatch helper
    const safeDispatchEvent = useCallback((eventName: string, detail: any) => {
        try {
            const event = new CustomEvent(eventName, { detail });
            window.dispatchEvent(event);
        } catch (error) {
            console.warn(`Failed to dispatch ${eventName} event:`, error);
        }
    }, []);

    // Update valid time in sidebar when current index changes
    useEffect(() => {
        if (!mounted || !images[currentIndex]) return;

        safeDispatchEvent('weatherFrameSelect', {
            timestamp: images[currentIndex].timestamp
        });
    }, [currentIndex, images, mounted, safeDispatchEvent]);

    const handlePlayPause = () => {
        if (!isPlaying && currentIndex === images.length - 1) {
            // If at the end, restart from beginning when playing
            setCurrentIndex(0);
        }
        setIsPlaying(prev => !prev);
    };

    const handlePrevFrame = () => {
        setCurrentIndex(prev => Math.max(0, prev - 1));
        setIsPlaying(false);
    };

    const handleNextFrame = () => {
        setCurrentIndex(prev => Math.min(images.length - 1, prev + 1));
        setIsPlaying(false);
    };

    const handleSliderChange = useCallback((value: number[]) => {
        if (!images.length) return;

        const newIndex = Math.min(Math.max(0, value[0]), images.length - 1);
        setCurrentIndex(newIndex);
        setIsPlaying(false);

        if (images[newIndex]) {
            safeDispatchEvent('weatherFrameSelect', {
                timestamp: images[newIndex].timestamp
            });
        }
    }, [images, safeDispatchEvent]);

    // Update the image loading handler
    const handleImageLoad = useCallback((imageUrl: string) => {
        setLoadingStates(prev => ({ ...prev, [imageUrl]: true }));
    }, []);

    // Modify the render condition for the loading overlay
    const isCurrentImageLoading = useCallback(() => {
        if (!images[currentIndex]) {
            return false;
        }
        const currentImageUrl = getAbsoluteUrl(images[currentIndex].url);
        const isLoaded = loadingStates[currentImageUrl] === true;
        console.log(`Current image (${currentIndex}): ${isLoaded ? 'loaded' : 'loading'} - ${currentImageUrl}`);
        return !isLoaded;
    }, [images, currentIndex, loadingStates]);

    useEffect(() => {
        const shouldShowOverlay = isAnalyzing || isCurrentImageLoading();
        console.log('=== Overlay State ===');
        console.log('isAnalyzing:', isAnalyzing);
        console.log('isCurrentImageLoading():', isCurrentImageLoading());
        console.log('SHOWING OVERLAY:', shouldShowOverlay);
        console.log('currentIndex:', currentIndex);
        console.log('Total images:', images.length);
        console.log('====================');
    }, [isAnalyzing, loadingStates, currentIndex, images, isCurrentImageLoading]);

    // Don't render anything until mounted
    if (!mounted) {
        return null;
    }


    return (
        <div className="h-full w-full flex flex-col bg-gradient-to-br from-background via-muted/20 to-background">
            {
                weatherState ? (
                    <div className="flex items-center justify-center h-full min-h-[400px] sm:min-h-[600px]">
                        <div className="flex flex-col items-center gap-4">
                            <MoonLoader
                                color="hsl(var(--primary))"
                                size={64} />
                            <p className="text-xs sm:text-sm text-muted-foreground font-medium">Loading forecast data...</p>
                        </div>
                    </div>
                ): (
                    <>
                        <div className="relative flex-1 p-3 sm:p-4 lg:p-6">
                            {images.length > 0 ? (
                                <>
                                    <div className="relative w-full h-full rounded-2xl overflow-hidden bg-card border border-border shadow-medium">
                                        {images.map((image, index) => {
                                            const imageUrl = getAbsoluteUrl(image.url);
                                            return (
                                                <Image
                                                    key={image.url}
                                                    src={imageUrl}
                                                    alt={`Weather Map Frame ${index + 1}`}
                                                    fill
                                                    priority={index === currentIndex}
                                                    sizes="100vw"
                                                    style={{
                                                        objectFit: 'contain',
                                                        opacity: index === currentIndex ? 1 : 0,
                                                        transition: 'opacity 0.3s ease-in-out',
                                                        pointerEvents: index === currentIndex ? 'auto' : 'none'
                                                    }}
                                                    unoptimized
                                                    onLoad={() => handleImageLoad(imageUrl)}
                                                    onError={() => handleImageError(imageUrl)}
                                                />
                                            );
                                        })}
                                    </div>
                                    {(isAnalyzing || isCurrentImageLoading()) && (
                                        <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-background/90 backdrop-blur-sm rounded-2xl">
                                            <div className="animate-spin rounded-full h-10 w-10 border-3 border-primary border-t-transparent"></div>
                                            <p className="text-base font-semibold text-foreground">Analyzing forecast data...</p>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="relative w-full h-full rounded-2xl overflow-hidden bg-card border border-border shadow-medium">
                                    {initRandomImagePath === "" ? (
                                        <div className="flex items-center justify-center h-full">
                                            <MoonLoader color="hsl(var(--primary))" size={64} />
                                        </div>
                                    ) : (
                                        <Image
                                            src={`${BACKEND_URL}${initRandomImagePath}`}
                                            alt={`Weather Map Frame `}
                                            fill
                                            sizes="100vw"
                                            style={{
                                                objectFit: 'contain',
                                                opacity: 1 ,
                                                transition: 'opacity 0.3s ease-in-out',
                                                pointerEvents: 'none'
                                            }}
                                            unoptimized
                                        />
                                    )}
                                </div>
                            )}
                        </div>

                        {images.length > 0 && (
                            <div className="glass-panel rounded-xl sm:rounded-2xl p-3 sm:p-4 lg:p-6 mx-2 sm:mx-3 lg:mx-4 mb-2 sm:mb-3 lg:mb-4">
                                {/* Playback Controls */}
                                <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4 lg:gap-6 mb-4 sm:mb-5 lg:mb-6">
                                    {/* Navigation Controls */}
                                    <div className="flex items-center gap-1.5 sm:gap-2">
                                        <Button
                                            variant="outline"
                                            size="icon"
                                            onClick={handlePrevFrame}
                                            disabled={currentIndex === 0}
                                            className="h-9 w-9 sm:h-10 sm:w-10 rounded-xl hover:bg-primary/10 hover:border-primary smooth-transition disabled:opacity-30"
                                        >
                                            <SkipBack className="h-3.5 w-3.5 sm:h-4 sm:w-4"/>
                                        </Button>

                                        <Button
                                            size="icon"
                                            onClick={handlePlayPause}
                                            disabled={images.length <= 1}
                                            className="h-11 w-11 sm:h-12 sm:w-12 rounded-xl shadow-medium hover:shadow-hard smooth-transition disabled:opacity-30"
                                        >
                                            {isPlaying ? (
                                                <Pause className="h-4.5 w-4.5 sm:h-5 sm:w-5"/>
                                            ) : (
                                                <Play className="h-4.5 w-4.5 sm:h-5 sm:w-5 ml-0.5"/>
                                            )}
                                        </Button>

                                        <Button
                                            variant="outline"
                                            size="icon"
                                            onClick={handleNextFrame}
                                            disabled={currentIndex === images.length - 1}
                                            className="h-9 w-9 sm:h-10 sm:w-10 rounded-xl hover:bg-primary/10 hover:border-primary smooth-transition disabled:opacity-30"
                                        >
                                            <SkipForward className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                                        </Button>
                                    </div>

                                    {/* Frame Counter */}
                                    <div className="flex-1 text-center order-first sm:order-none">
                                        <div className="text-xs sm:text-sm font-semibold text-foreground">
                                            Frame {currentIndex + 1} <span className="text-muted-foreground">of</span> {images.length}
                                        </div>
                                    </div>

                                    {/* Speed Control */}
                                    <div className="flex items-center gap-1.5 sm:gap-2">
                                        <span className="text-xs font-medium text-muted-foreground hidden md:inline">Speed</span>
                                        <select
                                            className="px-2 sm:px-3 py-1.5 sm:py-2 rounded-xl border border-border bg-background text-xs sm:text-sm font-medium hover:border-primary focus:border-primary focus:ring-2 focus:ring-primary/20 smooth-transition outline-none"
                                            value={playbackSpeed}
                                            onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                                        >
                                            <option value={1000}>1x</option>
                                            <option value={500}>2x</option>
                                            <option value={250}>4x</option>
                                            <option value={125}>8x</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Timeline Slider */}
                                <div className="space-y-2 sm:space-y-3">
                                    <Slider
                                        value={[currentIndex]}
                                        min={0}
                                        max={Math.max(0, images.length - 1)}
                                        step={1}
                                        onValueChange={handleSliderChange}
                                        className="w-full"
                                    />

                                    {/* Timestamp Display */}
                                    <div className="text-center text-xs text-muted-foreground leading-relaxed">
                                        {images[currentIndex] && (
                                            <div className="flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-2">
                                                {images[currentIndex].timestamp.split('_').map((ts, i) => {
                                                    const date = new Date(parseInt(ts) * 1000);
                                                    const formattedDate = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')} ${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')} UTC`;
                                                    return (
                                                        <React.Fragment key={i}>
                                                            {i > 0 && <span className="text-primary hidden sm:inline">→</span>}
                                                            <span className="font-mono text-xs">{formattedDate}</span>
                                                        </React.Fragment>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                )
            }
        </div>
    );
}

