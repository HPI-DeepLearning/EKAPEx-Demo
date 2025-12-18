import React from 'react';
import Image from "next/image";

interface IImgWrapperProps {
    imgSrc: string,
    modelType: string
}
const ImgWrapper: React.FC<IImgWrapperProps> = ({imgSrc,modelType}): React.JSX.Element => {
    const backendUrl = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;
    const [forecastVariable,imgName] = imgSrc.split(":")
    console.log(forecastVariable," :: ",imgName)

    return (
        <div className={"w-[850px] h-[850px] relative cursor-grab active:cursor-grabbing"}>

            <Image
                //src={`http://127.0.0.1:8000/backend-fast-api/streaming/${modelType}/${forecastVariable}/${imgName}`}
                src={`${backendUrl}/${modelType}/${forecastVariable}/${imgName}`}
                alt={"sdfs"} width={1200} height={1200}/>
        </div>
    );
};

export default ImgWrapper;
