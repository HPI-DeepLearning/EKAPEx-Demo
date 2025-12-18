import {useCallback, useState} from "react";

export const useImageZoom = () => {
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
