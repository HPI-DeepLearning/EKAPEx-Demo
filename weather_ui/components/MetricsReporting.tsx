import React from 'react';
import ModelMetricsReportCard from "@/components/ModelMetricsReportCard";
import LIneChrt from "@/components/LIneChrt";
import BarChrt from "@/components/BarChrt";

const MetricsReporting: React.FC = (): React.JSX.Element => {
    return (

        <div className={"flex  gap-2 border border-2 border-red-500"}>
            {
        //<ModelMetricsReportCard description={"Overall Accuracy"} score={87.3} indicator={"%"}/>
    //<ModelMetricsReportCard description={"Mean Absolute Error"} score={1.8} indicator={"oc"}/>
    //<ModelMetricsReportCard description={"Precipitation RMSE"} score={12.4} indicator={"mm"}/>
}
    <div className={"flex  w-ful justify-center mt-4"}>
        <LIneChrt/>
        <BarChrt/>
    </div>
</div>
    );
};

export default MetricsReporting;
