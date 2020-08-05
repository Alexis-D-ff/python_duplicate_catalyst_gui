from tkinter import ttk
import tkinter as tk
import threading
from tkinter import filedialog
from gui_message_box import Message_Box
import pathlib
import os

class Buttons(ttk.Frame):
    """
    This class handles the appearance of the app buttons and its functionality.
    Attributes:
        parent  - parent ttk widget
        fnavigator  - a current instance of the file_navigator ttk treeview widget
        details     - a current instance of the details ttk treeview widget
        prog_bar    - ungrided ttk progress bar widget
    """
    def __init__(self, parent, fnavigator, dnavigator, prog_bar):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.__fnavigator = fnavigator
        self.__dnavigator = dnavigator
        self.prog_bar = prog_bar
        
        s = ttk.Style()
        s.configure('my.TButton', font=('Segoe UI', 9), anchor='center',)
        self.background_label = tk.Label(self)
        self.background_label.grid(row=0, column=0, columnspan=2, pady=(0,0))
        
        self.folder_opener = ttk.Button(self,
                             text="Open Folder",
                             command=lambda: self.thread_func(self.open_folder),
                             width=30,
                             style='my.TButton')
        self.folder_opener.grid(row=1,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.find_duplicates = ttk.Button(self,
                             text="Find Duplicates",
                             command=lambda: self.thread_func(self.scan_duplicates),
                             width=30,
                             style='my.TButton')
        self.find_duplicates.grid(row=2,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.delete_file = ttk.Button(self,
                             text="Delete Selected File(s)",
                             command=lambda: self.thread_func(self.parse_selected),
                             width=30,
                             style='my.TButton')
        self.delete_file.grid(row=3,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.open_log = ttk.Button(self,
                             text="Access Permission Log",
                             command=self.open_log_file,
                             width=30,
                             style='my.TButton',
                             state='disabled',)
        self.open_log.grid(row=4,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.exit = ttk.Button(self,
                             text="Exit",
                             command=lambda: Message_Box(self.parent, "Confirm exit", "Do you want to quit?", "exit"),
                             width=30,
                             style='my.TButton')
        self.exit.grid(row=5,column=0, columnspan=2, sticky='nsew', padx=(50,50), ipady=5, ipadx=5)

        # Create a tuple of buttons to block/unblock them further
        self.buttons = (self.folder_opener,
                        self.find_duplicates,
                        self.delete_file,
                        )

    def thread_func(self, target_func):
        """
        This method generates a thread for each called function when the proper button is pressed.
        Threads are needed to get rid of app freezing during some function execution.
        """
        # Call a work function
        self.func = threading.Thread(target=target_func, daemon = True)
        self.func.start()
        # Disable all buttons except of the "EXIT"
        for button in self.buttons:
            button.state(["disabled"])
        self.open_log.state(["disabled"])

    def open_folder(self):
        """
        This method handles opening of a folder for ttk fnavigator treeview widget
        """
        folder_select = filedialog.askdirectory(initialdir = "/",
                                title = "Select a Folder with standards",
                                )
        if folder_select:
            # Launch a progress bar in a separate thread
            func = threading.Thread(target=self.prog_bar.starting, daemon = True)
            func.start()
            self.__fnavigator.set_folder(folder_select)
            self.__dnavigator.insert_message(self.__dnavigator.default_text)
        # Enable all buttons
        for button in self.buttons:
            button.state(["!disabled"])
            
        # Stop the progress bar and ungrid it
        self.prog_bar.stoping()
    
    def scan_duplicates(self):
        selected_paths = self.__fnavigator._tree.selection()
        
        if selected_paths:
            selected_objects = (pathlib.Path(path) for path in selected_paths)
            directories = [pathlib.Path(object.parent) if object.is_file() else object for object in selected_objects]
            if selected_paths:
                func = threading.Thread(target=self.prog_bar.starting, daemon = True)
                func.start()
                duplicates = self.__dnavigator.find_duplicates(directories)
                self.__dnavigator.fill_treeview(duplicates)
                #self.__fnavigator.update_duplicates(duplicates)
            else:
                pass
            
        for button in self.buttons:
            button.state(["!disabled"])

        try:
            if pathlib.Path('log_file.log').stat().st_size != 0:
                num_lines = sum(1 for line in open('log_file.log'))
                self.open_log['text'] = f"Access Permission Log ({num_lines})"
                self.open_log.state(["!disabled"])
        except:
            pass
        
        self.prog_bar.stoping()
    
    def open_log_file(self):
        
        try:
            os.startfile('log_file.log')
            
        except:
            pass
    
    def something(self):
        """
        This method handles the file analysis (name analysis, web parsing, report reloading) of the whole selected root folder
        """
        keep_parse = Message_Box(self.parent, "Confirm folder parsing", "Do you want to parse all files?", "confirm")
        # Start file analysis only if confirmed
        if keep_parse.pass_action() == True:
            # Create a prog bar in a separate thread
            func = threading.Thread(target=self.prog_bar.starting, daemon = True)
            func.start()
            # Call 
            ff.main(self.fnavigator.loaded_folder())
            # 
            self.details.changing_database()
            self.fnavigator.database_refreshed()
        # Enable all buttons
        for button in self.buttons:
            button.state(["!disabled"])
        self.prog_bar.stoping()
    
    def rename_main_func(self):
        if self.fnavigator.select_to_rename():
            selected_to_rename = self.fnavigator.select_to_rename()[1]
            item_position = self.fnavigator.select_to_rename()[2]
            start = PopUpConfirmQuit(self.parent, selected_to_rename, self)
            try:
                if self.renaming_flag:
                    ff.del_item(self.fnavigator.select_to_rename()[0])
                    self.fnavigator.rename_item(self.new_name, self.new_fullname, item_position)
                    self.details.changing_database()
            except AttributeError:
                pass
        else:
            pass
        for button in self.buttons:
            button.state(["!disabled"])
        
    def rename_check_permission(self, pop_window):
        self.new_name = pop_window.send_renamed()
        self.fullname = self.fnavigator.select_to_rename()[0]
        self.new_fullname = self.fullname.replace(self.fnavigator.select_to_rename()[1], self.new_name)
        try:
            os.rename(self.fullname, self.new_fullname)
            self.renaming_flag = True
        except PermissionError:
            self.renaming_flag = False
    
    def get_renaming_flag(self):
        """
        This method returns the flag value for renaming.
        It is called in PopUp renaming window.
        """
        return self.renaming_flag
    
    def selection_to_archive(self):
        func = threading.Thread(target=self.prog_bar.starting, daemon = True)
        func.start()
        dict_fullpaths = self.fnavigator.select_to_archive()
        for fullpath in dict_fullpaths:
            filename = dict_fullpaths[fullpath]['text']
            root = fullpath.replace(filename, '')
            if root[-9:] != '\Archive\\':
                archive_dir = root + 'Archive\\'
                path_meta = pathlib.Path(archive_dir)
                path_meta.mkdir(parents=True, exist_ok=True)
                new_fullname = archive_dir + filename
                os.rename(fullpath, new_fullname)
                self.fnavigator.items_to_archive(filename, fullpath, new_fullname, dict_fullpaths)
            else:
                pass
        for button in self.buttons:
            button.state(["!disabled"])
        self.prog_bar.stoping()
        
    def selection_out_archive(self):
        func = threading.Thread(target=self.prog_bar.starting, daemon = True)
        func.start()
        dict_fullpaths = self.fnavigator.select_to_archive()
        for fullpath in dict_fullpaths:
            filename = dict_fullpaths[fullpath]['text']
            root = fullpath.replace(filename, '')
            archive_parent = root.replace('Archive\\', '')
            new_fullname = archive_parent + filename
            try:
                os.rename(fullpath, new_fullname)
                self.fnavigator.items_out_archive(filename, fullpath, new_fullname, dict_fullpaths)
            except PermissionError:
                pass
        
        self.details.changing_database()
        self.details.new_window_refresh()
        for button in self.buttons:
            button.state(["!disabled"])
        self.prog_bar.stoping()
        
    def all_obsolete_archive(self):
        confirm_moving = Message_Box(self.parent, "Confirm file transfer", "Do you want to transfer each obsolete document to the realted archive folder?", "confirm")
        if confirm_moving.pass_action() == True:
            func = threading.Thread(target=self.prog_bar.starting, daemon = True)
            func.start()
            dict_fullpaths = self.fnavigator.select_to_archive_all()
            for fullpath in dict_fullpaths:
                filename = dict_fullpaths[fullpath]['text']
                root = fullpath.replace(filename, '')
                if root[-9:] != '\Archive\\':
                    archive_dir = root + 'Archive\\'
                    path_meta = pathlib.Path(archive_dir)
                    path_meta.mkdir(parents=True, exist_ok=True)
                    new_fullname = archive_dir + filename
                    os.rename(fullpath, new_fullname)
                    self.fnavigator.items_to_archive(filename, fullpath, new_fullname, dict_fullpaths)
                else:
                    pass
            self.details.changing_database()
        for button in self.buttons:
            button.state(["!disabled"])
        self.prog_bar.stoping()