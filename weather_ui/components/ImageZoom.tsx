import React from 'react';

interface ImageZoomProps {
    src: string;
    alt: string;
    title: string;
    zoomLevel: number;
    panX: number;
    panY: number;
    isDragging: boolean;
    onWheel: (e: any) => void;
    onMouseDown: (e: any) => void;
    onMouseMove: (e: any) => void;
    onMouseUp: () => void;
    modelType?: string;
}

const ImageZoom: React.FC<ImageZoomProps> = ({
                                 src,
                                 alt,
                                 title,
                                 zoomLevel,
                                 panX,
                                 panY,
                                 isDragging,
                                 onWheel,
                                 onMouseDown,
                                 onMouseMove,
                                 onMouseUp,
                                 modelType,

                             }) => {
    const imageStyle = {
        transform: `scale(${zoomLevel}) translate(${panX / zoomLevel}px, ${panY / zoomLevel}px)`,
        transformOrigin: 'center center',
        transition: isDragging ? 'none' : 'transform 0.1s ease-out',
        cursor: isDragging ? 'grabbing' : 'grab',
        width: '100%',
        height: '100%',
        objectFit: 'contain'
    };

    const containerStyle = {
        width: '650px',
        height: '650px',
        borderRadius: '8px',
        overflow: 'hidden',
        position: 'relative',
        backgroundColor: '#f5f5f5'
    };

     //const [forecastVariable,imgName] = src.split("#")

    return (
        <div className="flex flex-col items-center">

            <div
                style={containerStyle}
                onWheel={onWheel}
                onMouseDown={onMouseDown}
                onMouseMove={onMouseMove}
                onMouseUp={onMouseUp}
                onMouseLeave={onMouseUp}
            >
                {src !== "undefined" ? (<img
                    className="w-full h-full object-cover transition-opacity duration-500 ease-in-out opacity-100"
                    src={`${src}`}
                    alt={alt}
                    style={imageStyle}
                    draggable={false}
                />):(
                    <div className={"h-full flex justify-center items-center"}>

                        <h1 className={"font-bold text-xl italic pl-4 py-2"}>
                            Please select a valid Variable and Image to display inference.
                        </h1>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ImageZoom;
