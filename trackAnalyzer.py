from PIL import Image

def is_black(pixel, threshold=100):
    # Assuming pixel is in RGB format
    # Calculate luminance as a measure of intensity (brightness)
    luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
    # Check if luminance is below the threshold
    return luminance <= threshold

def process_image(image_path, output_file, initial_target_size=(100, 100)):
    images = []
    while initial_target_size[0] != 0 and initial_target_size[1] != 0:
        # Open the image file
        img = Image.open(image_path)

        # Resize the image to the specified target size
        img = img.resize(initial_target_size, resample=Image.BOX)

        # Get the size of the resized image
        width, height = img.size

        # Create a new file for storing the results
        with open(output_file, 'w') as f:
            # Iterate through each pixel
            for y in range(height):
                for x in range(width):
                    nodes = []
                    pixel = img.getpixel((x, y))

                    # Check if the pixel is considered black
                    if is_black(pixel):
                        f.write('1')
                        negX = width-1
                        while negX != x:
                            if is_black(img.getpixel((negX, y))):
                                nodes.append('1')
                            elif '1' in nodes:
                                nodes.append('2')
                            else:
                                nodes.append('0')
                            negX -= 1
                        i = len(nodes)
                        while i != 0:
                            f.write(nodes.pop())
                            i-=1
                        break

                    else:
                        f.write('0')

                # Add a newline after each row
                f.write('\n')
                # Check for 5 connected neighbors that are 0

        # Check for 5 connected neighbors that are 0 and rewrite the file
        with open(output_file, 'r') as file:
            lines = file.readlines()

        with open(output_file, 'w') as f:
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if lines[y][x] == '1':
                        neighbors = [
                            lines[y - 1][x],
                            lines[y + 1][x],
                            lines[y][x - 1],
                            lines[y][x + 1],
                            lines[y - 1][x - 1],
                        ]
                        if neighbors.count('0') >= 5:
                            
                            f.write('0')
                        else:
                            f.write(lines[y][x])
                    else:
                        f.write(lines[y][x])
                f.write('\n')

        # Read the grid from the text file
        with open(output_file, 'r') as file:
            lines = file.readlines()
            images.append(lines)
        
        hole = False
        totalNodes = 0
        for line in lines:
            node = 0
            fill = False
            for i in line:
                if i == '1':
                    node += 1
                    totalNodes += 1
                if i == '2':
                    fill = True
            if node == 1:
                hole = True
                break
            # elif node > 5 and not fill:
            #     hole = True
            #     break

        print(f'{totalNodes=}')
        if totalNodes == 0:
            hole = True
            

        if hole:
            lines = images.pop()
            break
        else:
            initial_target_size = (initial_target_size[0]-1,initial_target_size[1]-1)

    # Convert the lines to a 2D list of integers
    grid = [[int(char) for char in line.strip()] for line in lines]

    return grid

# Example usage with a specified initial target size
image_path = 'tracks/monza.jpg'
output_file = 'output.txt'
initial_target_size = (90, 90)
grid = process_image(image_path, output_file, initial_target_size)

print('\n')

# Print the updated grid
for row in grid:
    print(' '.join(map(str, row)))

print('\n')

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

# Print the grid for visualization
i = 0
for row in grid:
    for node in row:
        if node == 1:
            print(BackgroundColors.BLUE + '  ' + BackgroundColors.RESET, end='')
            i += 1
        elif node == 2:
            print(BackgroundColors.RED + '  ' + BackgroundColors.RESET, end='')
            i += 1
        else:
            print(BackgroundColors.GREEN + '  ' + BackgroundColors.RESET, end='')
    print('\n', end='')

print(f'Number of nodes: {i}')
