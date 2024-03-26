import os
import sys
import io
import tkinter as tk
from tkinter import ttk
import json 
import base64
import requests
from PIL import Image, ImageDraw, ImageTk


# Create the main window
root = tk.Tk()
root.title("Encounter Generator")

# Frame for inputs
input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, sticky="nsew")

# Frame for Treeview
treeview_frame = tk.Frame(root)
treeview_frame.grid(row=0, column=1, sticky="nsew", padx=10)

# Frame for the map and scrollbars
map_frame = tk.Frame(root)
map_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Frame for text output
text_frame = tk.Frame(root)
text_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

# Encounter Name 
tk.Label(input_frame, text="Encounter Name:").grid(row=0, column=0)
encounter_name_entry = tk.Entry(input_frame)
encounter_name_entry.grid(row=0, column=1)

# Load monsters from the JSON file
def load_monsters():
    # Determine if we're frozen (compiled) and set the base directory accordingly
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(__file__)
    
    bestiary_path = os.path.join(base_dir, 'data', 'bestiary.json')
    
    try:
        with open(bestiary_path, 'r') as file:
            monsters = json.load(file)
    except FileNotFoundError:
        print(f"Bestiary file not found at {bestiary_path}. Please ensure the file exists.")
        sys.exit(1)  # Exit the program if the file is not found
    
    return monsters

# Initialize the monsters
monsters = load_monsters()

# Convert monsters list to a format suitable for the dropdown menu
monster_names = [monster["name"] for monster in monsters]

# Logic for selecting monsters 
def on_monster_selected(event):
    # Get the selected monster's name
    selected_monster_name = monster_combobox.get()
    # Find the monster in the loaded JSON data
    selected_monster = next((monster for monster in monsters if monster["name"] == selected_monster_name), None)
    
    if selected_monster:
        if selected_monster["shortcodeToken"]:
            token_url_entry.config(state='disabled')  # Keep it disabled if shortcodeToken exists
        else:
            token_url_entry.config(state='normal')  # Enable if shortcodeToken is empty

# Logic for filtering monsters by name typed in
def filter_monsters(*args):
    #Filter the monster list based on the input (case-insensitive)
    input_text = monster_input_var.get().lower()
    filtered_monster_names = [name for name in monster_names if input_text in name.lower()]
    
    # Update the combobox values to only show filtered options
    monster_combobox['values'] = filtered_monster_names

    # If the current input fully matches one of the filtered options, automatically select it
    if input_text in [name.lower() for name in filtered_monster_names]:
        monster_combobox.set(next((name for name in filtered_monster_names if name.lower() == input_text), ''))

# Add monster selection combobox
tk.Label(input_frame, text="Select Monster:").grid(row=1, column=0)
monster_input_var = tk.StringVar(input_frame)
monster_combobox = ttk.Combobox(input_frame, values=monster_names)
monster_combobox.bind("<<ComboboxSelected>>", on_monster_selected)
monster_combobox.grid(row=1, column=1)
monster_combobox.config(textvariable=monster_input_var)
monster_input_var.trace_add("write", filter_monsters)

# Add monster quantity entry
tk.Label(input_frame, text="Quantity:").grid(row=2, column=0)
monster_quantity_entry = tk.Entry(input_frame)
monster_quantity_entry.grid(row=2, column=1)

# Field for adding token URLs
tk.Label(input_frame, text="Token URL:").grid(row=3, column=0)
token_url_entry = tk.Entry(input_frame, state='disabled')
token_url_entry.grid(row=3, column=1)

# Initialize the counter
monster_id_counter = 1  

# Array containing the monsters in the encounter
monsters_data = []

