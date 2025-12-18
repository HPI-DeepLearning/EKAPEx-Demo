"use client"
import React, {useEffect, useState} from 'react';
import {Header} from "@/components/header";
import {Provider, useSelector} from "react-redux";
import {store} from "@/lib/rdx/Store";


const InferenceCompare: React.FC = (): React.JSX.Element => {
    return (
        <Provider store={store}>
            <div className="flex flex-col min-h-screens">
                <div className="flex-1 flex flex-col sm:flex-row">
                    <main className="border-red-500 border-2 flex-1 flex gap-2">

                        <div className={"border-2 border-red-500 flex-1 "}>
                            <h1 className={"font-bold text-xl italic pl-4 py-2"}>Graphcast</h1>

                        </div>

                        <div className={"border-2 border-black flex-1 "}>
                            <h1 className={"font-bold text-xl italic pl-4 py-2"}>Cerrora</h1>

                        </div>

                    </main>
                </div>
            </div>
        </Provider>
    );
};



/*
<TransformWrapper>
    <TransformComponent>
        <ImgWrapper modelType={modelType} imgSrc={imgDetail}/>
    </TransformComponent>
</TransformWrapper>



*/
