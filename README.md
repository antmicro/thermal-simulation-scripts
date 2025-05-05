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
wget -O ./freecad.AppImage https://github.com/FreeCAD/FreeCAD/releases/download/1.0.0/FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage
sudo chmod +x freecad.AppImage
./freecad.AppImage --appimage-extract
sudo mv squashfs-root /usr/local/share/freecad
sudo ln -s /usr/local/share/freecad/AppRun /usr/local/bin/freecad
echo 'export FREECAD_PATH="/usr/local/share/freecad"' >> ~/.bashrc && source ~/.bashrc
rm freecad.AppImage
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

The first step in a thermal simulation is to define constraints for each surface of the 3D model and convert it into a mesh using FreeCAD. This process results in a `.FCStd` format file.

### Pre-processing

This step prepares the simulation. The `.FCStd` file should be sufficient, but additional settings can be configured.

#### Generating inp file

```sh
tpre parse-fcstd <path_to_fcstd> <inp_dir> <settings_dir>
```

- `<path_to_fcstd>`: Path to freecad design file (.fcstd)
- `<inp_directory>`: Output directory for generating simulation input file (.inp)
- `<setting_dir>`: Output directory for generating simulation settings file (.json)

#### Preparing the simulation

```sh
tpre prepare <path_to_inp_file> <simulate_temperature_only>
```

- `<path_to_inp_file>`: Path to the CalculiX input file.
- `<simulate_temperature_only>`: Set to `true` to simulate only temperature and heat flux.

#### Checking simulation settings

```sh
tpre get-settings <path_to_inp_file> <output_file>
```

- `<path_to_inp_file>`: Path to the CalculiX `.inp` file.
- `<path_to_settings_file>`: Path to simulation settings file (.json)

#### Generating simulation settings report

```sh
tpre report <path_to_settings_file> <report dir>
```

- `<path_to_settings_file>`: Path to simulation settings file (.json)
- `<report dir>`: Path to report file (.md)

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
tpost plot <data_file> [output_dir] [simulation_json]
```

- `<data_file>`: Path to simulation `.csv` file.
- `[output_dir]`: Optional directory where graphs will be saved.
- `[simulation_json]`: Optional simulation JSON file.

Graphs generated:

- Temperature vs. time (Kelvin & Celsius)
- Highest/Lowest temperatures
- Temperature differences
- Simulation iterations over time

All of them will be saved in `/graphs`.

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

## Example simulation walkthrough

### Prepare simulation

```sh
tpre parse-fcstd designs/example.FCStd ./designs ./designs
tpre prepare designs/FEMMeshGmsh.inp True
tpre get-settings designs/FEMMeshGmsh.inp designs/simulation.json
tpre report ./designs/simulation.json ./designs
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

Generate graphs, previews and animation frames:
```sh
tpost csv vtk FEMMeshGmsh.sta temperature.csv
tpost plot temperature.csv
tpost preview
tpost animation
```

To generate animations from ParaView output frames:

```sh
ffmpeg -framerate 5 -i animations/ISO_%6d.png animations/iso.webm
ffmpeg -framerate 5 -i animations/TOP_%6d.png animations/top.webm
ffmpeg -framerate 5 -i animations/BOTTOM_%6d.png animations/bottom.webm
```

### Convert to Blender

```sh
tpost x3d
```

---

## Automated film coefficient estimation

Simulating natural convection requires calculating the film coefficients for the surfaces.
These coefficients can be estimated using an initial guess for the surface temperature.
However, since predicting the surface temperature accurately is complex, this method alone may not provide precise results.

The Bisection Algorithm is used to improve accuracy.
It iterates over a given temperature range, comparing the simulated final temperature with the temperature assumed in the film coefficient calculator.
With each iteration, the temperature range is reduced until the difference between the simulated and assumed temperatures is within a specified tolerance.
Then the algorithm returns the final temperature and the corresponding film coefficients.

**Using sparse mesh is recommended for this algorithm**

### Defining constraints in FreeCad

Define the `Heat Flux Load` constraints in FreeCad.
Then assign each face that dissipates heat to one of them.
Rename each `Heat Flux Load` to a custom name.

In this example, 3 `Heat Flux Load` constraints were defined:

* vertical
* horizontal_up
* horizontal_down

### Defining the config

In `/designs`, create `config.json`.
In the `film` dictionary, specify entries for each `Heat Flux Load` constraint defined in FreeCad:

```bash
<constraint name> : [ <characteristic length>, <orientation>]
```

where:

* `<constraint name>` is the constraint name defined in FreeCad
* `<characteristic length>` is height (in case of vertical plane approximation) or the smaller dimension (in case of horizontal plane approximation) in [mm]
* `<orientation>` is `vertical`,`horizontal_up` or `horizontal_down`

In the `temperature` dictionary, specify the `max`, `min` and `tolerance` values [Celsius].

A config for this example can be found in [config.json](/designs/config.json).

### Running the bisection algorithm

```bash
./src/preprocessing/bisect.sh ./designs/example.FCStd ./designs
```

The 1st argument is the path to the `.FCStd` file and the 2nd argument is the path to the `/designs` directory.

Convergence temperature and calculated coefficients are displayed at the end of the log.

---

## Licensing

This project is published under the [Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0).
