import os
import sys
import tkinter as tk
from tkinter import ttk
import json 
import base64
import requests

# Create the main window
root = tk.Tk()
root.title("Encounter Generator")

# Encounter Name 
tk.Label(root, text="Encounter Name:").grid(row=0, column=0)
encounter_name_entry = tk.Entry(root)
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

monsters = load_monsters()

# Convert monsters list to a format suitable for the dropdown menu
monster_names = [monster["name"] for monster in monsters]

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
tk.Label(root, text="Select Monster:").grid(row=1, column=0)
monster_input_var = tk.StringVar(root)
monster_combobox = ttk.Combobox(root, values=monster_names)
monster_combobox.bind("<<ComboboxSelected>>", on_monster_selected)
monster_combobox.grid(row=1, column=1)
monster_combobox.config(textvariable=monster_input_var)
monster_input_var.trace_add("write", filter_monsters)

# Add monster quantity entry
tk.Label(root, text="Quantity:").grid(row=2, column=0)
monster_quantity_entry = tk.Entry(root)
monster_quantity_entry.grid(row=2, column=1)

# Field for adding token URLs
tk.Label(root, text="Token URL:").grid(row=3, column=0)
token_url_entry = tk.Entry(root, state='disabled')
token_url_entry.grid(row=3, column=1)

# Array containing the monsters in the encounter
monsters_data = []

def add_monster():
    # Get monster from combobox
    selected_monster_name = monster_combobox.get()
    quantity = int(monster_quantity_entry.get())
    
    # Find the monster in the loaded JSON data
    selected_monster = next((monster for monster in monsters if monster["name"] == selected_monster_name), None)
    
    if selected_monster:
        # Include the CR in the monsters_data
        monsters_data.append({
            "name": selected_monster["name"],
            "cr": selected_monster["cr"],
            "quantity": quantity,
            # Assuming you will later include the token URL and size, for now placeholders
            "token_url": token_url_entry.get(), 
            "size": selected_monster["size"],  # You can include size or any other needed attributes
            "shortcodeToken" : selected_monster["shortcodeToken"]
        })
    
    out_print("Monster Added")
    out_print(monsters_data)
    # Recalculate and update CR/EXP info based on the newly added monster
    #update_cr_exp_info()
    # Clear input fields for the next addition
    monster_quantity_entry.delete(0, tk.END)
    token_url_entry.delete(0, tk.END)
    display_monsters()

# Add monster button
add_monster_button = tk.Button(root, text="Add Monster", command=add_monster)
add_monster_button.grid(row=4, column=0, columnspan=2)

# Delete monster button 
delete_monster_button = tk.Button(root, text="Delete Selected Monster", command=lambda: delete_selected_monster())
delete_monster_button.grid(row=13, column=0, columnspan=4, pady=5)

# Field for encounter map URL
tk.Label(root, text="Map URL:").grid(row=5, column=0)
map_url_entry = tk.Entry(root)
map_url_entry.grid(row=5, column=1)

# Field for Map Grid Size
tk.Label(root, text="Grid Size (XxY):").grid(row=6, column=0)
grid_size_entry = tk.Entry(root)
grid_size_entry.grid(row=6, column=1)

# Field for Map Cell Size
tk.Label(root, text="Cell Size:").grid(row=7, column=0)
cell_size_entry = tk.Entry(root)
cell_size_entry.grid(row=7, column=1)

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
            monster_command = f"!i madd \"{monster['name']}\" -n 1 -name \"{monster['name']} #\" -note \"Token: {token_short_code_final} | Size: {monster_size}\""
            bplan_data[encounter_name].append(monster_command)
    
    bplan_json = json.dumps(bplan_data, indent=4)
    out_print("!uvar Battles " + bplan_json)

# Generate button
generate_button = tk.Button(root, text="Generate", command=generate_bplan_data)
generate_button.grid(row=8, column=0, columnspan=4)

output_text = tk.Text(root, height=10, width=50)
output_text.grid(row=14, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

scrollb = ttk.Scrollbar(root, command=output_text.yview)
scrollb.grid(row=14, column=2, sticky='nsew')
output_text['yscrollcommand'] = scrollb.set

# Frame for the Treeview
frame = ttk.Frame(root)
frame.grid(row=12, column=0, columnspan=4, sticky='nsew')  

# Configure the root grid to allow the frame to expand and fill the space
root.grid_rowconfigure(12, weight=1)  # Make the frame's row expandable
root.grid_columnconfigure(0, weight=1)  # Make the first column expandable

# Adding the Treeview widget
tree = ttk.Treeview(frame, columns=("Name", "Quantity", "CR", "Size", "Token URL"), show="headings")
tree.heading("Name", text="Name")
tree.heading("Quantity", text="Quantity")
tree.heading("CR", text="CR")
tree.heading("Size", text="Size")
tree.heading("Token URL", text="Token URL")
tree.pack(fill='both', expand=True)

# Display the monsters in the treeView
def display_monsters():
    # Clear the current items in the treeview
    for i in tree.get_children():
        tree.delete(i)
    
    # Add new items from the monsters_data list
    for monster in monsters_data:
        tree.insert("", tk.END, values=(monster["name"], monster["quantity"], monster["cr"], monster["size"], monster["token_url"]))

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

# Itterated through monsters with changed shortcodes and updates json
def update_monster_shortcode(monster_name, shortcode):
    for monster in monsters:
        if monster["name"] == monster_name:
            monster["shortcodeToken"] = shortcode
            break
    with open('./data/bestiary.json', 'w') as file:
        json.dump(monsters, file, indent=4)

# Print to output text box
def out_print(*args, **kwargs):
    # Insert text at the end of the text widget
    output_text.insert(tk.END, ' '.join(map(str, args)) + '\n')
    # Ensure the latest output is visible
    output_text.see(tk.END)

# Run the application
root.mainloop()