#!/bin/bash

# Create gifs directory if it doesn't exist
mkdir -p gifs

# Convert each MP4 to GIF with good quality settings
for video in videos/*.mp4; do
    filename=$(basename "$video" .mp4)
    echo "Converting $filename.mp4 to GIF..."
    
    # Convert to GIF with good quality settings
    ffmpeg -i "$video" \
        -vf "fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
        -y "gifs/${filename}.gif"
done

echo "Conversion complete! GIFs are in the gifs directory." 