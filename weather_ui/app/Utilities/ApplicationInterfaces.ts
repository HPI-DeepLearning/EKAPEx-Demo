import extremeEvents from "@/extreme_events_dataset.json";

export interface ValidTimeUpdateEvent extends CustomEvent {
    detail: { validTime: string };
}

export interface WeatherFrameSelectEvent extends CustomEvent {
    detail: { timestamp: string };
}

// Add type safety for extreme events
export interface ExtremeEvent {
    type: string[];
    description: string;
    start_time: string;
    end_time: string;
    lat_slice: number[];
    lon_slice: number[];
    year: number;
    location: string[];
}

export interface ExtremeEventsDataset {
    [key: string]: ExtremeEvent;
}

// Cast the imported data to unknown first
export const typedExtremeEvents = extremeEvents as unknown as ExtremeEventsDataset;

// Update interface for valid times
export interface TimeOption {
    label: string;
    value: string;
}

export interface ValidTimeData {
    value: string;
    label?: string;
}

export interface ValidTimesResponse {
    [baseTime: string]: ValidTimeData[];
}

export interface QueryMeta {
    queryTime?: string;
}

export interface ValidTimeResponse {
    label: string;
    value: string;
}

export interface ValidTimesQueryResponse {
    validTimes: ValidTimeResponse[][];
}

export interface WeatherData {
    images: Array<{
        timestamp: string;
        url: string;
    }>;
}

export interface ValidTimesAPIResponse {
    validTimes: TimeOption[][];
}

export interface IWeatherSideBarProps {
    toggleDisplay: (input:boolean)=>void,
    toggleValue: boolean,
    onDisplayChangedImg: (inputParam:{type?:string, value:string})=>void
}

export interface TimeRange {
    baseTime: number;
    validTime: number[];
}

export interface ImageResponse {
    timestamp: string;
    url: string;
}

export interface WeatherResponse {
    images: ImageResponse[];
    validTimes: TimeOption[];
}

export interface TimeOption {
    label: string;
    value: string;
}
export interface fileOptions{
    variable:string
    baseTime:number,
    modelType:string
}
