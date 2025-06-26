#!/bin/bash
GLTF_DIR=$1
height=$(yq '.thermal.RENDERER.IMAGE_HEIGHT' blendcfg.yaml )
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WD=$PWD
echo "Converting colormap..."
rsvg-convert -a -h "$height" -o "$SCRIPT_DIR"/colormap_scale.png "$SCRIPT_DIR"/colormap_scale.svg
mkdir -p blends
for GLTF in "$GLTF_DIR"/*.gltf; do
    if [[ -f "$GLTF" ]]; then
        name=$(basename "$GLTF" .gltf)
        echo "Converting $name to .blend"
        tpost gltf-to-blend --gltf "$GLTF" --blend "temp.blend" &>/dev/null
        echo "Preparing $name for pcbooth"
        tpost process-blend --input "temp.blend" --output "temp.blend" --material "$SCRIPT_DIR/material.blend" --config "config.json" &>/dev/null
        echo "Rendering $name frame"
        pcbooth -b "temp.blend" -c thermal &>/dev/null
        mv temp.blend blends/$name.blend
        latest_file=$(find renders -maxdepth 1 -type f -printf "%T@ %p\n" | sort -n | tail -n 1 | cut -d' ' -f2-)
        mv "$latest_file" "renders/$name.png"
        echo "Merging $name scale with frame"
        composite -gravity east "$SCRIPT_DIR"/colormap_scale.png renders/"$name".png renders/"$name".png
    fi
done
echo "Processing frames..."
trap 'cd "$WD"' EXIT
cd renders || EXIT
ffmpeg -framerate 25 -i %04d.png -c:v libvpx-vp9 -pix_fmt yuva420p10le -lossless 1 -vf scale=iw:-2 animation.webm &>/dev/null
ffmpeg -framerate 25 -i %04d.png -vf palettegen palette.png &>/dev/null
ffmpeg -framerate 25 -i %04d.png -i palette.png -lavfi "paletteuse" animation.gif &>/dev/null
echo "Processing completed"