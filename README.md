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

This scripts can be used for rendering of thermal simulations, this append simulation results onto shape texture, in a way
that only places hotter than specific temperature are colored in red.

# `postprocessing`

## `postprocessing/plot.py`

This script can generate graph from simulation csv file, the data can be exported directlly from paraview. 

## `postprocessing/plot_meas.py`

This script can generate `simulation vs measurement` plot 
