import tkinter as tk
from PIL import Image, ImageTk
import heapq
import math



def runGUI():
   # Path to the pre-determined image
   image_path = "images/DSU_MAP.png"  # Replace with your image path

   # Function to handle mouse clicks
   def on_click(event):
      # Map the clicked position back to the original image's coordinates
      original_x = int(event.x * scale_x)
      original_y = int(event.y * scale_y)
      print(f"Clicked at scaled coordinates: ({event.x}, {event.y})")
      print(f"Clicked at original coordinates: ({original_x}, {original_y})")

   # Initialize the main window
   root = tk.Tk()
   root.title("Image Click Coordinate Viewer")

   # Open the image using PIL
   try:
      img = Image.open(image_path)
   except FileNotFoundError:
      print(f"Error: File not found at {image_path}")
      root.destroy()
      exit()

   # Determine the window size and scale the image
   window_width = 800  # Adjust the width of the Tkinter window
   window_height = 600  # Adjust the height of the Tkinter window
   original_width, original_height = img.size

   # Calculate scaling factors
   scale_x = original_width / window_width
   scale_y = original_height / window_height

   # Resize the image while maintaining its aspect ratio
   if scale_x > scale_y:
      new_width = window_width
      new_height = int(original_height / scale_x)
   else:
      new_width = int(original_width / scale_y)
      new_height = window_height

   img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
   tk_img = ImageTk.PhotoImage(img_resized)

   # Label to display the image
   img_label = tk.Label(root, image=tk_img)
   img_label.pack()

   # Bind click events to the image
   img_label.bind("<Button-1>", on_click)

   # Run the application
   root.mainloop()


def draw_graph(canvas, graph, image_on_canvas):
   # Redraw the image on the canvas (ensure it stays on top of the graph)
   canvas.create_image(0, 0, anchor="nw", image=image_on_canvas)

   # Draw edges first
   for from_node, neighbors in graph.edges.items():
      x1, y1 = graph.nodes[from_node]
      for to_node, _ in neighbors:
         x2, y2 = graph.nodes[to_node]
         # Draw line between nodes
         canvas.create_line(x1, y1, x2, y2, fill="gray", width=1)

   # Draw nodes on top of edges
   for node, (x, y) in graph.nodes.items():
      color = "green" if node in selected_nodes else "blue"  # Change to green if selected
      canvas.create_oval(x-Graph.nodeSize, y-Graph.nodeSize, x+Graph.nodeSize, y+Graph.nodeSize, fill=color, tags=node)
      # Bind the node to the click event
      canvas.tag_bind(node, "<Button-1>", lambda e, n=node: on_node_click(canvas, graph, n, image_on_canvas))


# Dijkstra's algorithm for shortest path
def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph.nodes}
    distances[start] = 0
    priority_queue = [(0, start)]
    previous = {node: None for node in graph.nodes}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            break

        for neighbor, weight in graph.get_neighbors(current_node):
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the path
    path = []
    while end:
        path.append(end)
        end = previous[end]
    return path[::-1], distances[path[0]]


# Node selection and pathfinding
selected_nodes = [] # An array that contains all currently selected nodes
previous_path_lines = []
def on_node_click(canvas, graph, node, image_on_canvas):
   global selected_nodes, previous_path_lines
   
   if node not in selected_nodes:
      selected_nodes.append(node)
      print(f"Selected: {node}")
   
   # Re-draw the graph to update the color of selected nodes
   canvas.delete("all")
   draw_graph(canvas, graph, image_on_canvas)

   if len(selected_nodes) == 2:
      start, end = selected_nodes
      path, cost = dijkstra(graph, start, end)
      print(f"Path: {path}, Cost: {cost}")
      
      # Clear previously drawn path lines
      for line in previous_path_lines:
         canvas.delete(line)  # Remove the previous path lines
      
      previous_path_lines.clear()  # Clear the stored lines list

      # Highlight the new path on the canvas
      path_lines = []
      for i in range(len(path) - 1):
         x1, y1 = graph.nodes[path[i]]
         x2, y2 = graph.nodes[path[i+1]]
         line_id = canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
         path_lines.append(line_id)  # Store the line ID for future deletion
      previous_path_lines = path_lines  # Update the stored path lines
      selected_nodes.clear()
   if len(selected_nodes) > 2:
      print("ERROR: More than two nodes were in the 'selected_nodes' array, which shouldn't be possible.")



