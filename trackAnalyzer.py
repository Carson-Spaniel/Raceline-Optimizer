from PIL import Image
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import os
import time
from multiprocessing import Pool, freeze_support
import concurrent.futures
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
    plt.plot(xCoords, yCoords, '.', label='Track Nodes', color='black')
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

getMove = {
    '0111':['0011','0111','0100'],
    '0100':['0111','0100','0101'],
    '0101':['0100','0101','0001'],
    '0011':['1111','0011','0111'],
    '0001':['0101','0001','1101'],
    '1111':['0011','1111','1100'],
    '1100':['1111','1100','1101'],
    '1101':['1100','1101','0001']
}

def choosePath(moves, currPosX, currPosY, xCoords, yCoords, startX, startY, visited):
    nextMove = []
    nextDist = 1e7 # Infinity
    nextMoveStr = moves[0]
    for move in moves:
        iNeg = int(move[0])
        jNeg = int(move[2])
        i = int(move[1])
        j = int(move[3])
        if iNeg:
            i *= -1
        if jNeg:
            j *= -1
        nextX = currPosX + j
        nextY = currPosY + i
        coords = (nextX,nextY)
        if nextX in xCoords and nextY in yCoords:
            xIndex = [i for i, x in enumerate(xCoords) if x == nextX]
            yIndex = [i for i, y in enumerate(yCoords) if y == nextY]

            if any(index in yIndex for index in xIndex) and coords not in visited:
                xDist = abs(startX - nextX)
                yDist = abs(startY - nextY)
                dist = xDist + yDist
                if dist < nextDist:
                    nextDist = dist
                    nextMove.append(coords)
                    nextMoveStr = move
        else:
            try:
                nextMove.pop()
            except IndexError:
                nextMove = []
    try:
        return (nextMove[-1], nextMoveStr)
    except IndexError:
        return ((None, None), nextMoveStr)

def findStart(startX, startY, direction, startDirX, startDirY, xCoords, yCoords, numNodes, concurrentProcesses):
    nodeCount = 1e7
    numberToBeatLow = round(numNodes * .27,0)
    print(f'\nSearching paths with at least {numberToBeatLow} nodes.\n')
    path = None
    pathCounter = 1
    nodes = 0
    pathsChecked = 0
    if concurrentProcesses:
        countNeeded = 1
    else:
        countNeeded = 6
    while path == None or pathCounter < countNeeded:
        currPosX = startDirX
        currPosY = startDirY
        move = direction
        currPathX = [currPosX]
        currPathY = [currPosY]
        movesPath = []
        visited = [(currPosX,currPosY)]
        try:
            i = 0
            nodes = 0
            while (currPosX,currPosY) != (startX, startY):
                if nodes > 500:
                    return path, nodes, pathsChecked
                moves = getMove[move]
                coords, move = choosePath(moves, currPosX, currPosY, xCoords, yCoords, startX, startY, visited)
                currPosX, currPosY = coords
                if currPosX == None:
                    if i == 100:
                        raise Exception
                    currPosX = currPathX.pop()
                    currPosY = currPathY.pop()
                    moves = movesPath.pop()
                    move = moves[1]
                    visited.pop()
                    i += 1
                    nodes -= 1
                else:
                # if currPosX:
                    currPathX.append(currPosX)
                    currPathY.append(currPosY)
                    movesPath.append(moves)
                    visited.append((currPosX, currPosY))
                    nodes += 1
            
            if nodes <= nodeCount and moves[1] == direction:
                print('Path found.')
                print(f'{nodes} Nodes.')
                print(f'Checked {pathsChecked} paths.\n')
                # print('Same distance path found')
                nodeCount = nodes
                path = (currPathX, currPathY)
                pathCounter += 1
                pathsChecked += 1
                if concurrentProcesses:
                    showPath(currPathX, currPathY, xCoords, yCoords, startDirX, startDirY, startX, startY, nodeCount)

        except Exception as e:
            print("Path not found.")
            print(e)
            pathsChecked += 1
            print(pathsChecked)
            path = (currPathX, currPathY)
            if pathsChecked > 50:
                return path, nodes, pathsChecked
            # if nodes > numberToBeatLow and nodes < numberToBeatHigh:
            #     pathCounter += 1
        return (currPathX, currPathY), nodes, pathsChecked

    return path, nodes, pathsChecked

def start(x,y,direction, xCoords, yCoords, numNodes):
    iNeg = int(direction[0])
    jNeg = int(direction[2])
    i = int(direction[1])
    j = int(direction[3])
    if iNeg:
        i *= -1
    if jNeg:
        j *= -1

    concurrentProcesses = False

    startTime = time.time()

    if concurrentProcesses:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {executor.submit(findStart, x, y, direction, x+j, y+i, xCoords, yCoords, numNodes, concurrentProcesses) for _ in range(math.floor(os.cpu_count()*.6))}
            done, not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

            # Get the result from the first completed task
            results = next(iter(done)).result()

    else:
        results = findStart(x,y,direction,x+j,y+i,xCoords,yCoords, numNodes, concurrentProcesses)
    
    endTime = time.time()

    print(f'Wait time was: {round(endTime-startTime,2)} seconds.')

    # if not concurrentProcesses:
    showPath(results[0][0], results[0][1], xCoords, yCoords, x+j, y+i, x, y, results[1])

