import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export enum VARIABLE_TYPES  {
  DESCRIPTION ="PLEASE SELECT A MODEL VARIABLE",
  TEMPWIND = "temp_wind",//"tempWind",
  GEOPOTENTIAL = "geo",//"geopotential",
  PRECEPITATION = "rain",
  SEALEVELPRESSURE = "sea_level"//"seaLevelPressure"
}

