import {configureStore} from "@reduxjs/toolkit"
import weatherReducer from "./WeatherSlice"

export const store = configureStore({
    reducer:{
        weatherReducer
    }
})
