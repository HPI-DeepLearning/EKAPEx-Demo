import React from 'react';
import {FaBeer} from "react-icons/fa";
import {WiRain, WiRaindrop} from "react-icons/wi";

interface IModelMetricsCard{
    description: string
    score: number
    indicator: string
}

const ModelMetricsReportCard: React.FC<IModelMetricsCard> = ({description,score,indicator}): React.JSX.Element => {
    return (
        <div className={"border border-2 flex items-center justify-between py-4 px-2"}>
            <div>
                <h2 className={"text-gray-500 text-2xl"}>
                    {description}
                </h2>
                <h2 className={"text-3xl font-bold"}>{`${score} ${indicator}`}</h2>
            </div>
            <div>
                <WiRain size={50}/>
            </div>
        </div>
    );
};

export default ModelMetricsReportCard;
