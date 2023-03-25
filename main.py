import json
import subprocess
import tkinter as tk
from tkinter import messagebox

def read_graph(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def open_file_in_vscode(filename):
    try:
        subprocess.run(['code', filename])
    except FileNotFoundError:
        messagebox.showerror('Error', f'File {filename} not found.')

def create_node(parent, node_data, x, y):
    frame = tk.Frame(parent, borderwidth=1, relief='solid', padx=5, pady=5)
    frame.place(x=x, y=y)
    
    label = tk.Label(frame, text=node_data['filename'])
    label.pack()
    
    snippet_label = tk.Label(frame, text=node_data['snippet'], justify='left')
    snippet_label.pack()
    
    frame.bind('<Button-1>', lambda event: open_file_in_vscode(node_data['filename']))
    label.bind('<Button-1>', lambda event: open_file_in_vscode(node_data['filename']))
    snippet_label.bind('<Button-1>', lambda event: open_file_in_vscode(node_data['filename']))
    
    return frame

def display_graph(graph_data):
    window = tk.Tk()
    window.title('Data Flow Visualization')

    # Make the window open in full screen
    window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")

    node_widgets = []

    for i, node in enumerate(graph_data['nodes']):
        x, y = 50, i * 150 + 50
        node_widget = create_node(window, node, x, y)
        node_widgets.append(node_widget)

    window.mainloop()

if __name__ == '__main__':
    graph_data = read_graph('graph.json')
    display_graph(graph_data)