# Logic for adding monsters to list
def add_monster():
    global monster_id_counter
    # Get monster from combobox
    selected_monster_name = monster_combobox.get()
    quantity = int(monster_quantity_entry.get())
    
    # Find the monster in the loaded JSON data
    selected_monster = next((monster for monster in monsters if monster["name"] == selected_monster_name), None)
    
    if selected_monster:
        for _ in range (quantity):
            monsters_data.append({
                # Access global counter 
                "id" : monster_id_counter,
                "name": selected_monster["name"],
                # Include the CR in the monsters_data for encounter balancing 
                "cr": selected_monster["cr"],
                "quantity": 1,
                "token_url": token_url_entry.get(), 
                "size": selected_monster["size"], 
                "shortcodeToken" : selected_monster["shortcodeToken"],
                "location" : ""
            })
            monster_id_counter += 1 
    
    out_print("Monster Added")
    out_print(monsters_data)
    # Clear input fields for the next addition
    monster_quantity_entry.delete(0, tk.END)
    token_url_entry.delete(0, tk.END)
    display_monsters()

# Add monster button
add_monster_button = tk.Button(input_frame, text="Add Monster", command=add_monster)
add_monster_button.grid(row=4, column=1)

# Field for encounter map URL
tk.Label(input_frame, text="Map URL:").grid(row=5, column=0)
map_url_entry = tk.Entry(input_frame)
map_url_entry.grid(row=5, column=1)

# Field for Map Grid Size
tk.Label(input_frame, text="Grid Size (XxY):").grid(row=6, column=0)
grid_size_entry = tk.Entry(input_frame)
grid_size_entry.grid(row=6, column=1)

# Field for Map Cell Size
tk.Label(input_frame, text="Cell Size:").grid(row=7, column=0)
cell_size_entry = tk.Entry(input_frame)
cell_size_entry.grid(row=7, column=1)

# Vertical and horizontal scrollbars for the canvas
v_scrollbar = ttk.Scrollbar(map_frame, orient="vertical")
h_scrollbar = ttk.Scrollbar(map_frame, orient="horizontal")

