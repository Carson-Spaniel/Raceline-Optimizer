from PIL import Image
import heapq

class Graph:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.graph = {}

    def create_graph(self, grid):
        for i in range(self.rows):
            for j in range(self.cols):
                if grid[i][j] == 1:
                    self.add_node((i, j), grid)

    def add_node(self, node, grid):
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

            if current_node not in self.graph:
                continue  # Skip if the node is not present in the graph

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
            if distances:  # Check if distances dictionary is not empty
                shortest_path[node] = min(distances.values())

        if shortest_path:  # Check if shortest_path dictionary is not empty
            return min(shortest_path, key=shortest_path.get)
        else:
            return ()  # Return an empty tuple if no nodes have valid distances

    def update_grid_with_path(self, path, grid):
        nodes = 0
        for node in self.graph:
            grid[node[0]][node[1]] = 0

        for node in path:
            grid[node[0]][node[1]] = 1
            nodes += 1
        return nodes

    def print_graph(self):
        for node, neighbors in self.graph.items():
            print(f"{node} -> {neighbors}")

def is_black(pixel, threshold=100):
    # Assuming pixel is in RGB format
    # Calculate luminance as a measure of intensity (brightness)
    luminance = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
    # Check if luminance is below the threshold
    return luminance <= threshold

def process_image(image_path, output_file, initial_target_size=(100, 100)):
    graphs = []
    while initial_target_size[0] > 1 and initial_target_size[1] > 1:
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
                    pixel = img.getpixel((x, y))

                    # Check if the pixel is considered black
                    if is_black(pixel):
                        f.write('1')
                    else:
                        f.write('0')

                # Add a newline after each row
                f.write('\n')

        # Read the grid from the text file
        with open(output_file, 'r') as file:
            lines = file.readlines()

        # Convert the lines to a 2D list of integers
        grid = [[int(char) for char in line.strip()] for line in lines]

        # Create a graph from the grid
        rows = len(grid)
        cols = len(grid[0])
        graph = Graph(rows, cols)
        graph.create_graph(grid)

        shortest_path_start = graph.find_shortest_path()
        graphs.append(shortest_path_start)

        # Check if shortest_path_start is not empty
        if shortest_path_start:
            shortest_path = graph.dijkstra(shortest_path_start)
            connected_components = graph.update_grid_with_path(shortest_path, grid)
            print(connected_components)
            
            # !
            if connected_components < 330:
                graphs.pop()
                shortest_path = graph.dijkstra(graphs[-1])
                graph.update_grid_with_path(shortest_path, grid)

                # If there is only one connected component, break from the loop
                if connected_components == 1:
                    break
                else:
                    # Reduce the target size
                    initial_target_size = (initial_target_size[0] - 1, initial_target_size[1] - 1)
                break

            # If there is only one connected component, break from the loop
            if connected_components == 1:
                break
            else:
                # Reduce the target size
                initial_target_size = (initial_target_size[0] - 1, initial_target_size[1] - 1)
        else:
            graphs.pop()
            shortest_path = graph.dijkstra(graphs[-1])
            graph.update_grid_with_path(shortest_path, grid)

            # Check the number of connected components
            connected_components = sum(1 for node in graph.graph if node in graph.dijkstra(node) and graph.dijkstra(node)[node] == 0)

            # If there is only one connected component, break from the loop
            if connected_components == 1:
                break
            else:
                # Reduce the target size
                initial_target_size = (initial_target_size[0] - 1, initial_target_size[1] - 1)
            break
    
    print('Number of graphs checked:',len(graphs))

    return graph, grid

# Example usage with a specified initial target size
image_path = 'tracks/monza.jpg'
output_file = 'output.txt'
initial_target_size = (75, 75)
graph, grid = process_image(image_path, output_file, initial_target_size)

graph.print_graph()

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