# def showPath(xPath, yPath, xCoords, yCoords, startX, startY, finishX, finishY, numNodes):
#     # Extract marked points (every 5th point)
#     markedX = xPath[::3]
#     markedY = yPath[::3]

#     # Adding the very last point to the marked points
#     markedX.append(xPath[-1])
#     markedY.append(yPath[-1])

#     # Plotting with markers
#     plt.plot(xCoords, yCoords, '.', label='Track Nodes', color='black')
#     plt.plot(markedX, markedY, 'd', label='Control Points', color='b')

#     # Connect the marked points with lines
#     plt.plot(markedX, markedY, '-', color='b')
#     plt.plot(startX, startY, 'o', label='Start Node', color='g')
#     plt.plot(finishX, finishY, 'D', label='Finish Node', color='r')
#     plt.xlabel('X-axis')
#     plt.ylabel('Y-axis')
#     plt.title(f'Number of nodes in path: {numNodes}', loc='center')
#     plt.legend()
#     plt.show()

def showPath(xPath, yPath, xCoords, yCoords, startX, startY, finishX, finishY, numNodes):
    # Point to divide track into
    splitPoint = 1

    # Extract marked points
    markedX = xPath[::splitPoint]
    markedY = yPath[::splitPoint]

    # Adding the very last point to the marked points
    markedX.append(startX)
    markedY.append(startY)

    # Connect the marked points with lines
    plt.plot(markedX, markedY, '-', color='b')

    # Find indices of duplicate x values
    _, idx = np.unique(markedX, return_index=True)
    duplicates = np.setdiff1d(np.arange(len(markedX)), idx)

    # Split the track into sections based on duplicate x values
    sections = np.split(np.c_[markedX, markedY], duplicates+1)

    # Plotting with markers
    plt.plot(xCoords, yCoords, '.', label='Track Nodes', color='black')
    plt.plot(markedX, markedY, 'k-', label='Control Points', color='b')

    # # Connect the marked points with lines for each section
    # for section in sections:
    #     x, y = section.T
    #     if len(x) >= 4:  # Only interpolate if there are enough points
    #         tck = make_interp_spline(np.arange(len(x)), section)
    #         xnew = np.linspace(0, len(x)-1, 500)
    #         xnew, ynew = tck(xnew).T
    #         plt.plot(xnew, ynew, '-', color='b')

    plt.plot(startX, startY, 'D', label='Start Node', color='g')
    plt.plot(finishX, finishY, 'D', label='Finish Node', color='r')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title(f'Number of nodes in path: {numNodes}', loc='center')
    plt.legend()
    plt.show()

def main():
    tracksFolder = 'tracks'
    while True:
        image = printTracks(tracksFolder)
        imagePath = f'{tracksFolder}/{image}'
        while True:
            try:
                size = int(input("\nEnter the size you want: "))
                if size > 0:
                    if size < 50:
                        print('Enter a size larger than 50.')
                    elif size > (1500*os.cpu_count()):
                        print(f'Enter a size smaller than','{:,}.'.format(1500*os.cpu_count()))
                    else:
                        break
                else:
                    print("Enter a positive number.")
            except Exception as e:
                print("Invalid size.")

        print('\nBuilding Track...')

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

        print('\nFind the starting X and Y coordinates as well as the starting direction.')
        plotNodes(xCoords, yCoords)

        directions = {
            1:['N','0100'],
            2:['NE','0101'],
            3:['E','0001'],
            4:['SE','1101'],
            5:['S','1100'],
            6:['SW','1111'],
            7:['W','0011'],
            8:['NW','0111'],
        }

        while True:
            try:
                # TODO implement ways to not have to restart
                xCoord = int(input('Enter starting X coordinate: '))
                if xCoord <= width:
                    yCoord = int(input('Enter starting Y coordinate: '))
                    if yCoord <= height:
                        print('Relative cardinal direction of the track:')
                        # TODO add int error checking
                        for key in directions:
                            print(f'{key}. {directions[key][0]}')
                        try:
                            choice = directions[int(input('\nPick a starting direction: '))]
                            print(f"You selected: {choice[0]}")
                            break
                        except Exception as e:
                            print('Invalid choice.')
                    else:
                        print("Y Coordinate not in graph bounds.")
                else:
                    print("X Coordinate not in graph bounds.")
            except Exception as e:
                print('Invalid coordinate.')

        start(xCoord,yCoord,choice[1], xCoords, yCoords, total_nodes)

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