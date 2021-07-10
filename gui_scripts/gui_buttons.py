import tkinter
from tkinter import ttk
import threading
from tkinter import filedialog
from typing import Callable
import yaml
from gui_scripts.gui_message_box import Message_Box
import pathlib
import os

class Buttons(ttk.Frame):
    """
    This class controls the appearance of the buttons and their functionality.
    """
    def __init__(self, parent: object, fnavigator: object, dnavigator: object, prog_bar: object, config_file_path: str):
        """
        Args:
        ----
        parent: object
            the main root tkinter widget. It is used for calling message windows after some actions.
            
        fnavigator: object
            the current instance of the file navigator tk.treeview widget
        dnavigator: object
            the current instance of the duplicates ttk.treeview widget
        prog_bar: object
            the ungrided ttk.progress bar widget
        config_file_path: str
            path-object containing the path to the configuration yaml file
        """
        ttk.Frame.__init__(self, parent)
        
        with open(config_file_path, "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        
        self.log_file = pathlib.Path(self.config['log'])
        
        self.parent = parent
        self.__fnavigator = fnavigator
        self.__dnavigator = dnavigator
        self.prog_bar = prog_bar
        
        # Spawn buttons
        self.create_buttons()
        self.grid_buttons()
        
        # Configure the appearance
        buttons_style = ttk.Style()
        buttons_style.configure(**self.config['buttons_style'])
        
        # Create a tuple of buttons to block/unblock them further
        self.buttons = (self.folder_opener,
                        self.find_duplicates,
                        self.delete_file,
                        )
        
    def create_buttons(self) -> None:
        """
        This method wraps the creation of button widgets.
        """
        self.folder_opener = ttk.Button(self,
                             text="Open Folder",
                             command=lambda: self.thread_func(self.open_folder),
                             width=30,
                             style=self.config['buttons_style']['style'])
        self.find_duplicates = ttk.Button(self,
                             text="Find Duplicates",
                             command=lambda: self.thread_func(self.scan_duplicates),
                             width=30,
                             style=self.config['buttons_style']['style'],
                             state='disabled',)
        self.delete_file = ttk.Button(self,
                             text="Delete Selected File(s)",
                             command=lambda: self.thread_func(self.file_remove),
                             width=30,
                             style=self.config['buttons_style']['style'],
                             state='disabled',)
        self.open_log = ttk.Button(self,
                             text="Access Permission Log",
                             command=self.open_log_file,
                             width=30,
                             style=self.config['buttons_style']['style'],
                             state='disabled',)
        self.exit = ttk.Button(self,
                             text="Exit",
                             command=lambda: Message_Box(self.parent, "Confirm exit", "Do you want to quit?", "exit"),
                             width=30,
                             style=self.config['buttons_style']['style'])
    
    def grid_buttons(self) -> None:
        """
        This method grids the buttons with the required visualization parameters.
        """
        self.folder_opener.grid(row=1,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        self.find_duplicates.grid(row=2,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        self.delete_file.grid(row=3,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        self.open_log.grid(row=4,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        self.exit.grid(row=5,column=0, columnspan=2, sticky='nsew', padx=(50,50), ipady=5, ipadx=5)

    def thread_func(self, target_func: Callable) -> None:
        """
        This method generates a thread for each called function when the proper button is pressed.
        Each action creates a separate thread, so i.e. progress bar casting or log file opening can be executed during
        duplicate scanning, etc.
        
        Args:
        ----
        target_func: Callable
            action that is called by the button
        """
        self.func = threading.Thread(target=target_func, daemon=True)
        self.func.start()
        
        # Disable all buttons except of the "EXIT"
        for button in self.buttons:
            button.state(["disabled"])

    def open_log_file(self) -> None:
        """
        This method wraps the opening of the log file with a standard os program.
        """
        try:
            os.startfile(self.log_file)
        except:
            pass
    
    def open_folder(self) -> None:
        """
        This method handles the opening of a folder for the ttk file navigator treeview widget.
        """
        # Explicitly gray out the exit and log access buttons, when the directory choice window is active
        self.exit.state(["disabled"])
        self.open_log.state(["disabled"])
        
        folder_select = filedialog.askdirectory(initialdir = "/",
                                                title = "Select a Folder",
                                                )
        if folder_select:
            # Launch a progress bar in a separate thread
            func = threading.Thread(target=self.prog_bar.starting, daemon=True)
            func.start()
            self.__fnavigator.set_folder(folder_select)
            self.__dnavigator.insert_delete_message(self.__dnavigator.default_text)
            
            # Enable all buttons
            for button in self.buttons:
                button.state(["!disabled"])
            self.log_button_state_switch()
        
        # Enable all buttons if any folder was already loaded before.
        if self.__fnavigator._directory:
            for button in self.buttons:
                button.state(["!disabled"])
            self.log_button_state_switch()
        
        # Explicitly enable the exit and log access buttons.
        self.exit.state(["!disabled"])
        self.folder_opener.state(["!disabled"])
        
        # Stop the progress bar and ungrid it
        self.prog_bar.stoping()
    
    def scan_duplicates(self) -> None:
        """
        This method gets the selected objects of the file navigator treeview (a directory or a file)
        and launches the search for duplicates (inside the directory for a directory and inside the parent
        directory for a file).
        """
        selected_paths = self.__fnavigator._tree.selection()
        
        if selected_paths:
            selected_objects = (pathlib.Path(path) for path in selected_paths)
            directories = [pathlib.Path(object.parent) if object.is_file() else object for object in selected_objects]
            if selected_paths:
                # Start the progress bar
                func = threading.Thread(target=self.prog_bar.starting, daemon = True)
                func.start()
                duplicates = self.__dnavigator.find_duplicates(directories)
                self.__dnavigator.refresh(duplicates)
            else:
                pass
        
        # Re-activate the buttons and stop the progress bar
        for button in self.buttons:
            button.state(["!disabled"])
        self.log_button_state_switch()
        self.prog_bar.stoping()
    
    def log_button_state_switch(self) -> None:
        """
        This method verifies if the log file contains any error messages and if so, makes the access log file button available,
        and puts the number of errors in the button text.
        """
        try:
            if pathlib.Path('log_file.log').stat().st_size == 0:
                self.open_log.state(["disabled"])
            else:
                num_lines = sum(1 for line in open('log_file.log'))
                self.open_log['text'] = f"Access Permission Log ({num_lines})"
                self.open_log.state(["!disabled"])
        except:
            pass
    
    def file_remove(self) -> None:
        """
        This method deletes the file from os, and after that removes the corresponding lines from the file navigator and
        duplicates treeviews.
        """
        # Filter out empty selections
        try:
            # Call a confirmation window widget
            confirm_deleting = Message_Box(self.parent,
                                            "Confirm deleting file(s)",
                                            "Do you want to delete the selected file(s)?",
                                            "confirm")
            if confirm_deleting.pass_action() == True:
                for item in self.__dnavigator._duplicates_tree.selection():
                    item_obj = self.__dnavigator._duplicates_tree.item(item)
                    if item_obj['tags'][0] == 'file_path':
                            try:
                                path_obj = pathlib.Path(item)
                                os.remove(path_obj)
                                self.__dnavigator._duplicates_tree.delete(item)
                                # If the path was never accessed in the file_navigator_tree, it doesn't exist there
                                # so skip if nothing to delete
                                try:
                                    self.__fnavigator._tree.delete(item)
                                except tkinter.TclError:
                                    pass
                            except (OSError, PermissionError):
                                pass 
        
        except AttributeError:
            pass
        
        # Re-activate the buttons and stop the progress bar
        for button in self.buttons:
            button.state(["!disabled"])
        self.prog_bar.stoping()