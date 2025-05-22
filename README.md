# Circulation and Biogeography:

### Code to replicate modeled larval dispersal and neutral population modeling in the paper "Circulation-driven larval dispersal patterns are sufficient to set the location of many coastal biogeographic boundaries" (Lush and Pringle, 2025)

Particle tracking uses [TRACMASS](https://github.com/TRACMASS/Tracmass), with 1/12 deg. global velocity fields (top 36 depth levels) on the native C-grid from the [Copernicus Marine Environmental Monitoring Service](https://marine.copernicus.eu/) (CMEMS).  
The code in this repository is divided into 3 directories: particleTracking, populationModeling, and visualization.  
- particleTracking includes files for building TRACMASS executables/output and files used to create connectivity matrices  
- populationModeling includes files used to model populations globally and analyze population distributions  
- visualization includes code to replicate figures within the manuscript


## File descriptions:
### particleTracking _(directory)_:  
The particleTracking directory contains the following files:  
- BIGrun.com
  - bash script to iterate over months in a year, create executable for tracmass runs, and run (times run and create/writes log file)
- sampleRuns _(subdirectory)_
  - sampleRuns contains 5 subdirectories (Atlantic, fulInd _(Indian Ocean)_, indPac _(Indo-Pacific)_, norPac _(north Pacific)_, souPac _(south Pacific)_), each with code to build and run TRACMASS within each of the overlapping particle tracking analysis regions.
  - The code in the sampleRuns subdirectory uses the following organizational pattern:
    - Makefile
      - makefile for building TRACMASS executable
    - Makefile.global
      - additional dependencies for makefile, included in Makefile above
    - output_trm _(subdirectory)_
      - subdirectory for output files; outputs to further subdirectory _mycase_
      - _contains empty subdirectory mycase; used to hold TRACMASS output before processing to connectivity matrices_
    - projects _(subdirectory)_
      - Makefile.prj
        - project-specific flags
      - myCase.in
        - project-specific inputs
      - readfield.f95 _and_ setupgrid.f95
        - code to read in velocity fields and set up model grid
    - src _(subdirectory)_
      - source code for TRACMASS (the version of TRACMASS used in this paper was accessed from the TRACMASS github in March 2019)
    
- seedfiles _(subdirectory)_
  - contains release locations for individual particle tracking regions as text files (denoted .seed)
  - _note that this regional breakdown was necessary for older/lower performance hardware_
    
### populationModeling _(directory)_:  
The populationModeling directory contains the following files:  
- analysis_regions.npz
  - This file contains individual regions used for analysis of population modeling results.
- automated_max_multigen.pkl
  - This file contains a pickled Pandas dataframe containing the locations of biogeographic boundaries
- cleaned_meow_intersections.npz
  - Contains the locations and names of intersections of Marine Ecoregions of the World (MEOW) shapefiles with the global coastline.
  - Multiple intersections (where a single MEOW ecoregion intersected with the coastline multiple times) were removed
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

### visualization _(directory)_:  
The visualization directory contains the following files:  
- 3spp_alongshore.py
  - creates figure showing species distributions over time for 3 model species in the Gulf of Maine (North America) at generations 0 (initial), 10, 100, and 1000.
- bar_global.py
  - Bar plot depicting model performance globally by season and pelagic larval duration (PLD)
- bar_hemispheres.py
  - Bar plot depicting model performance broken down by hemisphere for all seasons and PLDs
- byGeneration.py
  - Line plot depicting mode performance and number of discrete biogeographic boundaries as a function of generation (initial transients omitted for clarity)
- ecoregions.exclude.txt
  - MEOW ecoregions excluded from the analysis in this paper (by ecoregion code)
- globalBoundPlot_circ.py
  - Creates global map of model boundaries and 'uncertainty radii' around MEOW/coastline intersection points (for April/May/June larval releases and 30-day PLDs)
- jaccardAndMeow_eastCoast.py
  - Plots Jaccard difference against MEOW and model boundaries along the east coast of the United States
- jaccard_vals_1000gen.npz
  - Jaccard difference values globally at 1000 generations for all seasons and PLDs

