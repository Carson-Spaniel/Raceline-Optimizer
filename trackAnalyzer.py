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
    # Calculate luminance as a measure of intensity (brightness)
    if type(pixel) == int:
        luminance = 0
    else:
        luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
    # Check if luminance is below the threshold
    return luminance <= threshold

def process_image(image_path, size=(100, 100)):
    # Open the image
    img = Image.open(image_path)

    # Scale it to size
    img = img.resize(size, resample=Image.BOX)
    
    width, height = img.size

    i = 0
    xCoords = []
    yCoords = []
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            if is_black(pixel):
                i += 1
                xCoords.append(x)
                yCoords.append(-y+height)

    formatted_i = "{:,}".format(i)  # Use format to add commas to the number

    return xCoords,yCoords,f'\nNodes in track: {formatted_i}'

def plotNodes(xCoords, yCoords):
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

def timeEstimate(x):
    return round((.00000067*(x**2)+.1), 2)

def main():
    tracksFolder = 'tracks'
    while True:
        image = printTracks(tracksFolder)
        imagePath = f'{tracksFolder}/{image}'
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
        print(f'Estimated time is: {timeEstimate(size)} seconds.')

        startTime = time.time()
        x, y, numNodes = process_image(imagePath, (size, size))
        endTime = time.time()
        print(f'Actual time was: {round(endTime-startTime,2)} seconds.')

        print(numNodes) # Prints the number of nodes in the track 

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