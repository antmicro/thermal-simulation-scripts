# Thermal simulation scripts 

This repository contains scripts used for thermal simulations and blender renders of thermal simulations 

# File structure 

**blender** 

This directory contains scripts used for blender rendering

**freecad**
This directory contains scripts used for FreeCad automation

**paraview**
This directory contains scripts used for ParaView automation

**postprocessing**
This directory contains scripts used for addition postprocessing

# `blender` 

## `blender/thermal_sim_animation_textured.py`

This scripts can be used for rendering thermal simulations, this script append simulation results onto shape texture, in a way
that only places hotter than specific temperature are colored in red. To use this script a shading from `blender/thermal_animation_material.blend` must be added 
into blender collection.

# `postprocessing`

## `postprocessing/plot.py`

This script can generate graph with simulation results from csv file, the data can be exported directlly from paraview, see [this](https://discourse.paraview.org/t/simple-exporting-point-data-over-time-to-excel-table/6756) for more information about exporting data from paraview.   

The csv file must contain following columns:
- `Time` contains indexes of time steps
- `max(Maximum)` - contains temperature of hottest point in Kelwins

## `postprocessing/plot_meas.py`

This script can generate graph which comparison of simulation and measurement.

The csv file must contain following columns:
- `Time` contains indexes of time steps
- `max(Maximum)` - contains temperature of the hottest point in Kelwins (from simulation)
- `Meas` - contains measured temperature od radiator
