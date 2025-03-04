# Thermal simulation scripts

This repository contains scripts used for thermal simulation and data visualization.

## Table of Contents

1. [Installation](#installation)
   - [Dependencies](#dependencies)
   - [Installation instructions](#installation-instructions)
2. [Usage](#usage)
   - [Constraints and mesh generation](#constraints-and-mesh-generation)
   - [Pre-processing](#pre-processing)
   - [Running the simulation](#running-the-simulation)
   - [Post-processing](#post-processing)
   - [Generating graphs](#generating-graphs)
   - [Generating previews](#generating-previews)
3. [Example walkthrough](#example-walkthrough)
4. [Licensing](#licensing)

---

## Installation

### Dependencies

The `thermal-simulation-scripts` require the following dependencies:

- `calculix`
- `paraview` = 5.13.2
- `python` >= 3.10
- `pip`
- `libxrender1`
- `FreeCAD` = 1.0.0
- `ccx2paraview`
- `ffmpeg`

On Debian-based systems, these dependencies can be installed using:

```sh
sudo apt install -y calculix-ccx python3 python3-pip libxrender1 tar wget libgl1-mesa-glx ffmpeg
```

#### Install FreeCAD 1.0.0

```sh
wget https://github.com/FreeCAD/FreeCAD/releases/download/1.0.0/FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage
sudo mv FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage /usr/local/bin/freecad
sudo chmod +x /usr/local/bin/freecad
```

#### Install ParaView

```sh
sudo mkdir /opt/paraview
sudo wget -O /opt/paraview/paraview.tar.gz "https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.13&type=binary&os=Linux&downloadFile=ParaView-5.13.2-osmesa-MPI-Linux-Python3.10-x86_64.tar.gz"
sudo tar -xvzf /opt/paraview/paraview.tar.gz --strip-components=1 -C /opt/paraview
sudo rm /opt/paraview/paraview.tar.gz
echo 'export PATH=/opt/paraview/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Installation instructions

To install `thermal-simulation-scripts`, run:

```sh
git clone http://github.com/antmicro/thermal-simulation-scripts
cd thermal-simulation-scripts
pip install .
```

The script can be run using the following commands:

- `tpre` for pre-processing tasks.
- `tpost` for simulation post-processing.

---

## Usage

### Constraints and mesh generation

The first step in a thermal simulation is to define constraints for each surface of the 3D model and convert it into a mesh using FreeCAD. This process results in a `.inp` format file.

### Pre-processing

This step prepares the simulation. The `.inp` file should be sufficient, but additional settings can be configured.

#### Preparing the simulation

```sh
tpre prepare <path_to_inp_file> <simulate_temperature_only>
```

- `<path_to_inp_file>`: Path to the CalculiX input file.
- `<simulate_temperature_only>`: Set to `true` to simulate only temperature and heat flux.

#### Checking simulation settings

```sh
tpre get-settings <file_name> <output_file>
```

- `<file_name>`: Path to the CalculiX `.inp` file.
- `<output_file>`: Path where simulation settings will be saved.

### Running the simulation

To run the simulation using CalculiX:

```sh
ccx <path_to_inp_file>
```

Refer to the [CalculiX manual](http://www.dhondt.de/) for further details.

### Post-processing

#### Converting simulation results

```sh
ccx2paraview <frd_file> vtk
```

- `<frd_file>`: Path to the CalculiX output `.frd` file.

#### Generating CSV files

```sh
tpost csv <vtk_directory> <sta_file> <output_file>
```

- `<vtk_directory>`: Path to directory with `.vtk` files.
- `<sta_file>`: Path to `.sta` file (output from CalculiX).
- `<output_file>`: Path for the output CSV file.

The output CSV contains:

- Time [s]
- Maximum/Minimum temperature in Kelvin and Celsius

### Generating graphs

```sh
tpost plot <data_file> <output_dir> <simulation_json>
```

- `<data_file>`: Path to simulation `.csv` file.
- `<output_dir>`: Directory where graphs will be saved.
- `<simulation_json>`: Optional simulation JSON file.

Graphs generated:

- Temperature vs. time (Kelvin & Celsius)
- Highest/Lowest temperatures
- Temperature differences
- Simulation iterations over time

To compare simulated and measured temperatures:

```sh
plot-meas --sim <simulation_file> --meas <measurements_file> --time <max_time>
```

Run `plot-meas --help` for advanced options.

### Generating previews

#### Quick preview

```sh
tpost preview
```

Images colored with temperature gradients will be generated in `/previews`.

#### Generating animations

```sh
tpost animation
```

Animation frames will be saved in `/animations`.

To create an animation in `.webm` format, use e.g. `ffmpeg`

```
ffmpeg -framerate <fps>  -i <input_frames> <animation_path>
```

`<fps>`: frames per second
`<input_frames>`: path to animation frames - can be used with wildcards
`<animation_path>`: file path to the animation

#### Converting to Blender

```sh
tpost x3d
```

`.x3d` files will be generated in `/x3d`, allowing for rendering in Blender.

---

## Example walkthrough

### Prepare simulation

```sh
tpre prepare designs/FEMMeshGmsh.inp True
tpre get-settings designs/FEMMeshGmsh.inp designs/simulation.json
```

### Run simulation with multithreading

```sh
export OMP_NUM_THREADS=16
cd designs
ccx FEMMeshGmsh
```

### Convert results

```sh
ccx2paraview FEMMeshGmsh.frd vtk
mkdir -p vtk
mv *.vtk vtk/
```

### Post-processing

```sh
tpost csv vtk FEMMeshGmsh.sta temperature.csv
mkdir graphs
tpost plot temperature.csv graphs
tpost preview
tpost animation
```

To generate animations from ParaView:

```sh
ffmpeg -framerate 5 -i animations/so_%6d.png animations/iso.webm
ffmpeg -framerate 5 -i animations/top_%6d.png animations/top.webm
ffmpeg -framerate 5 -i animations/bottom_%6d.png animations/bottom.webm
```

### Convert to Blender

```sh
mkdir x3d
tpost x3d
```

---

## Licensing

This project is published under the [Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0).


