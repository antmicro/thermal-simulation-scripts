#! /bin/bash

fcstd_path=$1
designs=$2

# Prepare
cp "$designs"/config.json "$designs"/temporary_config.json

while true; do
    tpre get-coef "$fcstd_path" "$designs"/temporary_config.json
    tpre parse-fcstd "$fcstd_path" "$designs" "$designs"
    tpre prepare "$designs"/FEMMeshGmsh.inp True
    export OMP_NUM_THREADS=12
    ccx "$designs"/FEMMeshGmsh > /dev/null 2>&1
    ccx2paraview "$designs"/FEMMeshGmsh.frd vtk > /dev/null 2>&1
    mkdir -p "$designs"/vtk
    mv "$designs"/*.vtk "$designs"/vtk/
    tpost csv "$designs"/vtk "$designs"/FEMMeshGmsh.sta "$designs"/temperature.csv > /dev/null 2>&1
    tpre bisect-temperature "$designs"/temporary_config.json "$designs"/temperature.csv
    if [ $? -eq 0 ]; then
        echo "Convergence"
        break
    else
        echo "No convergence, continuing"
    fi
done

