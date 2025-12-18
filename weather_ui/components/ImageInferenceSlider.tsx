"use client"
import React, {useState, useEffect, useRef, useCallback} from 'react';
import { Play, Pause, SkipForward, SkipBack, RotateCcw } from 'lucide-react';
import ImageZoom from "@/components/ImageZoom";
import {useDispatch, useSelector} from "react-redux";
import {store} from "@/lib/rdx/Store";
import {updateImageIndex} from "@/lib/rdx/WeatherSlice";
import {useImageZoom} from "@/hooks/UseImageZoom";
import {fetchRandomImage} from "@/lib/api-client";
import {encodeURIPath} from "next/dist/shared/lib/encode-uri-path";
import {MoonLoader} from "react-spinners";
const ImageInferenceSlider = () => {
    // http://localhost:8000/backend-fast-api/streaming/graphcast/rain/1578808800_1579046400_image.webp
    const zoomControls = useImageZoom();
    const BACKEND_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;
    const dispatcher = useDispatch();
    const currentImageIndexState = useSelector((state: any)=>state.weatherReducer.currentImageIndex)

    const imageListCerrora = useSelector((state: any)=>state.weatherReducer.cerrora_img_list)
    const imageListGraphcast = useSelector((state: any)=>state.weatherReducer.graphcast_img_list)
    const selectedModelVariable = useSelector((state: any)=> state.weatherReducer.currentSelectedVariable)

    const [box1CurrentIndex, setBox1CurrentIndex] = useState(0);
    const [box2CurrentIndex, setBox2CurrentIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [slideInterval, setSlideInterval] = useState(2000); // 2 seconds default
    const [transitionEffect, setTransitionEffect] = useState('fade'); // 'fade' or 'slide'
    const [isTransitioning, setIsTransitioning] = useState(false);

    const [initCerroraImagePath,setInitCerroraImagePath] = useState("");
    const [initGraphcastImagePath,setInitGraphcastImagePath] = useState("");


    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const fetchImage = async()=>{
        const urlPathCerrora:string = await fetchRandomImage("cerrora", selectedModelVariable);
        const urlPathGraphcast:string = await fetchRandomImage("graphcast", selectedModelVariable);
            setInitCerroraImagePath(urlPathCerrora)
            setInitGraphcastImagePath(urlPathGraphcast)
    }

    useEffect(() => {
        fetchImage()

    }, [initCerroraImagePath,initGraphcastImagePath]);

    const nextImage = () => {
        if (isTransitioning) return;
        setIsTransitioning(true);
        setTimeout(() => {
            setBox1CurrentIndex(prev => (prev + 1) % imageListGraphcast.length);
            setBox2CurrentIndex(prev => (prev + 1) % imageListCerrora.length);
            const latestIndex =  store.getState().weatherReducer.currentImageIndex;
            latestIndex < (imageListGraphcast.length -1) ? dispatcher(updateImageIndex(latestIndex + 1)): dispatcher(updateImageIndex(0))
            setTimeout(() => setIsTransitioning(false), 50);
        },200)
    };

    const prevImage = () => {
        if (isTransitioning) return;
        setIsTransitioning(true);

        setTimeout(() => {
            setBox1CurrentIndex(prev => prev === 0 ? imageListGraphcast.length - 1 : prev - 1);
            setBox2CurrentIndex(prev => prev === 0 ? imageListCerrora.length - 1 : prev - 1);
            dispatcher(updateImageIndex(currentImageIndexState === 0 ? imageListGraphcast.length - 1 : currentImageIndexState - 1))
            setTimeout(() => setIsTransitioning(false), 50);
        }, 200);
    };

    const startSlideshow = () => {
        setIsPlaying(true);
    };

    const pauseSlideshow = () => {
        setIsPlaying(false);
    };

    useEffect(() => {
        if (isPlaying) {
            intervalRef.current = setInterval(nextImage, slideInterval);
        } else {
            if (intervalRef.current) clearInterval(intervalRef.current);
        }

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [isPlaying, slideInterval]);

    useEffect(() => {
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, []);

        //  src={"http://localhost:8000/backend-fast-api/streaming/cerrora/rain/1578204000_1578290400_image.webp"}
    return (
        <div className="w-full p-4">
            {/* Controls */}
            <div className="bg-white p-3 rounded-lg shadow-md mb-4">
                <div className="flex flex-wrap items-center justify-center gap-4">
                    <button
                        onClick={prevImage}
                        className="flex items-center gap-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                    >
                        <SkipBack size={16} />
                        Previous
                    </button>

                    <button
                        onClick={isPlaying ? pauseSlideshow : startSlideshow}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                            isPlaying
                                ? 'bg-red-500 hover:bg-red-600 text-white'
                                : 'bg-green-500 hover:bg-green-600 text-white'
                        }`}
                    >
                        {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                        {isPlaying ? 'Pause' : 'Play'}
                    </button>

                    <button
                        onClick={nextImage}
                        className="flex items-center gap-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                    >
                        Next
                        <SkipForward size={16} />
                    </button>
                </div>
            </div>

            {/* Images Grid - Equal margins on both sides */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                {/* GraphCast Image */}
                <div className="bg-white rounded-lg shadow-lg overflow-hidden w-full">
                    <div className="p-3">
                        <h2 className="text-base font-semibold mb-2">GraphCast</h2>
                        <div className="w-full">
                            {initGraphcastImagePath === "" ? (
                                <div className="flex justify-center items-center h-[400px]">
                                    <MoonLoader color="hsl(var(--primary))" size={64} />
                                </div>
                            ) : (
                                <ImageZoom
                                    src={
                                        imageListGraphcast.length == 0 ? `${BACKEND_URL}${initGraphcastImagePath}`:
                                            `${BACKEND_URL}/${"graphcast"}/${selectedModelVariable}/${imageListGraphcast[currentImageIndexState]}`
                                    }
                                    alt={"GraphCast Prediction"}
                                    title="GraphCast Prediction"
                                    zoomLevel={zoomControls.zoomLevel}
                                    panX={zoomControls.panX}
                                    panY={zoomControls.panY}
                                    isDragging={zoomControls.isDragging}
                                    onWheel={zoomControls.handleWheel}
                                    onMouseDown={zoomControls.handleMouseDown}
                                    onMouseMove={zoomControls.handleMouseMove}
                                    onMouseUp={zoomControls.handleMouseUp}
                                />
                            )}
                        </div>
                    </div>
                </div>

                {/* Cerrora Image */}
                <div className="bg-white rounded-lg shadow-lg overflow-hidden w-full">
                    <div className="p-3">
                        <h2 className="text-base font-semibold mb-2">Cerrora</h2>
                        <div className="w-full">
                            {initCerroraImagePath === "" ? (
                                <div className="flex justify-center items-center h-[400px]">
                                    <MoonLoader color="hsl(var(--primary))" size={64} />
                                </div>
                            ) : (
                                <ImageZoom
                                    src={
                                        imageListCerrora.length == 0 ? `${BACKEND_URL}${initCerroraImagePath}` :
                                            `${BACKEND_URL}/${"cerrora"}/${selectedModelVariable}/${imageListCerrora[currentImageIndexState]}`
                                    }
                                    alt={"Cerrora Prediction"}
                                    title="Cerrora Prediction"
                                    zoomLevel={zoomControls.zoomLevel}
                                    panX={zoomControls.panX}
                                    panY={zoomControls.panY}
                                    isDragging={zoomControls.isDragging}
                                    onWheel={zoomControls.handleWheel}
                                    onMouseDown={zoomControls.handleMouseDown}
                                    onMouseMove={zoomControls.handleMouseMove}
                                    onMouseUp={zoomControls.handleMouseUp}
                                />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImageInferenceSlider;
