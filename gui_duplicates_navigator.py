import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import pathlib
import os
from _os_duplicate_finder_v3 import Duplicates_Finder
from icon_loader import file_image_loader, unknown_icon_loader

class Duplicates_Navigator(ttk.Frame):
    """
    This class generates a supplementary treeview with all the detailed information of scanned + parsed file.
    Attributes:
        df - current database class instance (can be changed by calling db changing method)
        root - tkinter GUI window
    """
    def __init__(self):
        ttk.Frame.__init__(self)
        self.s = ttk.Style()
        self.def_font = Font(font=('Segoe UI', 8))
        self.s.configure('Details.Treeview', rowheight=20, font='TkDefaultFont')
        self.default_text = "Select folder(s) of file(s)"
        self.no_duplicates_message = 'No duplicates / Empty folder'
        
        
        # Initialize tkinter treeview GUI with default messages and scrollbars
        self._duplicates_tree = ttk.Treeview(self, show='tree', height=6, style='Details.Treeview')
        
        self.img_dict = file_image_loader()
        self.unknown_ext_icon = unknown_icon_loader()
        
        text1 = ttk.Label(self, text='Duplicates (Double Click to open file or Alt+DoubleClick to open containing folder)')
        text1.pack(fill="both")
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._duplicates_tree.yview, orient='vertical')
        tree_y_scroll_bar.pack(side='right', fill='y')
        tree_x_scroll_bar = ttk.Scrollbar(self, command=self._duplicates_tree.xview, orient='horizontal')
        tree_x_scroll_bar.pack(side='bottom', fill='x')
        self._duplicates_tree.config(yscrollcommand=tree_y_scroll_bar.set, xscrollcommand=tree_x_scroll_bar.set)
        
        # Bind clipboard copying and URL opening on Alt + Double click
        self._duplicates_tree.bind('<Double-Button-1>', lambda x: self.opening_object('file'))
        self._duplicates_tree.bind('<Alt-Double-Button-1>', lambda x: self.opening_object('folder'))
        
        self._duplicates_tree.pack(fill="both", expand=True)
    
    def find_duplicates(self, selected_objects):
                
        directories_to_scan = set()
        for object in selected_objects:
            # Skip if a folder was selected
            if object.is_file():
                parent_directory = pathlib.Path(object).parent
                directories_to_scan.add(parent_directory)
            else:
                directories_to_scan.add(object)
                
        finder = Duplicates_Finder(directories_to_scan)
        duplicates_dict = finder.duplicates_getter()
        
        return duplicates_dict
    
    def insert_delete_message(self, message=None):
        self._duplicates_tree.delete(*self._duplicates_tree.get_children())
        
        if message:
            self._duplicates_tree.insert(parent='',
                                        index="end",
                                        text=message,
                                        )
    
    def fill_treeview(self, selected_objects=None):
        """
        This method fills the treeview widget with details for the selected in main treeview files.
        Attributes:
            selected_files - full paths of selected in the main window files
        """
        
        self.insert_delete_message()
        
        if not selected_objects:
            self.insert_delete_message(self.no_duplicates_message)
        
        path_str_max_length = 0
        
        for hash, paths in selected_objects.items():
            # Each selected filename is going to be a parent field for related details
            single_file_path = pathlib.Path(selected_objects[hash][0])
            file_size = os.path.getsize(single_file_path)
            
            # Text to be visualized
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
        field_length = 0
        
        # The final length must be the max of : either the default length, the length of the filename,
        # or the length of the longest miss-info field
        if path_str_max_length and path_str_max_length != 0:
            str_length = int(path_str_max_length * 8.1 + 30)
            field_length = str_length if str_length > def_field_length else 0
        
        if field_length:
            self._duplicates_tree.column('#0', anchor='w', width=field_length, stretch='no')
        else:
            self._duplicates_tree.column('#0', anchor='w', stretch='yes')
    
    def opening_object(self, object, event=None):
        selected_object = self._duplicates_tree.item(self._duplicates_tree.focus())['tags']
        selected_obj_type = selected_object[0]
        
        if selected_obj_type == 'file_path':
            selected_file_path = selected_object[1] if object == 'file' else pathlib.Path(selected_object[1]).parent
            os.startfile(selected_file_path)
        
        return 'break'
    
    @staticmethod
    def file_size_transform(file_size: int):
        size_KB = file_size/1024
        if size_KB < 1:
            file_size_text = f'{int(file_size):,} B'
        elif size_KB > 99999:
            file_size_text = f'{int((file_size/1024)/1024):,} MB'
        else:
            file_size_text = f'{int(size_KB):,} KB'
            
        return file_size_text
