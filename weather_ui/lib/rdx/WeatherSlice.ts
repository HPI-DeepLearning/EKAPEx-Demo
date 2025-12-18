import {createSlice} from  "@reduxjs/toolkit"

const initialState = {
    applicationState: "currentAppState...",
    loadingState: false,
    currentImageIndex: 0,
    cerrora_img_list: [],
    graphcast_img_list: [],
    ground_truth_img_list: [],
    validTimeList: [],
    selectedBaseTime:-320,
    selectedValidTime: -4350,
    currentSelectedVariable: "seaLevelPressure",
    app_model: "cerrora",
    modelSwitchVariable: "sea_level",
}
const weatherSlice = createSlice({
    name: "weather",
    initialState,
    reducers: {
        updateLoadingDone:(state,action)=>{

            state.loadingState = action.payload
        },
        updateLoadingStart: (state, action)=>{

            state.loadingState = action.payload
        },
        updateImageIndex:(state,action)=>{
            state.currentImageIndex = action.payload
        },
        updateImageList:(state,action)=>{
            state.cerrora_img_list = action.payload.cerrora_img_list
            state.graphcast_img_list = action.payload.graphcast_img_list
            state.ground_truth_img_list = action.payload.ground_truth_img_list

        },
        updateValidTimeList:(state,action)=>{
            state.validTimeList = action.payload

        },
        updateSelectedVariable: (state, action)=>{
            state.currentSelectedVariable = action.payload;
        },
        updateModelSwitchVariable: (state, action)=>{
            state.modelSwitchVariable = action.payload;
        },
        updateBaseTimeChanged:(state,action)=>{
            state.selectedBaseTime = action.payload
        },
        updateValidTime:(state,action)=>{
          state.selectedValidTime = action.payload
        },
        updateAppModel:(state,action)=>{
            state.app_model = action.payload
        }
    }
})

export const {
    updateValidTime,
    updateBaseTimeChanged,
    updateSelectedVariable,
    updateImageIndex,
    updateLoadingStart,
    updateLoadingDone,
    updateAppModel,
    updateValidTimeList,
    updateModelSwitchVariable,
    updateImageList} = weatherSlice.actions
export default weatherSlice.reducer;
