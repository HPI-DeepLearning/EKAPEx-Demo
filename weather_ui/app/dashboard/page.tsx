import React from 'react';
import ImageInferenceSlider from "@/components/ImageInferenceSlider";
import ImageInferenceSliderGT from "@/components/ImageInferenceSliderGT";
import LIneChrt from "@/components/LIneChrt";
import BarChrt from "@/components/BarChrt";
import ModelMetricsReportCard from "@/components/ModelMetricsReportCard";

const Page: React.FC = (): React.JSX.Element => {
    return (
        <div className={"flex item-center justify-center"}>
            <div>
                <ImageInferenceSlider />
                <ImageInferenceSliderGT />

            </div>
            <div className={"flex flex-col w-1/4 gap-2"}>
                {//<ModelMetricsReportCard description={"Overall Accuracy"} score={87.3} indicator={"%"}/>
                //<ModelMetricsReportCard description={"Mean Absolute Error"} score={1.8} indicator={"oc"}/>
                //<ModelMetricsReportCard description={"Precipitation RMSE"} score={12.4} indicator={"mm"}/>
            }

            </div>
        </div>
    );
};

export default Page;
