import tkinter as tk
from ttkthemes import ThemedTk
import pathlib
import yaml
from ctypes import windll

# Adjust the DPI of the app in the Windows environment for the tkinter rendering
try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

from gui_scripts.gui_file_navigator import File_Navigator
from gui_scripts.gui_duplicates_navigator import Duplicates_Navigator
from gui_scripts.gui_buttons import Buttons
from gui_scripts.gui_progress_bar import Progress_Bar
from gui_scripts.gui_message_box import Message_Box
from gui_scripts.gui_credentials import Credentials

if __name__ == "__main__":
    
    # Load the config yaml file
    config_file_path = pathlib.Path('config.yaml')
    with open(config_file_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # Initialize tkinter main widget
    root = ThemedTk()
    root.state('zoomed')
    root.wm_title('Duplicate Catalyst')
    
    # Load the main icon
    icon_path = pathlib.Path(config['images']['app_icon_path'])
    app_icon = tk.PhotoImage(file=icon_path)
    root.iconphoto(False, app_icon)
    
    # Configure the app widgets grid weights
    root.rowconfigure(1, weight=1)
    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=1)
    
    # Create a filler label, just to fill the space before any folder would be loaded
    filler_widget = tk.Label(root, width=124, height=350)
    filler_widget.grid(row=0, column=0, padx=20, pady=(20,0), sticky='nsew')
    
    # Create widget objects
    file_navigator = File_Navigator(filler_widget, config_file_path)
    duplicates_navigator = Duplicates_Navigator(config_file_path)
    credentials = Credentials()
    progress_bar = Progress_Bar()
    buttons = Buttons(root, file_navigator, duplicates_navigator, progress_bar, config_file_path)
    
    # Set widgets grid parameters
    duplicates_navigator.grid(row=1, column=1, rowspan=2, padx=(0, 20), pady=(20, 20), sticky='nsew')
    credentials.grid(row=3, column=0, columnspan=2, sticky='we')
    progress_bar.grid(row=2, column=0, padx=(20, 20),pady=(20, 20), sticky='nsew')
    buttons.grid(row=0, column=1, padx=(20, 20), pady=(40, 20), sticky='ns')
    
    # Add exit confirmation windows
    root.protocol('WM_DELETE_WINDOW',
                  lambda: Message_Box(root, "Confirm exit", "Do you want to quit?", "exit"))
    
    root.mainloop()