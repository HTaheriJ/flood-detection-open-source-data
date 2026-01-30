# Flood Detection Using Open-Source Remote Sensing Data
This repository provides a flexible and customizable workflow for inundation mapping. By modifying a set of basic input parameters in the main code, users can detect inundated areas over a chosen time period and within a specified area of interest using remote sensing data.


## Key Features
- Flood / inundation detection based on open source satellite imagery
- User-defined area of interest (AOI)
- Customizable time period selection
- indication of lag of date
- indication of cloud threshold and min area of interest
- Designed for open-source Earth observation data
- Suitable for flood detection in the vast area
- Modular and easy-to-extend code structure


## Data Sources
The workflow is designed to work with **open-source Earth observation data**, such as:
- Sentinel-2 multispectral imagery
- Google Earth Engine


## Methodology 
1. add other modules  
2. Define the **area of interest (AOI)**
3. Select the **time period**
4. Select the **lag**
5. Select the **cloud_threshold**
6. Select the **min_area**
7. remember to adress name of you project in initialize_earth_engine and in the GEE


