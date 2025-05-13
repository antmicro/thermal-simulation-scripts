#! /bin/bash

fcstd_path=$1
designs=$2
ITERATION=0
cp "$designs"/config.json "$designs"/temp_config.json
trap 'rm -f "$designs"/temp_config.json' EXIT
# Get absolute boundaries
export TMAX=$(jq -r '.temperature | .max' "$designs"/temp_config.json) 
export TMIN=$(jq -r '.temperature | .min' "$designs"/temp_config.json) 
while true; do
    iteration=$(("$iteration"+1))
    echo ""
    echo "------------------ #$iteration Iteration "
    export ITERATION="$iteration"
    tpre calc-film-coefs --fcstd "$fcstd_path" --config "$designs"/temp_config.json
    tpre parse-fcstd --fcstd "$fcstd_path" --inp "$designs" --log "$designs"
    ccx "$designs"/FEMMeshGmsh > /dev/null 2>&1
    ccx2paraview "$designs"/FEMMeshGmsh.frd vtk > /dev/null 2>&1
    mkdir -p "$designs"/vtk
    mv "$designs"/*.vtk "$designs"/vtk/
    tpost csv --vtk "$designs"/vtk --sta "$designs"/FEMMeshGmsh.sta --output "$designs"/temperature.csv > /dev/null 2>&1
    tpre bisect-temperature --config "$designs"/temp_config.json --csv "$designs"/temperature.csv
    python_exit_code=$?
    if [ $python_exit_code -eq 0 ]; then
        break
    fi
    if [ $python_exit_code -eq 2 ]; then
        break
    fi
done
