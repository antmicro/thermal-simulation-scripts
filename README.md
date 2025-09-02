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
3. [Example walkthrough](#example-simulation-walkthrough)
4. [Licensing](#licensing)

---

## Installation

### Dependencies

The `thermal-simulation-scripts` require the following dependencies:

- `Calculix` = 2.2
- `ParaView` = 6.0.0
- `python` = 3.11.2
- `pip`
- `FreeCAD` = 1.0.0
- `ccx2paraview`
- `ffmpeg`

On Debian-based systems, these dependencies can be installed using:

#### Install apt requirements

```bash
sudo apt install -y calculix-ccx python3 python3-pip libxrender1 tar wget libgl1-mesa-glx libegl1 libosmesa6 ffmpeg 
```

#### Install FreeCAD

```bash
wget -O freecad.AppImage "https://github.com/FreeCAD/FreeCAD/releases/download/1.0.0/FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage"
sudo chmod +x freecad.AppImage
./freecad.AppImage --appimage-extract
sudo mv squashfs-root /usr/local/share/freecad
sudo ln -s /usr/local/share/freecad/AppRun /usr/local/bin/freecad
echo 'export FREECAD_PATH="/usr/local/share/freecad"' >> ~/.bashrc && source ~/.bashrc
rm freecad.AppImage
```

#### Install ParaView

```bash
sudo mkdir /opt/paraview
sudo wget -O /opt/paraview/paraview.tar.gz "https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v6.0&type=binary&os=Linux&downloadFile=ParaView-6.0.0-RC1-MPI-Linux-Python3.12-x86_64.tar.gz"
sudo tar -xvzf /opt/paraview/paraview.tar.gz --strip-components=1 -C /opt/paraview
sudo rm /opt/paraview/paraview.tar.gz
echo 'export PATH=/opt/paraview/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Installation instructions

Clone the repository:

```bash
git clone http://github.com/antmicro/thermal-simulation-scripts
cd thermal-simulation-scripts
```

Installation should be performed in an isolated python environment to avoid dependency conflicts:

```sh
sudo apt update
sudo apt install pipx
pipx ensurepath
pipx install . --include-deps
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

```bash
tpre parse-fcstd --fcstd <path_to_fcstd> --inp [inp_dir] --log [settings_dir]
```

- `<path_to_fcstd>`: Path to FreeCad design file (`.FCStd`)
- `[inp_directory]`: Optional output directory for generating simulation input file (`.inp`)
- `[setting_dir]`: Optional output directory for generating simulation settings file (`.json`)

#### Generating simulation settings report

To generate report in markdown format use the following command.
The report includes data from `simulation.json`, and optionally, user comments provided under the `user_comments` key in config.json.

```bash
tpre report --sim [path_to_settings_file] --config [path_to_config_file] --report-dir [report dir]
```

- `[path_to_settings_file]`: Optional path to simulation settings file (`simulation.json`)
- `[path_to_config_file]`: Optional path to config file (`config.json`)
- `[report dir]`: Optional path to report file (`.md`)

### Running the simulation

To run the simulation using CalculiX:

```bash
ccx <path_to_inp_file>
```

Refer to the [CalculiX manual](http://www.dhondt.de/) for further details.

### Post-processing

#### Converting simulation results

```bash
ccx2paraview <frd_file> vtk
```

- `<frd_file>`: Path to the CalculiX output `.frd` file.

#### Generating CSV files

```bash
tpost csv --vtk [vtk_directory] --sta [sta_file] --output [output_file]
```

- `[vtk_directory]`: Optional path to directory with `.vtk` files.
- `[sta_file]`: Optional path to `.sta` file (output from CalculiX).
- `[output_file]`: Optional path for the output CSV file.

The output CSV contains:

- Time [s]
- Maximum/Minimum temperature in Kelvin and Celsius

### Generating graphs

```bash
tpost plot --csv [data_file] --output [output_dir] --sim [simulation_json]
```

- `[data_file]`: Optional path to simulation `.csv` file.
- `[output_dir]`: Optional directory where graphs will be saved.
- `[simulation_json]`: Optional simulation JSON file.

Graphs generated:

- Temperature vs. time (Kelvin & Celsius)
- Highest/Lowest temperatures
- Temperature differences
- Simulation iterations over time

All of them will be saved in `/graphs/`.

To compare characteristics on a common graph use:

```bash
tpost compare-csv --csv1 <1st_csv_file> --csv2 <2nd_csv_file>
```

Run `tpost compare-csv --help` for advanced options.

### Visualizing simulation in ParaView

#### Preview

```bash
tpost preview
```

Images colored with temperature gradients will be generated in `/previews/`.

#### Animations

```bash
tpost animation
```

Animation frames will be saved in `/animations/`.

To create an animation in `.webm` format, use e.g. `ffmpeg`

```bash
ffmpeg -framerate <fps>  -i <input_frames> <animation_path>
```

`<fps>`: frames per second
`<input_frames>`: path to animation frames - can be used with wildcards
`<animation_path>`: file path to the animation

---

### Visualizing simulation in Blender

Blender animations utilize Antmicro's scene setup and rendering tool [PCBooth](https://github.com/antmicro/pcbooth).

Animation scripts require:

- `.vtk` files that are obtained in [converting simulation results](#converting-simulation-results)
- `config.json` [Optional] containing `camera_custom` parameters needed if PCBooth is set to use custom camera

#### Single frame

Use this command to generate `.gltf` files from `.vtk` files:

```bash
tpost generate-gltf
```

Then convert `.gltf` file to `.blend`:

```bash
tpost gltf-to-blend --gltf <path-to-gltf>
```

Prepare the .blend for [PCBooth](https://github.com/antmicro/pcbooth) with:

```bash
tpost process-blend
```

Add color scale bar:

```bash
rsvg-convert -a -h <height> -o scale.png <colormap_scale.svg>
composite -gravity east scale.png <frame.png> <output.png>
```

where:

- `<height>` is the height of the frame in pixels.  
- `<scale.svg>` is the color bar `.svg` generated using [`generate_svg_palette`](/src/postprocessing/generate_svg_palette.py).  
- `<frame.png>` is the frame image rendered with PCBooth.  
- `<output.png>` is the output path where the frame and color bar are combined.

#### Animation

Generate gltf files with the following command:

```bash
tpost generate-gltf
```

then in the `/designs/` directory run

```bash
../src/postprocessing/blender_animation.sh <gltf_dir> 
```

where:

- `<gltf_dir>` is path to gltf directory created with `tpost generate-gltf`

### Example simulation walkthrough

#### Prepare simulation

```bash
cd designs
tpre parse-fcstd --fcstd example.FCStd
tpre report
```

#### Run simulation with multithreading

```bash
export OMP_NUM_THREADS=16
ccx FEMMeshGmsh
```

#### Convert results

```bash
ccx2paraview FEMMeshGmsh.frd vtk
mkdir -p vtk
mv *.vtk vtk/
```

#### Visualize with ParaView

Generate graphs, previews and animation frames:

```bash
tpost csv
tpost plot
tpost preview
tpost animation
```

To generate animations from ParaView output frames:

```bash
ffmpeg -framerate 5 -i animations/ISO_%6d.png animations/iso.webm
ffmpeg -framerate 5 -i animations/TOP_%6d.png animations/top.webm
ffmpeg -framerate 5 -i animations/BOTTOM_%6d.png animations/bottom.webm
```

#### Render Blender animation

```bash
tpost generate-gltf
../src/postprocessing/blender_animation.sh gltf
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

In `/designs/`, create `config.json` (or edit if it exists):

- In the `film` dictionary, specify entries for each `Heat Flux Load` constraint defined in FreeCad
- In the `temperature` dictionary, specify the `max`, `min` and `tolerance` values.

Visit [config section](#config) for in detail information.
Config for this example can be found in [config.json](/designs/config.json).

### Running the bisection algorithm

```bash
./src/preprocessing/find_coef.sh designs/example.FCStd designs/
```

The 1st argument is the path to the `.FCStd` file and the 2nd argument is the path to the `/designs/` directory.

Convergence temperature and calculated coefficients are displayed at the end of the log.

---

## Config

`config.json` is used to store information needed for automated film coefficient estimation and Blender visualization flow.
It also allows adding user comments to the simulation report. Allowed fields with their structure are listed below:

```yaml
{
   "film":{
      <constraint1_name>:[
         <characteristic_length>,
         <orientation>
      ],
      <constraint2_name>:[
         ...
      ]
   },
   "temperature":{
      "max":<max_temp>,
      "min":<min_temp>,
      "tolerance":<tol>
   },
   "camera_custom":{
      ...
   },
   "user_comments":{
      ...
   }
}
```

- `<constraint_name>` is the constraint name defined in FreeCad
- `<characteristic_length>` is height (in case of vertical plane approximation) or the smaller dimension (in case of horizontal plane approximation) [mm]
- `<orientation>` is `vertical`,`horizontal_up` or `horizontal_down`
- `<max_temp>` is the upper boundary of automatic film coefficient search area [Celsius]
- `<min_temp>` is the lower boundary of automatic film coefficient search area [Celsius]
- `<tol>` is the acceptable difference of calculated and simulated temperature in automatic film coefficient search [Celsius]
- `camera_custom` stores Blender camera data and is defined automatically with `tpost save-config`
- `user_comments` the content of it will be parsed to the README.md with `tpost report` command

## Licensing

This project is published under the [Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0).
