import json
import subprocess
import tkinter as tk
import time

from tkinter import messagebox, Canvas, Scrollbar

def read_graph(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def open_file_in_vscode(filename, line_number):
    try:
        subprocess.run(['code', "--goto", f"../picnic/packages/{filename}:{line_number}"])
    except FileNotFoundError:
        messagebox.showerror('Error', f'File {"../picnic/packages/" + filename} not found.')

def create_node(parent, node_data, x, y):
    frame = tk.Frame(parent, borderwidth=1, relief='solid', padx=5, pady=5)
    frame.place(x=x, y=y)
    frame.x = x
    frame.y = y

    frame.filename_label = tk.Label(frame, text=node_data['filename'])
    frame.filename_label.pack()

    frame.snippet_label = tk.Label(frame, text=node_data['snippet'], justify='left')
    frame.snippet_label.pack()

    frame.bind('<Button-1>', lambda event: open_file_in_vscode(node_data['filename'], node_data['line_number']))
    frame.filename_label.bind('<Button-1>', lambda event: open_file_in_vscode(node_data['filename'], node_data['line_number']))
    frame.snippet_label.bind('<Button-1>', lambda event: open_file_in_vscode(node_data['filename'], node_data['line_number']))

    return frame

def update_ui(window, node_widgets, file_path):
    graph_data = read_graph(file_path)

    for node in graph_data['nodes']:
        node_widget = node_widgets[node['id']]
        node_widget.filename_label.config(text=node['filename'])
        node_widget.snippet_label.config(text=node['snippet'])

def draw_edge(canvas, source_widget, target_widget, color='black'):
    source_widget.update_idletasks()
    target_widget.update_idletasks()

    sx, sy = source_widget.x, source_widget.y
    tx, ty = target_widget.x, target_widget.y

    sw, sh = source_widget.winfo_width(), source_widget.winfo_height()
    tw, th = target_widget.winfo_width(), target_widget.winfo_height()

    canvas.create_line(sx + sw , sy + sh / 2, tx, ty + th / 2, fill=color, arrow=tk.LAST)

def display_graph(graph_data):
    window = tk.Tk()
    window.title('Data Flow Visualization')

    # Make the window open in full screen
    window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")

    canvas = Canvas(window, bg='white')
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = Scrollbar(window, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    

    window.update()  # Update to make sure widget sizes are calculated

    def update_ui_callback():
        node_widgets = {}
        last_source_id = None
        level = 0
        nodes_in_level = 0
        for node in graph_data['nodes']:
            if node['source_id'] is None or node['source_id'] != last_source_id:
                level += 1
                last_source_id = node['source_id']
                nodes_in_level = 0
            else: 
                nodes_in_level += 1
            x, y = nodes_in_level * 450 + 50, level * 150 + 50
            node_widget = create_node(canvas, node, x, y)
            node_widgets[node['id']] = node_widget
            if node['source_id'] is not None:
                draw_edge(canvas, node_widgets[node['source_id']], node_widget)
                
        update_ui(window, node_widgets, 'graph.json')
        window.after(1000, update_ui_callback)

    update_ui_callback()

    window.mainloop()

if __name__ == '__main__':
    graph_data = read_graph('graph.json')
    display_graph(graph_data)
