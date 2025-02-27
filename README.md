# Thermal simulation scripts 

This repository contains scripts used for thermal simulations. 

# Installation

**Dependencies**

The `thermal-simulation-scripts` requires following dependencies:  
* calculix    
* paraview    
* pyton3    
* pip  
* libxrender1  
* FreeCad = 1.0.0
* ccx2paraview     

On the Debian based systems those dependencies can be installed by following commands:

```
sudo apt install -y paraview calculix-ccx python3 python3-pip paraview libxrender1 
pip install ccx2paraview
wget https://github.com/FreeCAD/FreeCAD/releases/download/1.0.0/FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage
sudo mv FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage /usr/local/bin/freecad
sudo chmod +x /usr/local/bin/freecad
```

**Installation**

To install the `thermal-simulation-script` run following commands:

```
git clone http://github.com/antmicro/thermal-simulation-scripts
cd thermal-simulation-scripts
pip install .
```

Until now, the script can be run by `tpre` and `tpost` commands, the `tpre` is designed for task related to preproccesing,
the `tpost` is used for simulation postprocessing. For detailed usage see the `Usage` section bellow, to see an example scroll down 
to `Example usage` section bellow.

# Usage

Following section describes a typical usage of `thermal-simulation-scripts` 

## Constrains and mesh generation

