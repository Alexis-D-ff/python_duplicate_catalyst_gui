import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.font import Font
from ttkthemes import ThemedTk
import pathlib
import os
import sys
import threading
from ctypes import windll
from collections import defaultdict
from recursive_scandir import recursive_scandir
from read_and_hash import read_and_hash


windll.shcore.SetProcessDpiAwareness(1)

class FileNavigator(ttk.Frame):
    """
    This is the main TreeView widget of the GUI. It visualizes the directory content.
    Attributes:
    ----------
    directory 
    """
    def __init__(self, directory):
        ttk.Frame.__init__(self)
        s = ttk.Style()
        s.configure('Treeview', rowheight=24, font=('Segoe UI', 9))
        s.configure('Treeview.Heading', rowheight=24, borderwidth=5, font=('Segoe UI', 9))
        s.map('Treeview', background=[('selected', '#bb1e10')])
        
        self.folder_img = tk.PhotoImage(file = r"images\folder.png")
        img_img = tk.PhotoImage(file = r"images\img.png")
        pdf_img = tk.PhotoImage(file = r"images\pdf.png")
        txt_img = tk.PhotoImage(file = r"images\txt.png")
        word_img = tk.PhotoImage(file = r"images\word.png")
        xl_img = tk.PhotoImage(file = r"images\xl.png")
        self.icon = {".png": img_img, ".jpg": img_img, ".jpeg": img_img, ".tif": img_img, ".tiff": img_img, ".gif": img_img, ".ico": img_img,
                     ".pdf": pdf_img,
                     ".txt": txt_img, ".py": txt_img, ".csv": txt_img,
                     ".doc": word_img, ".docx": word_img,
                     ".xls": xl_img, ".xlsx": xl_img,
                     }
        self.unkwn_img = tk.PhotoImage(file = r"images\unkn.png")
        
        self._directory = directory
        
        self.file_after_renaming = ''
        
        self._tree = ttk.Treeview(self)
        self._tree['column'] = [*range(5)]
        for column in self._tree['column']:
            self._tree.column(column, anchor='center', stretch='yes', width=70, minwidth=40)
        self._tree.column('#0', width=940, minwidth=110)
        self._tree.column(4, width=145, minwidth=110)

        self._tree.heading('#0',text='Double click to collapse/expand folder or Alt+DoubleClick to open', anchor='w')
        self._tree.heading(0, text='Match')
        self._tree.heading(1, text='Active')
        self._tree.heading(2, text='Docs')
        self._tree.heading(3, text='New')
        self._tree.heading(4, text='Date')

        self.toggle = False
        self.toggle_single = False
        #self._tree.bind('<Double-Button-1>', self.collapse)
        #self._tree.bind('<<TreeviewSelect>>', self.show_details)
        #self._tree.bind('<Alt-Double-Button-1>', self.opening_file)
        
        self._tree['show'] = 'headings tree'
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._tree.yview, orient='vertical')
        tree_y_scroll_bar.pack(side='right', fill='y')
        self._tree.config(yscrollcommand=tree_y_scroll_bar.set)
        self._tree.pack(side='left', fill="both", expand=True)
        
    def set_folder(self, folder):
        self._directory = os.path.normpath(folder)
        self.refresh()
        self.grid(row=0,column=0, rowspan=2, padx=20, pady=(20,0), sticky='nsew')
        
    def refresh(self, a=self._directory):
        self._tree
        self._tree.delete(*self._tree.get_children())
        self._tree.insert(parent="",
                          index="end",
                          iid=self._directory,
                          text=self._directory,
                          image=self.folder_img,
                          open=True,
                          tags=("Directory", "root", a))
        
        for single_object in recursive_scandir(self._directory):
            if single_object.is_dir():
                directory_parent = pathlib.Path(single_object.path).parent
                self._tree.insert(parent=directory_parent,
                                    index="end",
                                    iid=single_object.path,
                                    text=single_object.name,
                                    image=self.folder_img,
                                    open=False,
                                    tags=("Directory", "\\", single_object),
                                    )
            else:
                file_parent = pathlib.Path(single_object.path).parent
                file_extension = pathlib.Path(single_object.path).suffix
                self._tree.insert(parent=file_parent,
                                  index="end",
                                  iid=single_object.path,
                                  text=single_object.name,
                                  values=(1,
                                          2,
                                          3,
                                          4,
                                          5,
                                          ),
                                  image=self.icon.get(file_extension) if self.icon.get(file_extension) else self.unkwn_img,
                                  tags=("File", file_extension, single_object.path)
                                  )

            
        return 1
        for root, directories, files in os.walk(self._directory, topdown=True):
            print(root, directories, files)
            for name in directories:
                self._tree.insert(parent=root,
                                  index="end",
                                  iid=os.path.join(root, name),
                                  text=name,
                                  image=self.folder_img,
                                  open=False,
                                  tags=("Directory", "\\", os.path.join(root, name)),
                                  )
            for name in files:
                fullpath = os.path.normpath(os.path.join(root, name))
                
                extension = os.path.splitext(name)[1]
                self._tree.insert(parent=root,
                                  index="end",
                                  iid=os.path.join(root, name),
                                  text=name,
                                  values=(1,
                                          2,
                                          3,
                                          4,
                                          5,
                                          ),
                                  image=self.icon.get(extension) if self.icon.get(extension) else self.unkwn_img,
                                  tags=("File", extension, os.path.join(root, name)))

