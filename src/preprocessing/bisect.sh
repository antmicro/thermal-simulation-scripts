#! /bin/bash

fcstd_path=$1
designs=$2
ITERATION=0
# Prepare
cp "$designs"/config.json "$designs"/temporary_config.json
rm "$designs"/bisect_log.csv
while true; do
    iteration=$(("$iteration"+1))
    export ITERATION="$iteration"
    tpre get-coef "$fcstd_path" "$designs"/temporary_config.json
    tpre parse-fcstd "$fcstd_path" "$designs" "$designs"
    tpre prepare "$designs"/FEMMeshGmsh.inp True
    export OMP_NUM_THREADS=12
    ccx "$designs"/FEMMeshGmsh > /dev/null 2>&1
    ccx2paraview "$designs"/FEMMeshGmsh.frd vtk > /dev/null 2>&1
    mkdir -p "$designs"/vtk
    mv "$designs"/*.vtk "$designs"/vtk/
    tpost csv "$designs"/vtk "$designs"/FEMMeshGmsh.sta "$designs"/temperature.csv > /dev/null 2>&1
    tpre bisect-temperature "$designs"/temporary_config.json "$designs"/temperature.csv "$designs"/bisect_log.csv
    if [ $? -eq 0 ]; then
        break
    fi
done

