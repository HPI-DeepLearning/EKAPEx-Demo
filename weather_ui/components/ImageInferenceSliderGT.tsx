"use client"
import React, {useState, useEffect} from 'react';
import { Play, Pause, SkipForward, SkipBack, RotateCcw } from 'lucide-react';
import ImageZoom from "@/components/ImageZoom";
import { useSelector} from "react-redux";
import {useImageZoom} from "@/hooks/UseImageZoom";
import {fetchRandomImage} from "@/lib/api-client";
import {MoonLoader} from "react-spinners";

const ImageInferenceSliderGT = () => {
    const zoomControls = useImageZoom();
    const BACKEND_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;

    const currentImageIndexState = useSelector((state: any)=>state.weatherReducer.currentImageIndex)
    const imageListGt = useSelector((state: any)=>state.weatherReducer.ground_truth_img_list)
    // log the image list
    console.log(imageListGt)

    const selectedModelVariable = useSelector((state: any)=> state.weatherReducer.currentSelectedVariable)
    const [initCerraImagePath,setInitCerraImagePath] = useState("");

    const fetchImage = async()=>{
        const urlPathCerrora:string = await fetchRandomImage("cerrora", selectedModelVariable);
        setInitCerraImagePath(urlPathCerrora)
    }

    useEffect(() => {
        fetchImage()
    }, [initCerraImagePath]);
    
    return (
        <div className="w-full flex justify-center items-center">
            <div className="w-full max-w-4xl">
                {initCerraImagePath === "" ? (
                    <div className="flex justify-center items-center h-[400px]">
                        <MoonLoader color="hsl(var(--primary))" size={64} />
                    </div>
                ) : (
                    <ImageZoom
                        src={
                            imageListGt.length == 0 ? `${BACKEND_URL}${initCerraImagePath}` :
                                `${BACKEND_URL}/${"cerrora"}/${selectedModelVariable}/${imageListGt[currentImageIndexState]}`
                        }
                        alt={`Ground Truth - Image ${currentImageIndexState + 1}`}
                        title="Ground Truth Data"
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
    );
};

export default ImageInferenceSliderGT;