class Message_box():
    """
    This class generates a simple messagebox to confir different actions
    Attributes:
        parent  - the ttk widget which is calling a messagebox
        title   - title of the messagebox to be shown
        message - message to be shown inside the box
        type    - type of the message_box (confirm exit or confirm action)
    """
    def __init__(self, parent, title: str, message: str, type: str):
        # Upon creation of an instance, check the type of message box
        if type == 'exit' and messagebox.askokcancel(title, message):
            parent.destroy()
            sys.exit()
        self.keep_going = False
        if type == 'confirm' and messagebox.askokcancel(title, message):
            # Continue only if OK button of the messagebox was pushed
            self.keep_going = True
    
    def pass_action(self):
        """
        This method returns the value of the binary keep_going variable,
        which controls the further execution of code after calling of the messagebox
        """
        return self.keep_going

class Buttons(ttk.Frame):
    """
    This class handles the appearance of the app buttons and its functionality.
    Attributes:
        parent  - parent ttk widget
        fnavigator  - a current instance of the file_navigator ttk treeview widget
        details     - a current instance of the details ttk treeview widget
        prog_bar    - ungrided ttk progress bar widget
    """
    def __init__(self, parent, fnavigator, prog_bar):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.fnavigator = fnavigator
        self.prog_bar = prog_bar
        
        s = ttk.Style()
        s.configure('my.TButton', font=('Segoe UI', 9), anchor='center',)
        self.background_label = tk.Label(self)
        self.background_label.grid(row=0, column=0, columnspan=2, pady=(0,0))
        
        self.b1 = ttk.Button(self,
                             text="Open Folder",
                             command=lambda: self.thread_func(self.openfolder),
                             width=30,
                             style='my.TButton')
        self.b1.grid(row=1,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.b2 = ttk.Button(self,
                             text="Web Parse Loaded Folder",
                             command=lambda: self.thread_func(self.parse_folder),
                             width=30,
                             style='my.TButton')
        self.b2.grid(row=2,column=0, columnspan=2, sticky='nsew', pady=(0,5), padx=(20,20), ipady=5, ipadx=5)
        
        self.b3 = ttk.Button(self,
                             text="Web Parse Selected File(s)",
                             command=lambda: self.thread_func(self.parse_selected),
                             width=30,
                             style='my.TButton')
        self.b3.grid(row=3,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.b4 = ttk.Button(self,
                             text="Move to Archive",
                             width=15,
                             command=lambda: self.thread_func(self.selection_to_archive),
                             style='my.TButton')
        self.b4.grid(row=4,column=0, sticky='nsw', pady=(0,10), padx=(20,0), ipady=5, ipadx=5)
        
        self.b5 = ttk.Button(self,
                             text="Move from Archive",
                             width=15,
                             command=lambda: self.thread_func(self.selection_out_archive),
                             style='my.TButton')
        self.b5.grid(row=4,column=1, sticky='nse', pady=(0,10), padx=(0,20), ipady=5, ipadx=5)
        
        self.b6 = ttk.Button(self,
                             text="Move All Obsolete Files to Archive",
                             command=lambda: self.thread_func(self.all_obsolete_archive),
                             width=30,
                             style='my.TButton')
        self.b6.grid(row=5,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.b7 = ttk.Button(self,
                             text="Rename Selected File",
                             command=self.rename_main_func,
                             width=30,
                             style='my.TButton')
        self.b7.grid(row=6,column=0, columnspan=2, sticky='nsew', pady=(0,15), padx=(20,20), ipady=5, ipadx=5)
        
        self.b8 = ttk.Button(self,
                             text="Exit",
                             command=lambda: Message_box(self.parent, "Confirm exit", "Do you want to quit?", "exit"),
                             width=30,
                             style='my.TButton')
        self.b8.grid(row=7,column=0, columnspan=2, sticky='nsew', padx=(50,50), ipady=5, ipadx=5)

        # Create a tuple of buttons to block/unblock them further
        self.buttons = (self.b1,
                        self.b2,
                        self.b3,
                        self.b4,
                        self.b5,
                        self.b6,
                        self.b7,
                        )
        
        self.prog = Prog_Bar()

    def thread_func(self, target_func):
        """
        This method generates a thread for each called function when the proper button is pressed.
        Threads are needed to get rid of app freezing during some function execution.
        """
        # Call a work function
        func = threading.Thread(target=target_func, daemon = True)
        func.start()
        # Disable all buttons except of the "EXIT"
        for button in self.buttons:
            button.state(["disabled"])

    def openfolder(self):
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
            self.fnavigator.set_folder(folder_select)
        # Enable all buttons
        for button in self.buttons:
            button.state(["!disabled"])
        # Stop the progress bar and ungrid it
        self.prog_bar.stoping()

    def parse_folder(self):
        """
        This method handles the file analysis (name analysis, web parsing, report reloading) of the whole selected root folder
        """
        keep_parse = Message_box(self.parent, "Confirm folder parsing", "Do you want to parse all files?", "confirm")
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
    
    def parse_selected(self):
        selected_files = self.fnavigator.select_to_update()
        if selected_files:
            func = threading.Thread(target=self.prog_bar.starting, daemon = True)
            func.start()
            ff.main(selected_files)
            self.details.changing_database()
            self.fnavigator.selection_refreshed(selected_files)
            self.fnavigator.show_details()
        else:
            pass
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
        confirm_moving = Message_box(self.parent, "Confirm file transfer", "Do you want to transfer each obsolete document to the realted archive folder?", "confirm")
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

class Prog_Bar(ttk.Frame):
    """
    This class generates a progress bar.
    """
    def __init__(self):
        ttk.Frame.__init__(self)
        self.b2 = ttk.Progressbar(self,
                                  orient = 'horizontal',
                                  length = 1000,
                                  mode = 'indeterminate',
                                  )
        
    def starting(self):
        """
        This method allows launching the progress bar
        """
        self.b2.pack(side='left', fill='both', expand=True)
        self.b2.start(50)
        
    def stoping(self):
        """
        This method allows stoping the progress bar
        """
        self.b2.pack_forget()
        self.b2.stop()
        
class Credits(ttk.Frame):
    """
    This class encapsulated credential info.
    """
    def __init__(self):
        ttk.Frame.__init__(self)
        text1 = ttk.Label(self, text='Designed from scratch by Alexis D.')
        text1.pack()
        
class Credits(ttk.Frame):
    """
    This class encapsulated credential info.
    """
    def __init__(self):
        ttk.Frame.__init__(self)
        text1 = ttk.Label(self, text='Designed from scratch by Alexis D.')
        text1.pack()
        
if __name__ == "__main__":
    
    root = ThemedTk()
    # Window icon
    root.wm_title('Rapid duplicates checker')
    
    # Configure grid
    root.rowconfigure(0,weight=0)
    root.rowconfigure(1,weight=200)
    root.rowconfigure(2,weight=0)
    root.rowconfigure(3,weight=0)
    root.columnconfigure(0,weight=1)
    root.columnconfigure(1,weight=20)
    fnavigator = FileNavigator(r'C:\Intel')
    
    credits = Credits()
    credits.grid(row=3,column=0, columnspan=2, sticky='we')
    
    prog = Prog_Bar()
    prog.grid(row=2,column=0, padx=(20,20),pady=(20,20), sticky='nsew')
    
    buttons = Buttons(root, fnavigator, prog)
    buttons.grid(row=0,column=1, padx=20, pady=(40,0), sticky='ns')
    
    # Add exit confirmation windows
    root.protocol('WM_DELETE_WINDOW', lambda: Message_box(root, "Confirm exit", "Do you want to quit?", "exit"))
    
    root.mainloop()