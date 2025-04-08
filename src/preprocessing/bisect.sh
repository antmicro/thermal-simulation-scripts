#! /bin/bash

fcstd_path=$1
designs=$2
ITERATION=0
cp "$designs"/config.json "$designs"/temporary_config.json
[ -f "$designs"/bisect_log.csv ] && rm "$designs"/bisect_log.csv
trap 'rm -f "$designs"/temporary_config.json' EXIT
while true; do

    iteration=$(("$iteration"+1))
    echo ""
    echo "------------------ #$iteration Iteration "
    export ITERATION="$iteration"
    tpre get-coef "$fcstd_path" "$designs"/temporary_config.json
    tpre parse-fcstd "$fcstd_path" "$designs" "$designs"
    tpre prepare "$designs"/FEMMeshGmsh.inp True > /dev/null 2>&1
    export OMP_NUM_THREADS=12
    ccx "$designs"/FEMMeshGmsh > /dev/null 2>&1
    ccx2paraview "$designs"/FEMMeshGmsh.frd vtk > /dev/null 2>&1
    mkdir -p "$designs"/vtk
    mv "$designs"/*.vtk "$designs"/vtk/
    tpost csv "$designs"/vtk "$designs"/FEMMeshGmsh.sta "$designs"/temperature.csv > /dev/null 2>&1
    tpre bisect-temperature "$designs"/temporary_config.json "$designs"/temperature.csv "$designs"/bisect_log.csv
    python_exit_code=$?
    if [ $python_exit_code -eq 0 ]; then
        break
    fi
    if [ $python_exit_code -eq 2 ]; then
        break
    fi
done
