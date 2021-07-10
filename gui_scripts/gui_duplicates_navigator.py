import tkinter as tk
from tkinter import ttk
import pathlib
import os
import yaml
from os_duplicate_finder import Duplicates_Finder
from icon_loader import file_image_loader, unknown_icon_loader

class Duplicates_Navigator(ttk.Frame):
    """
    This class creates a supplementary treeview with found duplicates.
    To simplify the adjustment of visualization, the treeview and scrollbar widgets are created inside a ttk.Frame via .pack() method,
    then this Frame is visualized in the main tkinter windows via .grid() method.
    """
    def __init__(self, config_file_path: str):
        """
        Args:
        ----
        config_file_path: str
            path-object containing the path to the configuration yaml file
        """
        ttk.Frame.__init__(self)
        
        self.config_file_path = config_file_path
        with open(self.config_file_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        
        # Configure the appearance of the duplicates treeview
        duplicates_tree_style = ttk.Style()
        duplicates_tree_style.configure(**config['d_tree']['Tree'])
        
        # Default messages to be shown
        self.default_text = "Select folder(s) of file(s)"
        self.no_duplicates_message = 'No duplicates / Empty folder'
        
        # Initialize tkinter treeview GUI with default messages and scrollbars
        self._duplicates_tree = ttk.Treeview(self, show='tree', height=6, style=config['d_tree']['Tree']['style'])
        
        # Load tkinter image objects to be used as file icons
        self.img_dict = file_image_loader()
        self.unknown_ext_icon = unknown_icon_loader()
        
        # Initialize the treeview heading 
        head_label = ttk.Label(self, text='Duplicates (Double Click to open file or Alt+DoubleClick to open containing folder)')
        head_label.pack(fill="both")
        
        # Initialize and adjust the scroll bars
        tree_x_scroll_bar = ttk.Scrollbar(self, command=self._duplicates_tree.xview, orient='horizontal')
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._duplicates_tree.yview, orient='vertical')
        tree_x_scroll_bar.pack(side='bottom', fill='x')
        tree_y_scroll_bar.pack(side='right', fill='y')
        self._duplicates_tree.config(yscrollcommand=tree_y_scroll_bar.set, xscrollcommand=tree_x_scroll_bar.set)
        
        # Load bindings
        self.bindings()
        
        # Path the treeview inside the ttk.Frame
        self._duplicates_tree.pack(fill="both", expand=True)
    
    def bindings(self) -> None:
        """
        This method wraps the bindings for the duplicates tree view navigator.
        """
        self._duplicates_tree.bind('<Double-Button-1>', lambda x: self.opening_object('file'))
        self._duplicates_tree.bind('<Alt-Double-Button-1>', lambda x: self.opening_object('folder'))
    
    def find_duplicates(self, selected_objects: list) -> dict:
        """
        This method accepts a list of objects to be checked for duplicates, transforms it into directory paths, calls a duplicate finder
        and return all found duplicates.
        
        Args:
        ----
        selected_objects: list
            the list of objects to be analyzed. If the object is a directory -> scan all children and find any duplicates
            If the object is a file -> scan its parent directory and all children, including the file itself, and find any duplicates 
        
        Returns:
        -------
        duplicates_dict: dict
            a dict of duplicates in the following form:
                    file_hash: [duplicate1_path, duplicate2_path, ...]
        """
        # Only unique directories should be scanned
        directories_to_scan = set()
        
        for object in selected_objects:
            # Add the parent directory if a file is selected
            if object.is_file():
                parent_directory = pathlib.Path(object).parent
                directories_to_scan.add(parent_directory)
            else:
                directories_to_scan.add(object)
        
        # Call the duplicates_finder with the set of unique directories to be checked
        finder = Duplicates_Finder(directories_to_scan, self.config_file_path)
        duplicates_dict = finder.duplicates_getter()
        
        return duplicates_dict
    
    def insert_delete_message(self, message: str=None) -> None:
        """
        This method deletes all rows from the treeview and inserts a text message if provided.
        
        Args:
        ----
        message: str
            text message to be shown.
        """
        self._duplicates_tree.delete(*self._duplicates_tree.get_children())
        if message:
            self._duplicates_tree.insert(parent='',
                                        index="end",
                                        text=message,
                                        )
    
    def refresh(self, duplicates: dict=None) -> None:
        """
        This method visualizes the found duplicates inside the treeview.
        The visualization tree form is as follows:
            + File hash: {hash_1} File size: {size}
                {icon} duplicate_1_path
                {icon} duplicate_2_path
            + File hash: {hash_2} File size: {size}
                {icon} duplicate_1_path
                {icon} duplicate_2_path
        
        Args:
        ----
        duplicates: dict
            dictionary of found duplicates in the following form:
                    file_hash: [duplicate1_path, duplicate2_path, ...]
        """
        
        # Each duplicates scan clears the previous results
        self.insert_delete_message()
        
        if not duplicates:
            self.insert_delete_message(self.no_duplicates_message)
        
        # Define the default length of the duplicate path string
        # This string is used for widget width adjustment
        path_str_max_length = 0
        
        for hash, paths in duplicates.items():
            single_file_path = pathlib.Path(duplicates[hash][0])
            file_size = os.path.getsize(single_file_path)
            
            # Text to be visualized in the treeview
            hash_text = hash[:11]
            file_size_text = self.file_size_transform(file_size) 
            
            # Skip, if the hash is already in the list
            try:
                self._duplicates_tree.insert(parent='',
                                             index='end',
                                             iid=hash,
                                             text=f'Empty files. File hash: {hash_text}...' if file_size == 0
                                                    else f'File hash: {hash_text}... File size: {file_size_text}',
                                             open='yes',
                                             tags=('meta_line'),
                                             )
            except tk.TclError:
                pass
            
            for path in paths:
                try:
                    path_str_max_length = max(path_str_max_length, len(path))
                    file_extension = pathlib.Path(path).suffix
                    self._duplicates_tree.insert(parent=hash,
                                                 index='end',
                                                 iid=path,
                                                 text=path,
                                                 open='yes',
                                                 image=self.img_dict.get(file_extension) if self.img_dict.get(file_extension)
                                                        else self.unknown_ext_icon,
                                                 tags=('file_path', pathlib.Path(path)),
                                                 )
                except tk.TclError:
                    pass
        
        # This is the default width of the window
        def_field_length = self._duplicates_tree.column('#0')['width']
        
        # Change the width of the widget field if the string is too long
        str_length = int(path_str_max_length * 8.1 + 30)
        field_length = str_length if str_length > def_field_length else None
        if field_length:
            self._duplicates_tree.column('#0', anchor='w', width=field_length, stretch='yes')
        else:
            self._duplicates_tree.column('#0', anchor='w', stretch='no')
        
    def opening_object(self, object, event=None) -> str:
        """
        This method binds object opening methods.
        If a file is clicked, it will be opened by the standard os program.
        If a file is clicked with the alt button pressed, the parent folder will be opened in os.
        
        Args:
        ----
        object: str
            this argument controls if the file or its parent should be opened.
        event: None
            this argument binds the key pressing event to this method.
        
        Returns:
        -------
        'break': str
            this keyword unbinds the event from the default tkinter method.
        """
        selected_object = self._duplicates_tree.item(self._duplicates_tree.focus())['tags']
        selected_obj_type = selected_object[0]
        
        # The hash and file_size heading are skipped
        if selected_obj_type == 'file_path':
            selected_file_path = selected_object[1] if object == 'file' else pathlib.Path(selected_object[1]).parent
            
            # Filter out the OS access errors. If it doesn't open - c'est la vie :)
            try:
                os.startfile(selected_file_path)
            except OSError:
                pass
        
        return 'break'
    
    @staticmethod
    def file_size_transform(file_size: int) -> int:
        """
        This static method converts the file size in bytes to KB or MB at some thresholds.

        Args:
        ----
        file_size:int
            file size in bytes

        Returns:
        -------
        file_size_text: str
            the message, including the file size, to be visualized in the treeview widget
        """
        size_KB = file_size/1024
        if size_KB < 1:
            file_size_text = f'{int(file_size):,} B'
        elif size_KB > 99999:
            file_size_text = f'{int((file_size/1024)/1024):,} MB'
        else:
            file_size_text = f'{int(size_KB):,} KB'
            
        return file_size_text
