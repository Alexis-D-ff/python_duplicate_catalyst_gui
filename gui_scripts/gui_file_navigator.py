from tkinter import ttk
import os
import pathlib
import yaml
from recursive_scandir import recursive_scandir
from icon_loader import file_image_loader, directory_image_loader, unknown_icon_loader

class File_Navigator(ttk.Frame):
    """
    This is the main TreeView widget of the GUI. It visualizes the directory content.
    To simplify the adjustment of visualization, the treeview and scrollbar widgets are created inside a ttk.Frame via .pack() method,
    then this Frame is visualized in the main tkinter windows via .grid() method.
    
    The objects of the treeview are obtained by the os.scandir() method (which is much faster than os.walk()).
    The nested directories are scanned dynamically, only when the user expands them. This crucially increases the performance of the
    treeview loading.
    """
    def __init__(self, filler: object, config_file_path: str):
        """
        Args:
        ----
        filler: object
            tkinter filler widget object, spawned at the app starting to handle the window aspect ratio.
            
        config_file_path: str
            path-object containing the path to the configuration yaml file.
        """
        ttk.Frame.__init__(self)
        
        self.config_file_path = config_file_path
        with open(self.config_file_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        
        # Configure the appearance of the treeview
        treeview_style = ttk.Style()
        treeview_style.configure(**config['f_tree']['Heading'])
        treeview_style.configure(**config['f_tree']['Tree'])
        treeview_style.map('Treeview', **config['f_tree']['Tree']['map'])
        
        self.filler = filler
        self.img_dict = file_image_loader()
        self.unknown_ext_icon = unknown_icon_loader()
        self.directory_icon = directory_image_loader()
        
        # Create a treeview widget and adjust its appearance
        self._tree = ttk.Treeview(self, show='headings tree')
        self._tree.column('#0', anchor='center', stretch='yes', width=900)
        self._tree.heading('#0', text='Double Click to open file or Alt+DoubleClick to open containing folder', anchor='w')
        
        # Set the default directory to None
        self._directory = None
        
        # Cast the scroll bar
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._tree.yview, orient='vertical')
        tree_y_scroll_bar.pack(side='right', fill='y')
        self._tree.config(yscrollcommand=tree_y_scroll_bar.set)
        
        # Load bindings
        self.bindings()
        
        # Path the treeview inside the ttk.Frame
        self._tree.pack(side='left', fill="both", expand=True)
    
    def bindings(self) -> None:
        """
        This method wraps the bindings for the file tree view navigator.
        """
        self._tree.bind('<Double-Button-1>', lambda x: self.expand_or_open('file'))
        self._tree.bind('<Button-1>', self.expand_scan_dirs)
        self._tree.bind('<Alt-Double-Button-1>', lambda x: self.expand_or_open('folder'))
    
    def set_folder(self, folder: str) -> None:
        """
        This is a setter that changes the working directory of the widget.

        Args:
        ----
        folder: str
            path to the directory to be visualized.
        """
        self._directory = pathlib.Path(folder)
        self.refresh()
        
        # Grid the ttk.Frame (which encapsulates treeview + scrollbar) at the main tkinter window
        self.grid(row=0,column=0, rowspan=2, padx=20, pady=(20,0), sticky='nsew')
    
    def expand_or_open(self, object: str=None, event=None) -> str:
        """
        This method wraps the self.refresh(), self.expand() and os.startfile() methods and is used for key binding actions.
        
        If a directory is clicked, it will be scanned by os.scandir(), visualized and expanded.
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
        selected_object = self._tree.item(self._tree.focus())
        
        # A directory clicked without the Alt modifier should be expanded.
        if selected_object['tags'][0] == 'Directory' and object != 'folder':
            self.refresh(clicked_directory=selected_object)
            self.expand_directory(selected_object)
            return 'break'
        
        # A file clicked without the Alt modifier should be opened,
        # Alt modifier should open either the clicked directory or the parent directory for a clicked file.
        else:
            if object == 'folder' and selected_object['tags'][0] == 'File':
                selected_file_path = pathlib.Path(selected_object['tags'][2]).parent
                
            else:
                selected_file_path = pathlib.Path(selected_object['tags'][2])
            
            # Filter out the OS access errors. If it doesn't open - c'est la vie :)
            try:
                os.startfile(selected_file_path)
            except OSError:
                pass
        
        return 'break'
    
    def expand_directory(self, current_directory: str, event=None) -> str:
        """
        This method expands the directory at the treeview navigator.
        Args:
        ----
        current_directory: str
            the path of the clicked directory.
            This path also defines the directory inside the treeview as follows:
            treeview.item(iid=current_directory)
            iid is used to perform actions with treeview items
        
        Returns:
        -------
        'break': str
            this keyword unbinds the event from the default tkinter method.
        """
        self._tree.item(current_directory['tags'][2], open=True)
        
        return 'break'
    
    def expand_scan_dirs(self, event=None) -> None:
        """
        This method wraps the self.refresh() method with the default tkinter folder opening event.
        When the user clicks on the Treeitem.indicator, the directory is scanned and visualized and then it expands.
        """
        if self._tree.identify_element(event.x, event.y) == 'Treeitem.indicator':
            selected_object = self._tree.item(self._tree.identify_row(event.y))
            self.refresh(clicked_directory=selected_object)
        
    def refresh(self, clicked_directory: dict=None) -> None:
        """
        This method is used for the dynamic visualization of directories. If the user opens a directory, this method scans the nested objects
        and visualizes it.
        
        Args:
        ----
        clicked_directory: dict
            this dictionary contains the parameters of the clicked tkinter treeview object.
            if this dictionary is provided, only the clicked directory will be scanned and filled with treeview objects.
        
        """
        # Remove the filler tkinter grid
        self.filler.grid_forget()
        
        if clicked_directory:
            # If and existing directory should be refreshed, first delete the child inside it,
            # to avoid insertion conflicts
            root_directory = clicked_directory['tags'][2]
            self._tree.delete(*self._tree.get_children(root_directory))
            
        else:
            root_directory = self._directory
            self._tree.delete(*self._tree.get_children())
            self._tree.insert(parent="",
                              index="end",
                              iid=root_directory,
                              text=root_directory,
                              image=self.directory_icon,
                              open=True,
                              tags=("Directory", "root", root_directory)
                              )
        
        # Scan directory and it children and insert it into treeview
        for object in recursive_scandir(root_directory, self.config_file_path):
            if object.is_dir():
                directory_parent = pathlib.Path(object.path).parent
                self._tree.insert(parent=directory_parent,
                                    index="end",
                                    iid=object.path,
                                    text=object.name,
                                    image=self.directory_icon,
                                    open=False,
                                    tags=("Directory", "\\", object.path),
                                    )
            else:
                file_parent = pathlib.Path(object.path).parent
                file_extension = pathlib.Path(object.path).suffix
                self._tree.insert(parent=file_parent,
                                    index="end",
                                    iid=object.path,
                                    text=object.name,
                                    image=self.img_dict.get(file_extension) if self.img_dict.get(file_extension)
                                                        else self.unknown_ext_icon,
                                    tags=("File", file_extension, object.path)
                                    )