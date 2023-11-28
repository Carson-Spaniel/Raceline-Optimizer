from PIL import Image
import matplotlib.pyplot as plt
import os
import numpy as np
import time
from collections import deque

class BackgroundColors:
    RESET = '\033[0m'
    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    PURPLE = '\033[45m'
    CYAN = '\033[46m'
    WHITE = '\033[47m'

def is_black(pixel, threshold=100):
    # Assuming pixel is in RGB format
    # Calculate luminance as a measure of intensity (brightness)
    if type(pixel) == int:
        luminance = 0
    else:
        luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
    # Check if luminance is below the threshold
    return luminance <= threshold

def process_image(image_path, output_file, initial_target_size=(100, 100), output_image_path='output.jpg'):
    images = []
    img = Image.open(image_path)
    img = img.resize(initial_target_size, resample=Image.BOX)
    width, height = img.size
    results = []

    # for y in range(height):
    #     row = []
    #     nodes = deque()
    #     for x in range(width):
    #         pixel = img.getpixel((x, y))
    #         is_black_pixel = is_black(pixel)
    #         row.append('1' if is_black_pixel else '0')
    #         if is_black_pixel:
    #             negX = width - 1
    #             while negX != x:
    #                 if is_black(img.getpixel((negX, y))):
    #                     nodes.append('1')
    #                 elif '1' in nodes:
    #                     nodes.append('0')
    #                 else:
    #                     nodes.append('0')
    #                 negX -= 1
    #             while nodes:
    #                 row.append(nodes.pop())
    #             break
    #     results.append(''.join(row))
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = img.getpixel((x, y))
            if is_black(pixel):
                row.append(1)
            else:
                row.append(0)
        grid.append(row)

    return grid

def addNodes(grid):
    # Print the grid for visualization
    i = 0
    rowNum = 0
    xCoords = []
    yCoords = []
    for row in grid:
        rowNumStr = str(rowNum)
        if rowNum < 100:
            rowNumStr = '0'+str(rowNum)
            if rowNum < 10:
                rowNumStr = '0'+str(rowNumStr)
        colNum = 0
        if 1 in row:
            for node in row:
                if node == 1:
                    i += 1
                    xCoords.append(colNum)
                    yCoords.append(-rowNum+len(grid))
                colNum += 1
        rowNum +=1

    formatted_i = "{:,}".format(i)  # Use format to add commas to the number
    print(f'\nNumber of nodes: {formatted_i}')
    return xCoords,yCoords

def plotNodes(xCoords, yCoords):
    # Assuming x_nodes and y_nodes are lists containing the x and y coordinates of nodes
    plt.plot(xCoords, yCoords, '.', label='Track Nodes')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Track Map with Nodes')
    plt.legend()
    plt.show()

def printTracks(tracksFolder):
    # Get the absolute path based on the current working directory
    absoluteTracksFolder = os.path.abspath(tracksFolder)

    # Get a list of files in the tracks folder
    trackFiles = [f for f in os.listdir(absoluteTracksFolder) if os.path.isfile(os.path.join(absoluteTracksFolder, f))]

    # Print out the available tracks
    print("\nAvailable Tracks:")
    for i, trackFile in enumerate(trackFiles, start=1):
        print(f"{i}. {trackFile.split('.')[0].capitalize()}")

    while True:
        # Prompt the user to choose a track
        selected_track_index = int(input("\nEnter the number of the track you want to choose: ")) - 1
        if selected_track_index == -1:
            print('Invalid choice.')
        else:
            try:
                # Retrieve the chosen track filename
                chosenTrack = trackFiles[selected_track_index]
                break
            except Exception as e:
                print('Selected option not in list.')

    print(f"You selected: {chosenTrack.split('.')[0].capitalize()}")
    return chosenTrack

def main():
    def timeEstimate(x):
        return round((.0000007 * (x**2) + .1), 2)
    # Specify the relative path to your tracks folder
    tracksFolder = 'tracks'
    while True:
        image = printTracks(tracksFolder)
        imagePath = f'{tracksFolder}/{image}'
        output_file = 'output.txt'  # Output file for the track in 1s and 0s
        while True:
            try:
                size = int(input("\nEnter the size you want: "))
                if size > 0:
                    if size < 80:
                        print('Enter a size larger than 80.')
                    else:
                        break
                else:
                    print("Enter a positive number.")
            except Exception as e:
                print("Invalid size.")
        print('\nBuilding Track...')
        print(f'Estimated Time is: {timeEstimate(size)} seconds.')

        startTime = time.time()
        grid = process_image(imagePath, output_file, (size, size), output_image_path='output.jpg')
        endTime = time.time()
        print(f'Actual time was: {round(endTime-startTime,2)} seconds.')

        x, y =  addNodes(grid)
        plotNodes(x, y)
        more = False
        while True:
            choice = str(input('Test another track? (y/n): '))
            if choice == 'y':
                more = True
                break
            elif choice == 'n':
                more = False
                break
            else:
                print('Invalid choice.')
        if not more:
            break

main()