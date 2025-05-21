# Circulation and Biogeography:

### Code to replicate modeled larval dispersal and neutral population modeling in the paper "Circulation-driven larval dispersal patterns are sufficient to set the location of many coastal biogeographic boundaries" (Lush and Pringle, 2025)

Particle tracking uses TRACMASS, with 1/12 deg. global velocity fields (top 36 depth levels) on the native C-grid from the Copernicus Marine Environmental Monitoring Service (CMEMS).  
The code in this repository is divided into 3 directories: particleTracking, populationModeling, and visualization.  
- particleTracking includes files used to set up TRACMASS runs, as well as files used to create connectivity matrices  
- populationModeling includes files used to model populations globally and analyze population distributions  
- visualization includes code to replicate figures within the manuscript

### particleTracking:  
The particleTracking directory contains the following files:  

### populationModeling  
The populationModeling directory contains the following files:  
- analysis_regions.npz
  - This file contains individual regions used for analysis of population modeling results.
- automated_max_multigen.pkl
  - This file contains a pickled Pandas dataframe containing the locations of biogeographic boundaries
- cleaned_meow_intersections.npz
  - Contains the locations and names of intersections of Marine Ecoregions of the World (MEOW) shapefiles with the global coastline.
  - Multiple intersections (where a single MEOW ecoregion intersected with the coastline multiple times) were removed
- count_meow_v2.py
  - Deprecated, will be removed
- excludePoints.py
  - Interactively select points to exclude from the analysis; this code was used to exclude the Indo-Pacific from the population model analysis due to issues with boundary-finding on islands
- fixed_regional_meow_subsets.npz
  - breaks down MEOW intersection locations based on regions from analysis_regions.npz
- indoPacific_removePoints.npz
  - removed points in the Indo-Pacific (removed due to issues with boundary-finding on islands)
- intersectionPoints.shp
  - shapefile containing intersections between MEOW and global coastlines
- jaccard_stats_automated_regional_multiGen.py
  - Code to determine model performance statistics, contained in automated_max_multigen.pkl
- make_MEOW_pointList.py
  - Utility code used to create cleaned_meow_intersections.npz based on intersections between MEOW shapefiles and global coastline
- simplified_regional_subsets.py
  - breaks automated boundary-finding results into discrete regions 

### visualization  
The visualization directory contains the following files:  

