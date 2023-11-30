from PIL import Image
import matplotlib.pyplot as plt
import os
import time
from multiprocessing import Pool, freeze_support
import math

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

def processImageSection(args):
    image_section, size, offset = args
    width, height = size

    i = 0
    xCoords = []
    yCoords = []
    for y in range(height):
        for x in range(width):
            pixel = image_section.getpixel((x, y))
            if is_black(pixel):
                i += 1
                xCoords.append(x + offset[0])
                yCoords.append(-y + height + offset[1])

    return xCoords, yCoords, i

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
        try:
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
        except Exception as e:
            print('Invalid choice.')

    print(f"You selected: {chosenTrack.split('.')[0].capitalize()}")
    return chosenTrack

def timeEstimate(x):
    return round((x/os.cpu_count()/43), 2)

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
                    elif size > (1500*os.cpu_count()):
                        print(f'Enter a size smaller than','{:,}.'.format(1500*os.cpu_count()))
                    else:
                        break
                else:
                    print("Enter a positive number.")
            except Exception as e:
                print("Invalid size.")

        print('\nBuilding Track...')
        # print(f'Estimated time is: {timeEstimate(size)} seconds.')

        # print(f'CPU count: {math.floor(os.cpu_count()*.8)}')

        startTime = time.time()

        # Open image
        img = Image.open(imagePath)

        # Scale it to size
        img = img.resize((size, size), resample=Image.BOX)

        # Split the image into sections
        width, height = img.size
        num_processes = os.cpu_count()  # Number of processes
        section_width = width // num_processes
        image_sections = [(img.crop((i * section_width, 0, (i + 1) * section_width, height)), (section_width, height), (i * section_width, 0)) for i in range(num_processes)]

        # Evaluates if multiprocessing is needed or will it slow it down
        if size > 1750:
             # Create a multiprocessing Pool
            pool = Pool()

            # Use pool.map() to run the function in parallel
            results = pool.map(processImageSection, image_sections)

            pool.close()
            pool.join()

            # Combine the results
            xCoords = sum((result[0] for result in results), [])
            yCoords = sum((result[1] for result in results), [])
            total_nodes = sum(int(result[2]) for result in results)
        else:
            xCoords, yCoords, total_nodes = processImageSection([img,(size,size),(0,0)])

        numNodes = "{:,}".format(total_nodes)

        endTime = time.time()

        print(f'\nWait time was: {round(endTime-startTime,2)} seconds.')
        print(f'Number of track nodes: {numNodes}') # Number of sections the track was split into

        plotNodes(xCoords, yCoords)
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

if __name__ == "__main__":
    freeze_support()
    main()