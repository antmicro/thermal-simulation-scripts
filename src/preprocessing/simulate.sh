#! /bin/bash

fcstd_path=$1
designs=$2

# Prepare
unset "$BISECTED_TEMP"
cp "$designs"/config.json "$designs"/temporary_config.json

while [ -z "$BISECTED_TEMP" ]
do
tpre get-coef "$fcstd_path" "$designs"/temporary_config.json
tpre parse-fcstd "$fcstd_path" "$designs" "$designs"
tpre prepare "$designs"/FEMMeshGmsh.inp True
export OMP_NUM_THREADS=12
ccx "$designs"/FEMMeshGmsh
ccx2paraview "$designs"/FEMMeshGmsh.frd vtk
mkdir -p "$designs"/vtk
mv "$designs"/*.vtk "$designs"/vtk/
tpost csv "$designs"/vtk "$designs"/FEMMeshGmsh.sta "$designs"/temperature.csv
tpre bisect-temperature "$designs"/temporary_config.json"$designs"/temperature.csv
done
echo "Bisected temperature is $BISECTED_TEMP"
