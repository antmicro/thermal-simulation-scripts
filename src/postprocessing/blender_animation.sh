#!/bin/bash
GLTF_DIR=$1
BLENDER_MATERIALS=$2
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
mkdir -p blends
echo "Merging material..."
tpost merge-materials --lib "$BLENDER_MATERIALS" --lib-thermal "$SCRIPT_DIR/material.blend" --output-material "merged_material.blend"
echo "Processing GLTF..."
for GLTF in "$GLTF_DIR"/*.gltf; do
    if [[ -f "$GLTF" ]]; then
        name=$(basename "$GLTF" .gltf)
        echo "Converting $name to .blend"
        tpost gltf-to-blend --gltf "$GLTF" --blend "temp.blend" &>/dev/null
        echo "Preparing $name for pcbooth"
        tpost process-blend --input "temp.blend" --output "temp.blend" --material "merged_material.blend" --config "config.json" &>/dev/null
        echo "Rendering $name frame"
        pcbooth -b "temp.blend" -c thermal &>/dev/null
        mv temp.blend blends/$name.blend
        latest_file=$(find renders -maxdepth 1 -type f -printf "%T@ %p\n" | sort -n | tail -n 1 | cut -d' ' -f2-)
        mv "$latest_file" "renders/$name.png"
    fi
done
echo "Processing completed"