The first step of thermal simulation is to define simulation constrains and creating the 
mesh, this can be done for example in [FreeCad](https://www.freecad.org/) as described in this [manual](https://wiki.freecad.org/Transient_FEM_analysis).
As output of this step file in [`.inp`](https://web.mit.edu/calculix_v2.7/CalculiX/ccx_2.7/doc/ccx/node160.html) format must be created. 


## Preparation

This step is designed for additionial preparation of a simulation.
To run the simulation an `.inp` file generated in previous step should be sufficient,
however procedures described bellow can preserve from simulation issues.

**Preparing the simulation**

By default simulation input file may contain unwanted or misconfigured settings,
for example: number or iteration can be to low or value of mechanical 
displacement can be simulated. 

The simulation settings can be easily reconfigured by using a `prepare_sim.py` script:

```
tpre prepare <path to .inp file> <simulate temperature only>
```

Where 
* `<path to .inp file>` - is a path to CalculiX input file
* `<simulate temperature only>` - when set to true only 
`structural temperature` and `heat flux` will be simulated 

The script will always check configured number of iteration and increase this value when it is necessary 

**Checking the simulation settings**

After preparation of the simulation, the simulations settings should be checked before running 
the actual simulation. This can be achieved by `tpre get-settings` command. This 
command will print selected simulations settings and save those settings into a json file.

To check the simulation run `tpre get-settings` as follow: 

```
tpre get-settings <file name> <output file>
```

Where:
- `file name` - is a path to CalculiX `.inp` file
- `output file` - is a path where file with simulation settings will be saved

## Running the simulation

The simulation can be computed using [CalculiX](https://www.calculix.de/). To run the simulation use following command: 

```
ccx <path to .inp file>
```

Where
* `<path to .inp file>` - path to CalculiX `.inp` file

For more details refers to the [CalculiX manual](http://www.dhondt.de/ccx_2.20.pdf)

## Converting simulation results  

To process the output data from simulation, the simulation results must be converted to `.vtk` format.
Use a `ccx2paraview` tool to convert CalculiX output file into `.vtk` format as follow:

```
ccx2paraview <frd file> vtk
```

Where 
- `<frd file>` - Is a path to CalculiX output file in `.frd` format 

## Post-processing

**Generating .csv files**

The simulation data files, generated in previous steps, contains temperature for every point, 
in many cases is convenient to have a file with highest and lowest temperature of simulated model over time. 

Use following command to generate  a '*.csv' file with simulation data.

```
tpost csv <vtk directory> <sta file> <output file> 
```

Where:
- `<vtk directory>` - path to directory with `.vtk` files generated with `ccx2paraview`
- `<sta file>` - path to `.sta` files this file is generated as output from CalculiX
- `<output file>` - path to output file


The output file contains following columns:
- `time [s]` - time of simulation
- `max [K]` - highest temperature of model at specific time in Kelvins
- `max [C]` - highest temperature of model at specific time in Celsius degrees
- `min [K]` - lowest temperature of model at specific time (in Kelvins)
- `min [C]` - lowest temperature of model at specific time (in Celsius degrees)

**Generating graphs** 

To generate `temperature vs time` graphs following command can be used:

```
tpost plot <data file> <output dir> <simulation json> 
```

Where:
- `<data file>` - path to simulation `.csv` file, generated in the previous step
- `<output dir>` - path to directory where graphs will be saved
- `<simulation json>` - optional `simulation json` file generated in previous steps

As output following graphs will be generated:
- Highest temperature of the model over time, both in Kelvins and Celsius degrees
- Lowest temperature of the model over time, both in Kelvins and Celsius degrees
- Difference between highest temperature and lowest temperature of the model over time, 
both in Kelvins and Celsius degrees
- Highest temperature of the model over simulation steps, both in Kelvins and Celsius degrees
- Lowest temperature of the model over simulation steps, both in Kelvins and Celsius degrees
- Difference between highest temperature and lowest temperature of the model simulation steps, 
both in Kelvins and Celsius degrees
- Simulation iterations in over time

**Generating previews**

To generate a quick preview of the simulation results, following command can be used:

```
tpost preview
```

As a results of this command an images colored with temperature gradient will be generated in a 
directory named `previews`. The images shows temperature gradient on the last stage of simulation from different views.
This command will search for `vtk` directory in the current working directory, the `vtk` directory must contains `.vtk` files generated in the previous steps.



**Generating animations**

To generate an quick animation of temperature gradient over time following command can be used. 

```
tpost animation
```

As a results of this command an animation of temperature gradient will be generated in a 
directory named `previews`. This command will search for `vtk` directory in the current working directory, 
the `vtk` directory must contains `.vtk` files generated in the previous steps.


**Converting to blender**

The `.vtk` files generated in previous step can be converted to `.x3d` format
which can be later used for rendering in programs like `blender`. 

To convert `.vtk` files into blender use following command:

```
tpost x3d
```

As as results of this command a files in `.x3d` format will be created in the x3d directory
This command will search for `vtk` directory in the current working directory, the `vtk` directory must contains `.vtk` files generated in the previous steps.


# Example usage

Following section describes an example usage 

## Set constrains and generate mesh

To speedup the example usage, in the `desings` directory there is a prepared file 
with constrains and generated mesh, so you can skip  the `Constrains and mesh generation` section, and go to the next stage. 

## Prepare simulation

**Prepare simulation settings**

To prepare simulation run: 
```
tpre prepare designs/FEMMeshGmsh.inp True
```

**Check simulation settings and generate simulation json file**

To check simulation settings run following command, 
a file named `simulation.json` should be generated in the `designs` directory.

```
tpre get-settings desings/FEMMeshGmsh.inp desings/simulation.json
```

## Running the simulation

If you want you can enable the CalculiX to use more than one core by setting the 
`OPM_NUM_THREADS` to number of cores you want to use for simulation.

For example use 16 cores for computing:
```
export OMP_NUM_THREADS=16
```

Run simulation 
```
cd designs
ccx FEMMeshGmsh
```

## Convert CalculiX to vtk

Run following commands to convert output from CalculiX to vtk

```
ccx2paraview FEMMeshGmsh.frd vtk
mkdir vtk
mv *.vtk vtk/
```

## Post process the results

**Create .csv file**

Run following command, a `temperature.csv` file should be generated in the designs directory

```
tpost csv designs/vtk designs/FEMMeshGmsh.sta designs/temperature.csv
```

**Create graphs**

To create a graphs run following command

```
mkdir desings/graphs
tpost plot designs/temperature.csv designs/graphs
```

**Generate preview**

To generate previews use following command

```
cd designs
tpost preview
```

**Generate animation (from paraview)**

To generate animation from paraview, use following command

```
cd desings
tpost animation
```

**Convert to blender (x3d files)**

To generate a files in x3d format

```
cd designs
tpost x3d
```

# Licensing

This project is published under the [Apache-2.0](https://github.com/antmicro/thermal-simulation-scripts/blob/main/LICENSE) license
