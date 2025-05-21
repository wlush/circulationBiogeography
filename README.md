# Circulation and Biogeography:

### Code to replicate modeled larval dispersal and neutral population modeling in the paper "Circulation-driven larval dispersal patterns are sufficient to set the location of many coastal biogeographic boundaries" (Lush and Pringle, 2025)

Particle tracking uses TRACMASS, with 1/12 deg. global velocity fields (top 36 depth levels) on the native C-grid from the Copernicus Marine Environmental Monitoring Service (CMEMS).  
The code in this repository is divided into 3 directories: particleTracking, populationModeling, and visualization.  
particleTracking includes files used to set up TRACMASS runs, as well as files used to create connectivity matrices  
populationModeling includes files used to model populations globally and analyze population distributions  
visualization includes code to replicate figures within the manuscript  
