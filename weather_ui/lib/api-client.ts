import {ImageResponse} from "next/og";
import {fileOptions, TimeOption, WeatherResponse} from "@/app/Utilities/ApplicationInterfaces";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const IMAGE_BASE_URL = process.env.NEXT_PUBLIC_IMAGE_BASE_URL;

export async function fetchBaseTimes(variableType: string,model_type:string): Promise<TimeOption[]> {

    console.log(" ::: ❌❌❌❌❌❌❌❌❌❌❌❌❌onModelChange", model_type);
    const response = await fetch(`${API_BASE_URL}/base-times/${model_type}?variableType=${variableType}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch base times: ${response.status}`);
  }
  const data = response.json()
  return data;
}

export async function fetchValidTimes(
    model_type: string,
    variableType: string,
  baseTime: number
): Promise<TimeOption[]> {
  const url = new URL(`${API_BASE_URL}/valid-times/${model_type}`);
  url.searchParams.append('variableType', variableType);
  url.searchParams.append('queryTime', baseTime.toString());

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Failed to fetch valid times: ${response.status}`);
  }
  const data = await response.json();
  return Array.isArray(data) && data.length > 0 ? data[0] : [];
}

export async function fetchWeatherData(model_type: string,endpoint: string, params: { baseTime: number; validTime: number[] }): Promise<WeatherResponse> {

    console.log("🚨🚨🚨🚨🚨🚨🚨 TIME TO fetchWeatherData()...🚨",model_type)
// /data/sea_level/{model_type}
    const url = `${API_BASE_URL}/${endpoint}/${model_type}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      baseTime: params.baseTime,
      validTime: params.validTime
    })
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch weather data: ${response.status} ${errorText}`);
  }
  const data = await response.json();
  if (data.images) {
    data.images = data.images.map((image: ImageResponse) => ({
      ...image,
      url: image.url.startsWith('http') ? image.url : `${IMAGE_BASE_URL}/${image.url}`
    }));
  }
  return data;
}

export const fetchFiles = async(fOptions: fileOptions):Promise<Array<string>> => {
  const {variable,baseTime} = fOptions;
  const url:string = `${API_BASE_URL}/data/${variable}/${baseTime}`
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load Images: ${response.status}`);
  }
  return response.json()
}

export const fetchRandomImage = async(model_name: string, varName:string):Promise<string> =>{
  // http://localhost:8000/api/v1/data/rand/init_random_image/graphcast
  const url:string = `${API_BASE_URL}/data/rand/init_random_image/${model_name}`;
  const response = await fetch(url);

  if(!response.ok){
    throw new Error(`Failed to fetch Image with Error. ${response.status}`)
  }
  return response.json();
}

export const fetchTempMetrics = async (countryName:string="Amsterdam",baseTime:number=1609804800) =>{
    const url = `${API_BASE_URL}/temp_compare/${countryName}/${baseTime}`;
    console.log(`A call to make inference for ${countryName}`)
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch Temp Metrics with Error. ${response.status}`);
    }
    return response.json();
}

