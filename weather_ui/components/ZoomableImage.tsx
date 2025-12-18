// Individual zoomable image component
const ZoomableImage = ({
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
        width: '850px',
        height: '850px',
        border: '2px solid #ccc',
        borderRadius: '8px',
        overflow: 'hidden',
        position: 'relative',
        backgroundColor: '#f5f5f5'
    };

    const BACKEND_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;
    const [forecastVariable,imgName] = src.split(":")

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
                {imgName !== "undefined" ? (<img
                    src={`${BACKEND_URL}/${modelType}/${forecastVariable}/${imgName}`}
                    alt={alt}
                    style={imageStyle}
                    draggable={false}
                />):(
                    <div className={" h-full flex justify-center items-center"}>

                        <h1 className={"font-bold text-xl italic pl-4 py-2"}>
                            Please select a valid Variable and Image to display inference.
                        </h1>
                    </div>
                )}


            </div>
        </div>
    );
};

export default ZoomableImage;
