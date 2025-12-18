"use client"
import React, {useState, useCallback, } from 'react';
import ZoomableImage from './ZoomableImage';
const useImageZoom = () => {
    const [zoomLevel, setZoomLevel] = useState(1);
    const [panX, setPanX] = useState(0);
    const [panY, setPanY] = useState(0);
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

    const handleWheel = useCallback((e) => {
        e.preventDefault();
        const zoomFactor = 0.1;
        const newZoom = e.deltaY > 0
            ? Math.max(0.5, zoomLevel - zoomFactor)
            : Math.min(10, zoomLevel + zoomFactor);

        setZoomLevel(newZoom);
    }, [zoomLevel]);

    const handleMouseDown = useCallback((e) => {
        setIsDragging(true);
        setDragStart({
            x: e.clientX - panX,
            y: e.clientY - panY
        });
    }, [panX, panY]);

    const handleMouseMove = useCallback((e) => {
        if (!isDragging) return;

        const newPanX = e.clientX - dragStart.x;
        const newPanY = e.clientY - dragStart.y;

        setPanX(newPanX);
        setPanY(newPanY);
    }, [isDragging, dragStart]);

    const handleMouseUp = useCallback(() => {
        setIsDragging(false);
    }, []);

    const resetZoom = () => {
        setZoomLevel(1);
        setPanX(0);
        setPanY(0);
    };

    return {
        zoomLevel,
        panX,
        panY,
        isDragging,
        handleWheel,
        handleMouseDown,
        handleMouseMove,
        handleMouseUp,
        resetZoom
    };
};

interface SynchronizedImageZomProps {
    graphcastImg: string
    cerroraImg:string
}

const SynchronizedImageZoom = ({graphcastImg,cerroraImg}:SynchronizedImageZomProps) => {


    const zoomControls = useImageZoom();

    return (
        <div className="flex flex-col p-6 bg-gray-50 min-h-screens ">
            <div className=" mx-auto">
                <div className=" flex-1 flex gap-2">

                    <div>
                    <h1 className={"font-bold text-xl italic pl-4 py-2"}>Graphcast</h1>
                        <ZoomableImage
                            modelType={"graphcast"}
                            src={graphcastImg}
                            alt="Graphcast Prediction"
                            title="Graphcast Prediction"
                            zoomLevel={zoomControls.zoomLevel}
                            panX={zoomControls.panX}
                            panY={zoomControls.panY}
                            isDragging={zoomControls.isDragging}
                            onWheel={zoomControls.handleWheel}
                            onMouseDown={zoomControls.handleMouseDown}
                            onMouseMove={zoomControls.handleMouseMove}
                            onMouseUp={zoomControls.handleMouseUp}
                        />
                    </div>
                    <div>
                            <h1 className={"font-bold text-xl italic pl-4 py-2"}>Cerrora</h1>
                        <ZoomableImage
                            modelType={"cerrora"}
                            src={cerroraImg}
                            alt="Cerrora Prediction"
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
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SynchronizedImageZoom;
