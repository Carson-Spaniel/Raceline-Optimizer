# Raceline Optimizer

This Python script is a raceline optimizer designed to analyze race tracks and generate optimized paths. Leveraging advanced image processing techniques, the script efficiently identifies key nodes on the track, estimates processing time, and provides a user-friendly interface for testing multiple tracks. Notably, the script takes advantage of multiprocessing to parallelize image processing tasks, significantly enhancing overall performance.

## Features

- **Image Processing:** Utilizes the Python Imaging Library (PIL) to process track images efficiently.
- **Node Detection:** Identifies nodes on the track by detecting black pixels below a specified luminance threshold.
- **Multiprocessing:** Distributes image processing tasks across multiple processes, enhancing overall performance.
- **Track Visualization:** Generates a plot of the track nodes on a 2D graph using Matplotlib.
- **Track Selection:** Allows users to choose a track from a specified folder for optimization.
- **Time Estimation:** Provides an estimated processing time based on the chosen image size.
- **Interactive Interface:** User-friendly interface for testing multiple tracks.

## Usage

1. Run the script, and it will prompt you to select a track from the 'tracks' folder.
2. Enter the desired size for processing (larger than 80, usually around 200).
3. The script will estimate and display the processing time.
4. After processing, it will show the number of nodes detected and a plot of the track nodes.
5. Choose whether to test another track.

## Dependencies

- [PIL (Pillow)](https://python-pillow.org/): Image processing library.
- [Matplotlib](https://matplotlib.org/): Plotting library.

## Configuration

- **Tracks Folder:** Ensure that the 'tracks' folder contains the track images for processing. Modify the `tracksFolder` variable in the script if your tracks are stored in a different location.

## Multiprocessing Advantage

The script optimizes image processing by employing **multiprocessing**, distributing the workload across multiple processes. This parallelization significantly enhances the overall performance and allows for faster analysis of track images.

## Future Development

The script will be extended to include path optimization algorithms, such as piecewise cubic Hermite splines, to further enhance raceline optimization.
