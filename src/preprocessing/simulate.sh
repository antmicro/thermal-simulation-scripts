#! /bin/bash

fcstd_path=$1
designs=$2

tpre parse-config "$fcstd_path" "$designs"/coef_config.json
tpre parse-fcstd "$fcstd_path" "$designs" "$designs"
tpre prepare "$designs"/FEMMeshGmsh.inp True
export OMP_NUM_THREADS=12
ccx "$designs"/FEMMeshGmsh
ccx2paraview "$designs"/FEMMeshGmsh.frd vtk
mkdir -p "$designs"/vtk
mv "$designs"/*.vtk "$designs"/vtk/
tpost csv "$designs"/vtk "$designs"/FEMMeshGmsh.sta "$designs"/temperature.csv