# The map canvas
map_canvas = tk.Canvas(map_frame, width=1250, height=500,
                       yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

# Configure scrollbars
v_scrollbar.config(command=map_canvas.yview)
h_scrollbar.config(command=map_canvas.xview)

# Grid placement for the canvas and scrollbars
map_canvas.grid(row=0, column=0, sticky="nsew")
v_scrollbar.grid(row=0, column=1, sticky="ns")
h_scrollbar.grid(row=1, column=0, sticky="ew")

# Loads map 
def load_map():
    # Fetch the image from the URL
    response = requests.get(map_url_entry.get())
    image_data = io.BytesIO(response.content)
    image = Image.open(image_data).convert("RGBA")
    
    # Create an ImageDraw object and draw the grid lines and labels on the image
    draw = ImageDraw.Draw(image)
    grid_size_x, grid_size_y = map(int, grid_size_entry.get().split('x'))
    cell_size_px = int(cell_size_entry.get())
    
    # Draw grid on map
    for x in range(0, grid_size_x * cell_size_px, cell_size_px):
        draw.line((x, 0, x, grid_size_y * cell_size_px), fill="black")
        label = get_alpha_label((x // cell_size_px) + 1)
        draw.text((x + 5, 0), text=label, fill="black")
        
    for y in range(0, grid_size_y * cell_size_px, cell_size_px):
        draw.line((0, y, grid_size_x * cell_size_px, y), fill="black")
        draw.text((0, y + 5), text=str(y // cell_size_px + 1), fill="black")

    # Convert the PIL image to a format Tkinter Canvas can use
    tk_image = ImageTk.PhotoImage(image)
    
    # Display the image on the Canvas
    map_canvas.create_image(0, 0, anchor="nw", image=tk_image)
    map_canvas.image = tk_image  # Keep a reference to avoid garbage collection
    
    # Set the scrollable region to the size of the image
    map_canvas.config(scrollregion=map_canvas.bbox("all"))

    # Bind the click event if needed
    map_canvas.bind("<Button-1>", on_canvas_click)

# Load Map button
load_map_button = tk.Button(input_frame, text="Load Map", state='disabled', command=load_map)
load_map_button.grid(row=8, column=1)

# Determines if fields are not empty
def check_fields_and_enable_button():
    url = map_url_entry.get()
    grid_size = grid_size_entry.get()
    cell_size = cell_size_entry.get()
    if url and grid_size and cell_size:  
        load_map_button['state'] = 'normal'
    else:
        load_map_button['state'] = 'disabled'
        
map_url_entry.bind('<KeyRelease>', lambda event: check_fields_and_enable_button())
grid_size_entry.bind('<KeyRelease>', lambda event: check_fields_and_enable_button())
cell_size_entry.bind('<KeyRelease>', lambda event: check_fields_and_enable_button())

# Logic for generating bplan code
def generate_bplan_data():
    encounter_name = encounter_name_entry.get()
    if not encounter_name:  # Check if encounter name is empty
        out_print("Encounter name is missing.")
        return  # Exit the function if no encounter name is provided

    bplan_data = {
        encounter_name: [
            "!init add 20 DM -p"
        ] + ["!i effect DM map -attack \"||Size: {} ~ Background: {} ~ Options: c{}\"".format(
            grid_size_entry.get(), map_url_entry.get(), cell_size_entry.get())
        ]
    }

    size_to_abbreviation = {"Tiny": "T", "Small": "S", "Medium": "M", "Large": "L", "Huge": "H", "Gargantuan": "G"}
    
    for monster in monsters_data:
        token_short_code_final = monster.get("shortcodeToken")
        if token_short_code_final:
            # If shortcodeToken exists, use it directly without making a request
            out_print("Using existing shortcodeToken for monster.")
        else:
            # Process for monsters without a shortcodeToken
            token_short_code = base64.b64encode(monster["token_url"].encode('utf-8')).decode('utf-8')
            url = f'https://token.otfbm.io/meta/{token_short_code}'
            response = requests.get(url)
            if response.status_code == 200:
                html_content = response.text
                start_index = html_content.find('<body>') + len('<body>') 
                end_index = html_content.find('</body>')
                token_short_code_final = html_content[start_index:end_index].strip()
                # Update json to add missing shortcodeToken
                update_monster_shortcode(monster["name"], token_short_code_final)
            else:
                out_print(f"Failed to obtain shortcode for {monster['name']}, status code: {response.status_code}")
                continue
        
        monster_size = size_to_abbreviation.get(monster["size"], "M")

        for _ in range(monster["quantity"]):
            monster_command = f"!i madd \"{monster['name']}\" -n 1 -name \"{monster['name']} #\" -note \"Token: {token_short_code_final} | Size: {monster_size} | Location: {monster['location']}\""
            bplan_data[encounter_name].append(monster_command)
    
    bplan_json = json.dumps(bplan_data, indent=4)
    out_print("!uvar Battles " + bplan_json)

# Generate button
generate_button = tk.Button(text_frame, text="Generate", command=generate_bplan_data)
generate_button.grid(row=1, column=0, columnspan=2)

# Ouput textbox
output_text = tk.Text(text_frame, height=10, width=50)
output_text.grid(row=14, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

# Output textbox scrollbar 
scrollb = ttk.Scrollbar(text_frame, command=output_text.yview)
scrollb.grid(row=14, column=2, sticky='nsew')
output_text['yscrollcommand'] = scrollb.set

# Create a vertical scrollbar for the Treeview
scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical")

# Adding the Treeview widget with specified columns
tree = ttk.Treeview(treeview_frame, yscrollcommand=scrollbar.set,
                    columns=("ID", "Name", "Quantity", "CR", "Size", "Token URL", "Location"),
                    show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Quantity", text="Quantity")
tree.heading("CR", text="CR")
tree.heading("Size", text="Size")
tree.heading("Token URL", text="Token URL")
tree.heading("Location", text="Location")

# Adjusting columns
tree.column("ID", width=50, minwidth=50, stretch=tk.NO)
tree.column("Name", width=150, minwidth=100, stretch=tk.NO)
tree.column("Quantity", width=60, minwidth=60, stretch=tk.NO)
tree.column("CR", width=60, minwidth=60, stretch=tk.NO)
tree.column("Size", width=60, minwidth=60, stretch=tk.NO)
tree.column("Token URL", width=100, minwidth=100, stretch=tk.NO)
tree.column("Location", width=80, minwidth=80, stretch=tk.NO)

# Configure the scrollbar to interact with the Treeview
scrollbar.config(command=tree.yview)

# Place the Treeview widget using grid
tree.grid(row=0, column=0, sticky='nsew', padx=(0, 20))  # Adding padding for visual space between tree and scrollbar

# Place the scrollbar next to the Treeview
scrollbar.grid(row=0, column=1, sticky='ns')

# Delete monster button 
delete_monster_button = tk.Button(treeview_frame, text="Delete Selected Monster", command=lambda: delete_selected_monster())
delete_monster_button.grid(row=1, column=0)

# Display the monsters in the treeView
def display_monsters():
    # Clear the current items in the treeview
    for i in tree.get_children():
        tree.delete(i)
    
    # Add new items from the monsters_data list
    for monster in monsters_data:
        tree.insert("", tk.END, values=(monster["id"],
                                        monster["name"], 
                                        monster["quantity"], 
                                        monster["cr"], 
                                        monster["size"], 
                                        monster["token_url"], 
                                        monster["location"]))

# Delete the monsters in the treeView
def delete_selected_monster():
    # Get the selected item
    selected_items = tree.selection()

    # If you have multiple items selected, loop through each
    for selected_item in selected_items:
        # Find the monster's name in the selected row
        monster_name = tree.item(selected_item, 'values')[0]
        quantity = tree.item(selected_item, 'values')[1]
        cr = tree.item(selected_item, 'values')[2]
        size = tree.item(selected_item, 'values')[3]
        token_url = tree.item(selected_item, 'values')[4]

        # Find and remove the corresponding monster from monsters_data
        monsters_data[:] = [monster for monster in monsters_data if not (monster['name'] == monster_name and
                                                                         str(monster['quantity']) == str(quantity) and
                                                                         str(monster['cr']) == str(cr) and
                                                                         monster['size'] == size and
                                                                         monster['token_url'] == token_url)]
        
        # Remove the item from the Treeview
        tree.delete(selected_item)

# Itterate through monsters with changed shortcodes and updates json
def update_monster_shortcode(monster_name, shortcode):
    for monster in monsters:
        if monster["name"] == monster_name:
            monster["shortcodeToken"] = shortcode
            break
    with open('./data/bestiary.json', 'w') as file:
        json.dump(monsters, file, indent=4)

selected_monster_id = 0

# Store ID when monster is selected
def on_monster_selected(event):
    global selected_monster_id
    for iid in tree.selection():
        item = tree.item(iid)
        selected_monster_id = int(item['values'][0])
        print(f"Selected Monster ID: {selected_monster_id}")
        
# Find grid coordinates based off of click
def on_canvas_click(event):
    global selected_monster_id, monsters_data
    if selected_monster_id is not None:
        # Convert event coordinates to canvas coordinates, considering the current scroll
        canvas_x = map_canvas.canvasx(event.x)
        canvas_y = map_canvas.canvasy(event.y)

        # Calculate the grid position based on the canvas (image) coordinates
        cell_size_px = int(cell_size_entry.get())
        grid_x = int(canvas_x // cell_size_px)
        grid_y = int(canvas_y // cell_size_px)

        # Convert the grid position to an alpha-numeric format (e.g., A1, B2)
        column_label = get_alpha_label(grid_x + 1)  # Adjusting grid_x to be 1-based for labeling
        grid_position = f"{column_label}{grid_y + 1}"  # Similarly, adjusting grid_y to be 1-based

        # Update the location of the selected monster
        update_monster_location(selected_monster_id, grid_position)
        display_monsters()

# Update monster location
def update_monster_location(selected_monster_id, grid_position):
    for monster in monsters_data:
        if monster["id"] == selected_monster_id:
            monster["location"] = grid_position
            break

# Converts numerical grid to alphabet
def get_alpha_label(index):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    label = ''
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        label = alphabet[remainder] + label
    return label

# Print to output text box
def out_print(*args, **kwargs):
    # Insert text at the end of the text widget
    output_text.insert(tk.END, ' '.join(map(str, args)) + '\n')
    # Ensure the latest output is visible
    output_text.see(tk.END)

# Shit randomly breaks if this isn't put at the end
tree.bind("<<TreeviewSelect>>", on_monster_selected)

# Run the application
root.mainloop()