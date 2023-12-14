from PIL import Image
import matplotlib.pyplot as plt
# from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import os
import time
from multiprocessing import Pool, freeze_support
import concurrent.futures
import math

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

def plotNodes(xCoords, yCoords, trackNodes):
    plt.plot(xCoords, yCoords, '.', label='Track Nodes', color='black')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title(f'Number of nodes in track: {trackNodes}')
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

# Dictionary of moves each with a specific direction
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

# Dictionary of opposite directions
getOpposite = {
    '0111':'1101',
    '0100':'1100',
    '0101':'1111',
    '0011':'0001',
    '0001':'0011',
    '1111':'0101',
    '1100':'0100',
    '1101':'0111'
}

def choosePath(moves, currPosX, currPosY, xCoords, yCoords, startX, startY, visited):
    nextMove = []
    nextDist = 1e7 # Infinity
    nextMoveStr = moves[0]
    for move in moves:
        # Extract the move based on the string
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
        # If the coordinates are in bounds of the track
        if nextX in xCoords and nextY in yCoords:
            xIndex = [i for i, x in enumerate(xCoords) if x == nextX]
            yIndex = [i for i, y in enumerate(yCoords) if y == nextY]
            # If the coordinates have not been visited
            if any(index in yIndex for index in xIndex) and coords not in visited:
                xDist = abs(startX - nextX)
                yDist = abs(startY - nextY)
                dist = xDist + yDist
                # If move is local minimum set to next move
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
    path = None
    pathCounter = 1
    failed = 0
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
        runningX = []
        runningY = []
        nodes = 0
        try:
            # Keeps checking if the position is back at the start
            while (currPosX,currPosY) != (startX, startY):
                if failed == 1000:
                    return (runningX, runningY)
                moves = getMove[move]
                coords, move = choosePath(moves, currPosX, currPosY, xCoords, yCoords, startX, startY, visited)
                currPosX, currPosY = coords
                # If no current position, backtrack
                if currPosX == None:
                    # To prevent from infinite loop, if it fails 1000 times it breaks out returning the latest path
                    if failed == 1000:
                        raise Exception
                    currPosX = currPathX.pop()
                    currPosY = currPathY.pop()
                    moves = movesPath.pop()
                    move = moves[1]
                    visited.pop()
                    failed += 1
                    nodes -= 1
                else:
                    currPathX.append(currPosX)
                    currPathY.append(currPosY)
                    runningX.append(currPosX)
                    runningY.append(currPosY)
                    movesPath.append(moves)
                    visited.append((currPosX, currPosY))
                    nodes += 1
            
            if nodes <= nodeCount and moves[1] == direction:
                nodeCount = nodes
                path = (currPathX, currPathY)
                pathCounter += 1
                if concurrentProcesses:
                    showPath(currPathX, currPathY, xCoords, yCoords, startDirX, startDirY, nodeCount)

        except Exception as e:
            failed += 1
            path = (currPathX, currPathY)

    return path

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

    if concurrentProcesses:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {executor.submit(findStart, x, y, direction, x+j, y+i, xCoords, yCoords, numNodes, concurrentProcesses) for _ in range(math.floor(os.cpu_count()*.6))}
            done, not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

            # Get the result from the first completed task
            results = next(iter(done)).result()

            showPath(results[0], results[1], xCoords, yCoords, x+j, y+i, len(results[0]))
    else:
        startTime = time.time()

        print('\nSearching direction 1...')
        resultsDir1 = findStart(x,y,direction,x+j,y+i,xCoords,yCoords, numNodes, concurrentProcesses) # Goes the wanted direction

        print('Searching direction 2...')
        resultsDir2 = findStart(x+j,y+i,getOpposite[direction],x,y,xCoords,yCoords, numNodes, concurrentProcesses) # Goes the opposite direction

        maxDist = -1e7
        maxDistCoord = None
        maxDistIndex = 0

        for index in range(len(resultsDir2[0])):
            coordX = resultsDir2[0][index]
            coordY = resultsDir2[1][index]
            xDist = abs(x - coordX)
            yDist = abs(y - coordY)
            dist = xDist + yDist
            if dist > maxDist:
                maxDist = dist
                maxDistCoord = (coordX,coordY)
                maxDistIndex = index

        dir2Index = maxDistIndex

        dir1Index = 0
        for dirIndex in range(len(resultsDir1[0])):
            if resultsDir1[0][dirIndex] == maxDistCoord[0] and resultsDir1[1][dirIndex] == maxDistCoord[1]:
                dir1Index = dirIndex
                break

        if dir1Index == 0:
            print('\nCannot find path.')

            endTime = time.time()
            print(f'\nWait time was: {round(endTime-startTime,2)} seconds.')
        else:
            half1X = resultsDir2[0][dir2Index:-1]
            half1Y = resultsDir2[1][dir2Index:-1]
            half2X = resultsDir1[0][dir1Index:-1]
            half2Y = resultsDir1[1][dir1Index:-1]

            results = (half1X[::-1] + half2X,half1Y[::-1] + half2Y) # Stitches the better parts of each together

            endTime = time.time()
            print(f'\nWait time was: {round(endTime-startTime,2)} seconds.')

            showPath(results[0], results[1], xCoords, yCoords, x+j, y+i, len(results[0]))
    

def showPath(xPath, yPath, xCoords, yCoords, startX, startY, numNodes):
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

    # Plotting with markers
    plt.plot(xCoords, yCoords, '.', label='Track Nodes', color='black')
    plt.plot(markedX, markedY, '-', label='Control Points', color='b')
    plt.plot(markedX[0], markedY[0], 'D', label='Start Node', color='g')
    plt.plot(startX, startY, 'D', label='Finish Node', color='r')
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
            print('Starting multiple processes...')
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
            print('Starting a single process...')
            xCoords, yCoords, total_nodes = processImageSection([img,(size,size),(0,0)])

        numNodes = "{:,}".format(total_nodes)

        endTime = time.time()

        # print(f'\nNumber of track nodes: {numNodes}') # Number of sections the track was split into

        print(f'\nWait time was: {round(endTime-startTime,2)} seconds.')

        print('\nFind the starting X and Y coordinates as well as the starting direction.')
        plotNodes(xCoords, yCoords, numNodes)

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
                xCoord = int(input('\nEnter starting X coordinate: '))
                if xCoord in xCoords:
                    yCoord = int(input('Enter starting Y coordinate: '))
                    if yCoord in yCoords:
                        print('\nRelative cardinal direction of the track:')
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