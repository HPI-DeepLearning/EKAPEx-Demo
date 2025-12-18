import React from 'react';
import Image from "next/image";

    const InferenceImageZoom: React.FC = ({
                                 src,
                                 alt,
                                 zoomLevel,
                                 panX,
                                 panY,
                                 isDragging,
                                 onWheel,
                                 onMouseDown,
                                 onMouseMove,
                                 onMouseUp,

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
    };

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
                priority={true}
                {src !== "undefined" ? (
                    <>
                    <h1>{src}</h1>
                    <Image
                        className={"object-contain opacity-60 pointer-events-auto"}
                    src={src}
                    alt={alt}

                    sizes="100vw"
                    fill
                    style={imageStyle}
                    draggable={false}
                />

                    </>):(
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

export default InferenceImageZoom;
