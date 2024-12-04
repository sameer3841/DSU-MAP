import tkinter as tk
from PIL import Image, ImageTk
import heapq
import math



def runGUI():
   # Path to the pre-determined image
   image_path = "/DSU-MAP/images/DSU_MAP.png"  # Replace with your image path

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
   root.title("DSU Maps")
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
   #
   # NODES Establish the nodes manually
   #
   # NOTE: The prefix "B" indicates a 'building, "P" indicates a road or parking lot.
   # NOTE: Try to name buildings after their actual name if possible, but fallback on normal naming scheme otherwise.
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
   graph.add_node("P4", 732, 300)
   graph.add_node("B8", 658, 295)
   graph.add_node("B7", 744, 342)
   graph.add_node("P1", 976, 338)
   graph.add_node("FootballStadium", 900, 270)
   graph.add_node("VolleyballCourt", 846, 350)
   graph.add_node("BasketballCourt", 865, 382)
   graph.add_node("B6", 802, 366)
   graph.add_node("Gym", 780, 406)
   graph.add_node("MLK", 918, 400)
   graph.add_node("MainEntrance", 1018, 442)
   graph.add_node("B37", 942, 490)
   graph.add_node("NorthScienceCenter", 852, 465)
   graph.add_node("SouthScienceCenter", 865, 510)
   graph.add_node("PoliceStation", 920, 512)
   graph.add_node("Library", 782, 518)
   graph.add_node("BOA", 745, 576)
   graph.add_node("Admin", 1002, 572)
   graph.add_node("P14", 1044, 500)
   graph.add_node("ETV", 955, 574)
   graph.add_node("Oscar", 930, 612)
   graph.add_node("E&H", 846, 591)
   graph.add_node("P18", 1006, 634)
   graph.add_node("Ville", 935, 656)
   graph.add_node("P24", 1017, 690)
   graph.add_node("B43", 870, 712) # University Village Building 1
   graph.add_node("B42", 947, 712) # University Village Building 2
   graph.add_node("B41", 910, 745) # University Village Building 3
   graph.add_node("P19", 870, 660)
   graph.add_node("P19B", 898, 578)
   graph.add_node("P12", 888, 520)
   graph.add_node("P25", 762, 706)
   graph.add_node("E&HEntrance", 690, 680)
   graph.add_node("P16", 736, 645)
   graph.add_node("PresidentsResidence", 686, 568)
   graph.add_node("Warren", 678, 531)
   graph.add_node("DEHall", 719, 488)
   graph.add_node("GrossleyHall", 788, 464)
   graph.add_node("DEPublicMedia", 620, 561)
   graph.add_node("P8A", 712, 440)
   graph.add_node("Towers", 586, 511)
   graph.add_node("HealthServices", 568, 526)
   graph.add_node("P9", 582, 480)
   graph.add_node("Tubman", 636, 488)
   graph.add_node("Thomasson", 654, 435)
   graph.add_node("Conrad", 624, 420)
   graph.add_node("Conwell", 665, 347)
   #
   # EDGES  Establish the edges manually, but calculate weights based on distance
   #
   graph.add_edge("B1", "B2")
   graph.add_edge("B2", "AquaticResearch")
   graph.add_edge("AquaticResearch", "SoccerField")
   graph.add_edge("AquaticResearch", "P3A0")
   graph.add_edge("SoccerField", "P3A0")
   graph.add_edge("SoftballField", "P3A0")
   graph.add_edge("P3A0", "TennisCourt")
   graph.add_edge("P3A0", "P4")
   graph.add_edge("TennisCourt", "P4")
   graph.add_edge("P3A0", "P3A1")
   graph.add_edge("P3A1", "P3A2")
   graph.add_edge("P3A1", "B53") # Road connection to building 53, small building to the west of the football field
   graph.add_edge("P3A2", "P3A3")
   graph.add_edge("P3A0", "B8")
   graph.add_edge("P4", "B8")
   graph.add_edge("P4", "B7")
   graph.add_edge("P3A3", "P1")
   graph.add_edge("P3A3", "FootballStadium")
   graph.add_edge("P3A2", "VolleyballCourt")
   graph.add_edge("VolleyballCourt", "BasketballCourt")
   graph.add_edge("P3A2", "B6")
   graph.add_edge("B6", "Gym")
   graph.add_edge("BasketballCourt", "MLK")
   graph.add_edge("P3A3", "MLK")
   graph.add_edge("P1", "MLK")
   graph.add_edge("MainEntrance", "P1")
   graph.add_edge("MainEntrance", "MLK")
   graph.add_edge("B37", "MLK")
   graph.add_edge("B37", "MainEntrance")
   graph.add_edge("NorthScienceCenter", "MLK")
   graph.add_edge("NorthScienceCenter", "Gym")
   graph.add_edge("NorthScienceCenter", "SouthScienceCenter")
   graph.add_edge("PoliceStation", "B37")
   graph.add_edge("PoliceStation", "SouthScienceCenter")
   graph.add_edge("Library", "BOA")
   graph.add_edge("Library", "NorthScienceCenter")
   graph.add_edge("P14", "MainEntrance")
   graph.add_edge("P14", "Admin")
   graph.add_edge("P14", "B37")
   graph.add_edge("Admin", "B37")
   graph.add_edge("ETV", "PoliceStation")
   graph.add_edge("ETV", "Admin")
   graph.add_edge("ETV", "Oscar")
   graph.add_edge("E&H", "BOA")
   graph.add_edge("E&H", "Oscar")
   graph.add_edge("E&H", "Library")
   graph.add_edge("E&H", "SouthScienceCenter")
   graph.add_edge("P18", "Admin")
   graph.add_edge("P18", "Oscar")
   graph.add_edge("Ville", "P18")
   graph.add_edge("Ville", "Oscar")
   graph.add_edge("P24", "P18")
   graph.add_edge("P24", "Ville")
   graph.add_edge("B42", "B41")
   graph.add_edge("B42", "B43")
   graph.add_edge("B43", "B41")
   graph.add_edge("B42", "Ville")
   graph.add_edge("P19", "Ville")
   graph.add_edge("P19", "B43")
   graph.add_edge("P19B", "E&H")
   graph.add_edge("P19B", "Oscar")
   graph.add_edge("P19B", "ETV")
   graph.add_edge("P19B", "PoliceStation")
   graph.add_edge("P12", "PoliceStation")
   graph.add_edge("P12", "SouthScienceCenter")
   graph.add_edge("P12", "P19B")
   graph.add_edge("P25", "P19")
   graph.add_edge("P25", "B43")
   graph.add_edge("E&HEntrance", "P25")
   graph.add_edge("E&HEntrance", "P16")
   graph.add_edge("P16", "P25")
   graph.add_edge("P16", "BOA")
   graph.add_edge("PresidentsResidence", "BOA")
   graph.add_edge("Warren", "PresidentsResidence")
   graph.add_edge("Warren", "Library")
   graph.add_edge("DEHall", "Warren")
   graph.add_edge("DEHall", "Library")
   graph.add_edge("DEHall", "GrossleyHall")
   graph.add_edge("GrossleyHall", "Library")
   graph.add_edge("DEPublicMedia", "PresidentsResidence")
   graph.add_edge("DEPublicMedia", "Warren")
   graph.add_edge("P8A", "DEHall")
   graph.add_edge("P8A", "Gym")
   graph.add_edge("P8A", "Gym")
   graph.add_edge("Towers", "DEPublicMedia")
   graph.add_edge("Towers", "HealthServices")
   graph.add_edge("P9", "Towers")
   graph.add_edge("P9", "HealthServices")
   graph.add_edge("Tubman", "Warren")
   graph.add_edge("Tubman", "Towers")
   graph.add_edge("Tubman", "P9")
   graph.add_edge("Thomasson", "Tubman")
   graph.add_edge("Thomasson", "P8A")
   graph.add_edge("Conrad", "Thomasson")
   graph.add_edge("Conrad", "P9")
   #graph.add_edge("Conwell", "P9")
   # Finally, draw the graph
   draw_graph(canvas, graph, image_on_canvas)

   # Start the main loop
   root.mainloop()


if __name__ == "__main__":
   main()
