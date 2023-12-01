# Raceline Optimizer

This Python script serves as a raceline optimizer, featuring a carefully crafted algorithm to analyze race tracks and determine precise paths. The algorithm intelligently navigates tracks, avoiding dead ends, and enhances accuracy in raceline generation. Leveraging advanced image processing techniques, the script effectively identifies crucial nodes on the track. Additionally, the utilization of multiprocessing optimizes image analysis, ensuring efficient and rapid track optimization.

## Features

- **Image Processing:** Utilizes the Python Imaging Library (PIL) to process track images efficiently.
- **Node Detection:** Identifies nodes on the track by detecting black pixels below a specified luminance threshold.
- **Multiprocessing:** Distributes image processing tasks across multiple processes, enhancing overall performance.
- **Path Finding Algorithm:** Implements a custom algorithm to traverse paths and return viable routes that lead back to the starting point.
- **Concurrent Events:** Uses concurrent events to find paths faster and optimize the exploration process.
- **Track Visualization:** Generates a plot of the track nodes on a 2D graph using Matplotlib.
- **Track Selection:** Allows users to choose a track from a specified folder for optimization.
- **Time Estimation:** Provides an estimated processing time based on the chosen image size.
- **Interactive Interface:** User-friendly interface for testing multiple tracks.

## Path Finding Algorithm

The script employs a custom path finding algorithm to explore potential routes on the track. The algorithm intelligently traverses paths, avoiding dead ends, and returns paths that lead back to the starting point. This ensures that the generated racelines are not only optimized but also practical for racing.

## Multiprocessing Advantage

The script optimizes image processing by employing **multiprocessing**, distributing the workload across multiple processes. This parallelization significantly enhances overall performance and allows for faster analysis of track images. The use of multiprocessing is carefully balanced to ensure efficiency, especially when dealing with larger track sizes.

## Concurrent Events for Faster Exploration

To expedite the path finding process, the script utilizes concurrent events, allowing for faster exploration of potential paths. This optimization is particularly beneficial when dealing with complex tracks, improving the overall efficiency of the raceline optimization.

## Future Development

Future updates to the script will include a more sophisticated visualization method for each optimized path. This enhancement aims to create smoother and more drivable racelines, improving the script's practicality for racing applications. Additionally, the script will explore advanced path optimization algorithms, such as piecewise cubic Hermite splines, to further enhance raceline optimization.

## Usage

1. Run the script, and it will prompt you to select a track from the 'tracks' folder.
2. Enter the desired size for processing (larger than 50, usually around 80-100).
3. The script will estimate and display the processing time.
4. After processing, it will show the number of nodes detected and a plot of the track nodes.
5. Choose whether to test another track.

## Dependencies

- [PIL (Pillow)](https://python-pillow.org/): Image processing library.
- [Matplotlib](https://matplotlib.org/): Plotting library.

## Configuration

- **Tracks Folder:** Ensure that the 'tracks' folder contains the track images for processing. Modify the `tracksFolder` variable in the script if your tracks are stored in a different location.
