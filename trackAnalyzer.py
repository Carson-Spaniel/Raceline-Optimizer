from PIL import Image

def is_black(pixel, threshold=100):
    # Assuming pixel is in RGB format
    # Calculate luminance as a measure of intensity (brightness)
    luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
    # Check if luminance is below the threshold
    return luminance <= threshold

def process_image(image_path, output_file, target_size=(100, 100)):
    # Open the image file
    img = Image.open(image_path)

    # Resize the image to the specified target size
    img = img.resize(target_size, resample=Image.BOX)

    # Get the size of the resized image
    width, height = img.size

    # Create a new file for storing the results
    with open(output_file, 'w') as f:
        # Iterate through each pixel
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))

                # Check if the pixel is considered black
                if is_black(pixel):
                    f.write('1')
                else:
                    f.write('0')

            # Add a newline after each row
            f.write('\n')

# Example usage with a specified target size
image_path = 'tracks/monza.jpg'
output_file = 'output.txt'
target_size = (50, 50)
process_image(image_path, output_file, target_size)

import heapq

class Graph:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.graph = {}
        self.create_graph()

    def create_graph(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if grid[i][j] == 1:
                    self.add_node((i, j))

    def add_node(self, node):
        i, j = node
        neighbors = []

        # Check all adjacent cells
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if 0 <= x < self.rows and 0 <= y < self.cols and (x, y) != (i, j) and grid[x][y] == 1:
                    neighbors.append((x, y))

        self.graph[node] = neighbors

    def dijkstra(self, start):
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        priority_queue = [(0, start)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor in self.graph[current_node]:
                distance = current_distance + 1  # Assuming all edges have weight 1
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))

        return distances

    def find_shortest_path(self):
        shortest_path = {}
        for node in self.graph:
            distances = self.dijkstra(node)
            shortest_path[node] = min(distances.values())

        return min(shortest_path, key=shortest_path.get)

    def update_grid_with_path(self, path):
        for node in self.graph:
            grid[node[0]][node[1]] = 0

        for node in path:
            grid[node[0]][node[1]] = 1

    def print_graph(self):
        for node, neighbors in self.graph.items():
            print(f"{node} -> {neighbors}")

# Read the grid from a text file
with open('output.txt', 'r') as file:
    lines = file.readlines()

# Convert the lines to a 2D list of integers
grid = [[int(char) for char in line.strip()] for line in lines]

def filter_grid(grid):
    filtered_grid = [row[:] for row in grid]  # Create a copy of the original grid

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 1:
                count_neighbors = sum(grid[x][y] == 0 for x in range(i-1, i+2) for y in range(j-1, j+2) if 0 <= x < len(grid) and 0 <= y < len(grid[i]))
                if count_neighbors >= 5:
                    filtered_grid[i][j] = 0

    return filtered_grid

filtered_grid = grid #filter_grid(grid)

rows = len(filtered_grid)
cols = len(filtered_grid[0])

# Create a graph from the grid
graph = Graph(rows, cols)
graph.print_graph()

print('\n')

# Find the shortest path and update the grid
shortest_path_start = graph.find_shortest_path()
shortest_path = graph.dijkstra(shortest_path_start)
graph.update_grid_with_path(shortest_path)

# Print the updated grid
for row in filtered_grid:
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
for row in filtered_grid:
    for node in row:
        if node:
            color = BackgroundColors.BLUE
            print(BackgroundColors.BLUE + '  ' + BackgroundColors.RESET, end='')
            i += 1
        elif node == 2:
            color = BackgroundColors.BLUE
            print(BackgroundColors.RED + '  ' + BackgroundColors.RESET, end='')
            i += 1
        else:
            color = BackgroundColors.GREEN
            print(BackgroundColors.GREEN + '  ' + BackgroundColors.RESET, end='')
    print('\n', end='')

print(f'Number of nodes: {i}')