import tkinter as tk
import pathlib
import yaml

with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

def directory_image_loader():
    """
    This function loads the path to the folder icon from the config file, transforms it to tk.PhotoImage object and returns.
    
    Returns:
    -------
    folder_img: object
        tkinter image object of the directory icon
    """
    directory_icon_path = pathlib.Path(config['images']['obj_icons']['folders']['ico_path'])
    folder_img = tk.PhotoImage(file=directory_icon_path)
    
    return folder_img

def unknown_icon_loader():
    """
    This function loads the path to the unknown file icon from the config file, transforms it to tk.PhotoImage object and returns.
    
    Returns:
    -------
    unknown_img: object
        tkinter image object of the unknown file icon
    """
    directory_icon_path = pathlib.Path(config['images']['obj_icons']['unkn_files']['ico_path'])
    unknown_img = tk.PhotoImage(file=directory_icon_path)
    
    return unknown_img

def file_image_loader():
    """
    This function loads the path to a sequence of file icons from the config file, transforms it to tk.PhotoImage objects and returns.
    
    Returns:
    -------
    icon_dict: dict
        dictionary of file extensions linked to the appropriate tkinter image objects
    """
    icon_dict = {}
    supported_files_dict = config['images']['obj_icons']
    
    for _, ico_params in supported_files_dict.items():
        icon_path = pathlib.Path(ico_params['ico_path'])
        icon_object = tk.PhotoImage(file=icon_path)
        for extension in ico_params['extensions']:
            icon_dict[extension] = icon_object
    
    return icon_dict