class Graph:
   nodeSize = 10

   def __init__(self):
      self.nodes = {}  # Dictionary to store node data
      self.edges = {}  # Dictionary to store edges and their weights

   def add_node(self, name, x, y):
      self.nodes[name] = (x, y)
      self.edges[name] = []

   def add_edge(self, from_node, to_node):
      # Get the coordinates of the nodes
      x1, y1 = self.nodes[from_node]
      x2, y2 = self.nodes[to_node]

      # Calculate the weight as the Euclidean distance
      weight = self.calculate_distance(x1, y1, x2, y2)

      # Add the edge with the calculated weight
      self.edges[from_node].append((to_node, weight))
      self.edges[to_node].append((from_node, weight))  # For undirected graphs

   def calculate_distance(self, x1, y1, x2, y2):
      return math.floor(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

   def get_neighbors(self, node):
      return self.edges[node]




def main():
   # Initialize Tkinter window
   root = tk.Tk()
   root.title("Graph on Map")
   canvas_width = 1200
   canvas_height = 850

   # Create canvas
   canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
   canvas.pack()

   # Load map image and display it
   image_path = "images/DSU_MAP.png"  # Replace with your map image path
   map_image = Image.open(image_path)

   # Get the original size of the image
   original_width, original_height = map_image.size

   # Resize the image to fit the canvas while maintaining the aspect ratio
   map_image = map_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
   tk_image = ImageTk.PhotoImage(map_image)
   # Reference to the tk image to be used by the rest of the program
   image_on_canvas = tk_image

   # Create image on canvas
   canvas.create_image(0, 0, anchor="nw", image=image_on_canvas)

   # Calculate scaling factors to convert canvas coordinates back to original image coordinates
   scale_x = original_width / canvas_width
   scale_y = original_height / canvas_height

   # Function to handle mouse click
   def on_click(event):
      # Get canvas coordinates
      canvas_x = event.x
      canvas_y = event.y

      # Convert to original image coordinates by applying the scaling factors
      original_x = int(canvas_x * scale_x)
      original_y = int(canvas_y * scale_y)

      # Print the coordinates
      print(f"Clicked at canvas coordinates: ({canvas_x}, {canvas_y})")
      print(f"Clicked at original image coordinates: ({original_x}, {original_y})")

   # Bind the click event to the canvas
   canvas.bind("<Button-1>", on_click)

   # Create and draw the graph
   graph = Graph()
   # Establish the nodes manually
   graph.add_node("B1", 608, 56)
   graph.add_node("B2", 568, 60)
   graph.add_node("AquaticResearch", 660, 155)
   graph.add_node("SoccerField", 780, 150)
      # Note: There are four 'P3-A' instances on the DSU map. Due to this, from left to right, they will be named "P3A0"-"P3A3"
   # P3-A's (no hypen allowed in the ID!)
   graph.add_node("P3A0", 752, 240)
   graph.add_node("P3A1", 802, 282)
   graph.add_node("P3A2", 840, 326)
   graph.add_node("P3A3", 902, 346)
   graph.add_node("B53", 822, 268)
   graph.add_node("SoftballField", 830, 184)
   graph.add_node("TennisCourt", 755, 286)
   # Establish the edges manually, but calculate weights based on distance
   graph.add_edge("B1", "B2")
   graph.add_edge("B2", "AquaticResearch")
   graph.add_edge("AquaticResearch", "SoccerField")
   graph.add_edge("AquaticResearch", "P3A0")
   graph.add_edge("SoccerField", "P3A0")
   graph.add_edge("SoftballField", "P3A0")
   graph.add_edge("P3A0", "TennisCourt")
   graph.add_edge("P3A0", "P3A1")
   graph.add_edge("P3A1", "P3A2")
   graph.add_edge("P3A1", "B53") # Road connection to building 53, small building to the west of the football field
   graph.add_edge("P3A2", "P3A3")
   # Finally, draw the graph
   draw_graph(canvas, graph, image_on_canvas)

   # Start the main loop
   root.mainloop()


if __name__ == "__main__":
   main()
