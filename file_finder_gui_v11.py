import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.font import Font
import webbrowser
from ttkthemes import ThemedTk
import pathlib
import os
import sys
import threading
from ctypes import windll
import file_finder_v2 as ff

windll.shcore.SetProcessDpiAwareness(1)

class FileNavigator(ttk.Frame):
    """
    
    """
    def __init__(self, directory, df, details, filler):
        ttk.Frame.__init__(self)
        self.details = details
        self.filler = filler
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
        
        self.database = df
        self.file_after_renaming = ''
        self.df = self.database.get_database()
        
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
        self._tree.bind('<Double-Button-1>', self.collapse)
        self._tree.bind('<<TreeviewSelect>>', self.show_details)
        self._tree.bind('<Alt-Double-Button-1>', self.opening_file)
        
        self._tree['show'] = 'headings tree'
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._tree.yview, orient='vertical')
        tree_y_scroll_bar.pack(side='right', fill='y')
        self._tree.config(yscrollcommand=tree_y_scroll_bar.set)
        self._tree.pack(side='left', fill="both", expand=True)
        
    
    def set_folder(self, folder):
        self.database.set_database()
        self.df = self.database.get_database()
        self._directory = os.path.normpath(folder)
        self.refresh()
        self.details.new_window_refresh()
        self.filler.grid_forget()
        self.grid(row=0,column=0, rowspan=2, padx=20, pady=(20,0), sticky='nsew')
    
    def database_refreshed(self):
        self.df = self.database.get_database()
        self.refresh()
        self.details.new_window_refresh()

    def refresh(self):
        self._tree
        self._tree.delete(*self._tree.get_children())
        self._tree.insert(parent="",
                          index="end",
                          iid=self._directory,
                          text=self._directory,
                          image=self.folder_img,
                          open=True,
                          tags=("Directory", "root", self._directory))
        for root, directories, files in os.walk(self._directory, topdown=True):
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
                single_meta_data = self.df.loc[self.df['fullpath'] == fullpath].squeeze()
                self.main_signs(single_meta_data)
                extension = os.path.splitext(name)[1]
                self._tree.insert(parent=root,
                                  index="end",
                                  iid=os.path.join(root, name),
                                  text=name,
                                  values=(self.web_match,
                                          self.status,
                                          self.amount_urls,
                                          self.amount_new,
                                          self.ver_time,
                                          ),
                                  image=self.icon.get(extension) if self.icon.get(extension) else self.unkwn_img,
                                  tags=("File", extension, os.path.join(root, name)))
    
    def selection_refreshed(self, items):
        self.df = self.database.get_database()
        selected_tuple = items
        for document in selected_tuple:
            single_meta_data = self.df.loc[self.df['fullpath'] == document].squeeze()
            self.main_signs(single_meta_data)
            self._tree.item(document,
                            values=(self.web_match,
                                    self.status,
                                    self.amount_urls,
                                    self.amount_new,
                                    self.ver_time,
                                    )
                            )
    
    def main_signs(self, series):
        try:
            if series.loc['web_match'] == True or  series.loc['web_match'] == 'True':
                self.web_match = '✅'
            elif series.loc['web_match'] == 'Multi':
                self.web_match = '⦁'
            else:
                self.web_match = ''
            
            if series.loc['status'] == 'En vigueur':
                self.status = '✅'
            elif series.loc['status'] == 'Annulée':
                self.status = '❎'
            elif series.loc['status'] == 'Multi':
                self.status = '⦁'
            else:
                self.status = ''
            
            # if pd.notna(series.loc['amount_urls']):
            #     val = pd.to_numeric(series.loc['amount_urls'])
            #     self.amount_urls = int(val)
            # else:
            #     self.amount_urls = ''
            
            # if pd.notna(series.loc['amount_new']):
            #     val2 = pd.to_numeric(series.loc['amount_new'])
            #     self.amount_new = int(val2)
            # else:
            #     self.amount_new = ''
            
            self.ver_time = series.loc['scan_time'][:-3]
        except KeyError:
            self.web_match = ''
            self.status = ''
            self.amount_urls = ''
            self.amount_new = ''
            self.ver_time = 'None'
        
    def collapse(self, event=None):
        if self._tree.identify_column(event.x) == '#0' and self._tree.identify_region(event.x, event.y) == 'heading':
            main_folder = self._tree.get_children()[0]
            def open_children(parent):
                self._tree.item(parent, open=True)
                for child in self._tree.get_children(parent):
                    open_children(child)
            def close_children(parent):
                for child in self._tree.get_children(parent):
                    self._tree.item(child, open=False)
                    close_children(child)
                    
            def handleOpenEvent():
                self.toggle = not self.toggle
                if self.toggle:
                    open_children(main_folder)
                else:
                    close_children(main_folder)
            handleOpenEvent()
        if self._tree.identify_column(event.x) == '#0' and self._tree.identify_region(event.x, event.y) != 'heading':
            rowID = self._tree.identify('item', event.x, event.y)
            def open_children(parent):
                self._tree.item(parent, open=True)
                for child in self._tree.get_children(parent):
                    open_children(child)
            def close_children(parent):
                for child in self._tree.get_children(parent):
                    self._tree.item(child, open=False)
                    close_children(child)
                    
            def handleOpenEvent():
                if self._tree.item(rowID)['open'] != True:
                    open_children(rowID)
                else:
                    self.toggle_single = not self.toggle_single
                    if self.toggle_single:
                        open_children(rowID)
                    else:
                        close_children(rowID)
            if self._tree.item(rowID)['tags'][0] == 'Directory':
                handleOpenEvent()
            return 'break'
        
    def show_details(self, event=None):
        selected_files = self._tree.selection()
        selected_files = tuple((os.path.normpath(filepath) for filepath in selected_files))
        self.details.refresh(selected_files)
    
    def select_to_update(self):
        files = tuple()
        for item in self._tree.selection():
            if self._tree.item(item)['tags'][0] == 'File':
                files += (item,)
        return files
    
    def loaded_folder(self):
        loaded_folder = os.path.normpath(self._tree.get_children()[0])
        return loaded_folder
    
    def select_to_rename(self):
        try:
            if self._tree.item(self._tree.focus())['tags'][0] == 'File':
                item_index = self._tree.index(self._tree.focus())
                return self._tree.item(self._tree.focus())['tags'][2], self._tree.item(self._tree.focus())['text'], item_index
            else:
                return 0
        except:
            pass
    
    def select_to_archive(self):
        selected_files = self._tree.selection()
        selected_dict = {}
        selected_files = tuple((os.path.normpath(filepath) for filepath in selected_files))
        for link in selected_files:
            if self._tree.item(link)['tags'][0] == 'File':
                selected_dict[link] = self._tree.item(link)
        return selected_dict
    
    def select_to_archive_all(self):
        all_files = list()
        main_folder = self._tree.get_children()[0]
        def get_all_children(parent):
            all_files.append(parent)
            for child in self._tree.get_children(parent):
                get_all_children(child)
                    
        get_all_children(main_folder)
        
        all_cancelled_dict = {}
        all_files = tuple((os.path.normpath(filepath) for filepath in all_files))
        for link in all_files:
            try:
                c = self.df.loc[self.df['fullpath'] == link, ['status']].iloc[0, 0]
                if c == 'Annulée':
                    all_cancelled_dict[link] = self._tree.item(link)
            except (ValueError, IndexError):
                pass
        return all_cancelled_dict
    
    def rename_item(self, new_name, new_fullname, item_position):
        extension = os.path.splitext(new_name)[1]
        root = new_fullname.replace(new_name, '')[:-1]
        try:
            self._tree.insert(parent=root,
                            index=item_position,
                            iid=new_fullname,
                            text=new_name,
                            values=(''
                                    '',
                                    '',
                                    '',
                                    '',
                                    'None',
                                    ),
                            image=self.icon.get(extension) if self.icon.get(extension) else self.unkwn_img,
                            tags=("File", extension, new_fullname),
                            )
            
            self._tree.delete(self._tree.focus())
            self.details.refresh(self._tree.selection())
        except tk.TclError:
            pass
        
    
    def items_to_archive(self, filename, old_fullpath, new_fullpath, dict_fullpaths):
        extension = os.path.splitext(filename)[1]
        archive_dir = new_fullpath.replace(filename, '')[:-1]
        root = archive_dir.replace('\\Archive', '')
        if not self._tree.exists(archive_dir):
            self._tree.insert(parent=root,
                              index="end",
                              iid=archive_dir,
                              text='Archive',
                              image=self.folder_img,
                              open=True,
                              tags=("Directory", "\\", archive_dir),
                              )
        
        self._tree.insert(parent=archive_dir,
                        index="end",
                        iid=new_fullpath,
                        text=filename,
                        values=dict_fullpaths[old_fullpath]['values'],
                        image=self.icon.get(extension) if self.icon.get(extension) else self.unkwn_img,
                        tags=("File", extension, new_fullpath),
                        )
        
        self._tree.item(archive_dir, open=True)
        
        self._tree.delete(old_fullpath)
        ff.change_item(old_fullpath, new_fullpath)

    def items_out_archive(self, filename, old_fullpath, new_fullpath, dict_fullpaths):
        extension = os.path.splitext(filename)[1]
        archive_parent = new_fullpath.replace(filename, '')[:-1]
        try:
            self._tree.insert(parent=archive_parent,
                            index="end",
                            iid=new_fullpath,
                            text=filename,
                            values=dict_fullpaths[old_fullpath]['values'],
                            image=self.icon.get(extension) if self.icon.get(extension) else self.unkwn_img,
                            tags=("File", extension, new_fullpath),
                            )
            self._tree.delete(old_fullpath)
            ff.change_item(old_fullpath, new_fullpath)
        except tk.TclError:
            pass
    
    def opening_file(self, event=None):
        selected_files = self._tree.item(self._tree.focus())['tags'][2]
        os.startfile(selected_files)
        return 'break'

class Buttons(ttk.Frame):
    """
    This class handles the appearance of the app buttons and its functionality.
    Attributes:
        parent  - parent ttk widget
        fnavigator  - a current instance of the file_navigator ttk treeview widget
        details     - a current instance of the details ttk treeview widget
        prog_bar    - ungrided ttk progress bar widget
    """
    def __init__(self, parent, fnavigator, details, prog_bar):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.fnavigator = fnavigator
        self.details = details
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
        self.details.changing_database()
        self.details.new_window_refresh()
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

class PopUpConfirmQuit(tk.Toplevel):
    """
    This class generates a TopLevel popup that asks for confirmation that the user 1) wants to quit OR 2) wants to rename a file.
    If not, the popup closes and no further action is taken
    Attributes:
        parent      - parent ttk widget
        filename    - selected filename for changing
        buttons     - instance of class encapsulating buttons
    """
    def __init__(self, parent, filename, buttons):
        super().__init__(parent)
        self.wm_title('Renaming')
        self.filename = filename
        self.initial_filename = filename
        self.buttons = buttons
        # Appear this windows in the screen's center
        w = max(300, len(filename)*8)
        h = 110
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.grab_set()
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.attributes("-toolwindow", 1)
        self.message = ttk.Label(self, text="Rename selected file", font=('Segoe UI', 9))
        self.entry_field = ttk.Entry(self, width=max(250, len(filename)*7))
        self.entry_field.bind('<Return>', self.get_renamed)
        rename = ttk.Button(self, text='Rename', command=self.get_renamed)
        cancel = ttk.Button(self, text='Cancel', command=self.destroy)
        self.entry_field.insert(0, self.filename)
        self.temp = self.entry_field.get()
        self.message.pack(expand=True, padx=5, pady=5)
        self.entry_field.pack(padx=5, pady=5)
        rename.pack(side='left', padx=5, pady=5, ipady=5, ipadx=5)
        cancel.pack(side='right', padx=5, pady=5, ipady=5, ipadx=5)
        self.wait_window(self)
    
    def get_renamed(self, event=None):
        """
        This method sets a new filename
        """
        if self.entry_field.get() != self.filename:
            self.filename = self.entry_field.get()
            self.buttons.rename_check_permission(self)
            # Check renaming permissions
            renaming_flag = self.buttons.get_renaming_flag()
            if renaming_flag:
                self.destroy()
                return 'break'
            else:
                self.filename = self.initial_filename
                self.message.config(text="Permission denied. Close the file.")
        else:
            pass

    def send_renamed(self):
        """
        This method returns the new filename
        """
        return self.filename
    
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

class Details(ttk.Frame):
    """
    This class generates a supplementary treeview with all the detailed information of scanned + parsed file.
    Attributes:
        df - current database class instance (can be changed by calling db changing method)
        root - tkinter GUI window
    """
    def __init__(self, df, root):
        ttk.Frame.__init__(self)
        self.root = root
        self.s = ttk.Style()
        self.def_font = Font(font=('Segoe UI', 8))
        self.s.configure('Details.Treeview', rowheight=20, font='TkDefaultFont')
        
        # The initial database is loaded when class is initialized
        self.database = df
        # If database need to be changed, new variable will be used
        self.df = self.database.get_database()
        
        # Containers for results
        self.main_search_url = {}
        self.mast_urls = {}
        
        # Initialize tkinter treeview GUI with default messages and scrollbars
        self._tree = ttk.Treeview(self, show='tree', height=6, style='Details.Treeview')
        self._tree.insert(parent='',
                          index="end",
                          text="Select file(s)",
                          )
        text1 = ttk.Label(self, text='Details (Alt+DoubleClick to open web and copy to clipboard)')
        text1.pack(fill="both")
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._tree.yview, orient='vertical')
        tree_y_scroll_bar.pack(side='right', fill='y')
        tree_x_scroll_bar = ttk.Scrollbar(self, command=self._tree.xview, orient='horizontal')
        tree_x_scroll_bar.pack(side='bottom', fill='x')
        self._tree.config(yscrollcommand=tree_y_scroll_bar.set, xscrollcommand=tree_x_scroll_bar.set)
        
        # Bind clipboard copying and URL opening on Alt + Double click
        self._tree.bind('<Alt-Double-Button-1>', self.open_url)
        
        self._tree.pack(fill="both", expand=True)
    
    def changing_database(self):
        """
        This method re-loads the meta_file with the database
        """
        self.database.set_database()
        self.df = self.database.get_database()
        
    def new_window_refresh(self):
        """
        This method resets the treeview
        """
        self._tree.delete(*self._tree.get_children())
        self._tree.insert(parent='',
                          index="end",
                          text="Select file(s)",
                          )
        
    def refresh(self, selected_files):
        """
        This method fills the treeview widget with details for the selected in main treeview files.
        Attributes:
            selected_files - full paths of selected in the main window files
        """
        self._tree
        self._tree.delete(*self._tree.get_children())
        
        # This is the default width of the window
        dynamic_width = 445
        
        for file in selected_files:
            # Skip if a folder was selected
            if any(self.df['fullpath'] == file):
                single_meta_data = self.df.loc[self.df['fullpath'] == file].squeeze()
                try:
                    # Associate the selected file with URL used for searching at afnor.fr
                    self.main_search_url[single_meta_data['filename']] = single_meta_data['search_url']
                except TypeError:
                    # Skip if the file cannot be scalped at all
                    break
                self.data_tuple(single_meta_data)
                
                # The final length must be the max of : either the defult length, the length of the filename,
                # or the length of the longest miss-info field
                str_length = len(single_meta_data['filename']) * 7 + 50
                str_length2 = self.length_miss*7 + 60
                dynamic_width = max(str_length, dynamic_width, str_length2)
                
                # Each selected filename is going to be a parent field for related details
                self._tree.insert(parent='',
                                index='end',
                                iid=file,
                                text=single_meta_data['filename'],
                                open='yes',
                                )
                # Insert all generated details for a single file
                for data_sample in self.mast_data_tuple:
                    self._tree.insert(parent=file,
                                    index='end',
                                    text=data_sample,
                                    open='yes',
                                    tags='')
                    
        self._tree.column('#0', anchor='w', width=dynamic_width, stretch='no')
    
    def data_tuple(self, single_file):
        """
        This method generated all available data to be displayed for a single file
        Attributes:
            single_file - a pandas.Series object, corresponding to a full data line for a file in csv meta
        """
        self.mast_data_tuple = []
        self.length_miss = 0
        
        # First display the missing data
        # if pd.notna(single_file['miss_data']):
        #     doc_miss_separated = single_file['miss_data'].split(';')
        #     self.mast_data_tuple.append('⚠ Missing data:')
        #     for single_miss_data in doc_miss_separated:
        #         self.mast_data_tuple.append(f"      {single_miss_data}")
        #         self.length_miss = max(self.length_miss, len(single_miss_data))
        
        # Then display the found standard docs
        # if pd.notna(single_file['web_numbers']):
        #     doc_number_separated = single_file['web_numbers'].replace('@',' : ').split(';')[:-1]
        #     doc_url_separated = single_file['web_URLs'].split(';')[:-1]
        #     self.mast_data_tuple.append('🔍 Web found documents:')
        #     # If a document has a web_number, it certainly will have at least one web_url (or several),
        #     # so I grab each web_url and put it inside a dictionary, that will be used for alt-doubleclick we opening
        #     for i, single_doc_number in enumerate(doc_number_separated):
        #         self.mast_data_tuple.append(f"      {single_doc_number}")
        #         self.mast_urls[single_doc_number] = doc_url_separated[i]
                
        # # Then display newer document, if there are any
        # if pd.notna(single_file['new_numbers']):
        #     doc_new_number_separated = single_file['new_numbers'].replace('@',' : ').split(';')[:-1]
        #     doc_new_url_separated = single_file['new_URLs'].split(';')[:-1]
        #     self.mast_data_tuple.append('🔔 Found newer documents:')
        #     # If a document has a new_numbers, it certainly will have at least one new_url (or several),
        #     # so I grab each new_url and put it inside a dictionary, that will be used for alt-doubleclick we opening
        #     for i, single_doc_number in enumerate(doc_new_number_separated):
        #         self.mast_data_tuple.append(f"      {single_doc_number}")
        #         self.mast_urls[single_doc_number] = doc_new_url_separated[i]
        
        # # Then display the doc number, extracted during file scanning
        # if pd.notna(single_file['extr_number']):
        #     self.mast_data_tuple.append('🏷 Doc number extracted from filename:')
        #     self.mast_data_tuple.append(f"      {single_file['extr_number']}")
        
        # # Then display the doc date, extracted during file scanning
        # if pd.notna(single_file['extr_date']):
        #     self.mast_data_tuple.append('📆 Doc date extracted from filename:')
        #     self.mast_data_tuple.append(f"      {single_file['extr_date']}")
            
        # # Then display the doc title, extracted during file scanning
        # if pd.notna(single_file['extr_title']):
        #     self.mast_data_tuple.append('📜 Doc title extracted from filename:')
        #     self.mast_data_tuple.append(f"      {single_file['extr_title']}")
        
    def open_url(self, event=None):
        """
        This method copies the text in the selected filed in the clipboard, and
        opens the associated URL for doc numbers
        """
        cur_item = self._tree.item(self._tree.focus())
        try:
            # Try to get the URL from the formed previously dict and open it
            current_url = self.mast_urls[cur_item['text'][6:]]
            webbrowser.open(current_url)
        except KeyError:
            pass
        try:
            # For the filename (parent of each sub-tree) open the URL used for searching
            current_url = self.main_search_url[cur_item['text']]
            webbrowser.open(current_url)
        except (KeyError, TypeError):
            pass
        
        # Copy data in clipboard, but cut something according to the selected field
        self.root.clipboard_clear()
        if cur_item['text'][0] == ' ':
            cur_item['text'] = cur_item['text'][6:]
        elif cur_item['text'][-1] == ':':
            cur_item['text'] = cur_item['text'][2:-1]
        self.root.clipboard_append(cur_item['text'])
        
        # This is used to unbind default double-click event for the tkinter treeview
        return 'break'

class Data_frame:
    """
    This is a dataclass.
    It generates pandas.DataFrame for the meta_data_file (file, containing all parsed data for all ever scanned files).
    If needed, it can re-load database after any manipulation (removal of duplicates, updating, partial updating, etc.)
    """
    def __init__(self):
        self.meta_path = ff.meta_path()[0]
        try:
            pass
            # self.db = pd.read_csv(self.meta_path, dtype={'amount_new': pd.Int64Dtype(),
            #                                              'amount_urls': pd.Int64Dtype(),
            #                                              'extr_number': 'object'})
        except Exception as e:
            print(e)
            sys.exit()
            
    def get_database(self):
        """
        This method simply returns loaded database as pandas.DataFrame
        """
        return 1 #self.db
    
    def set_database(self):
        """
        This method reloads the database from local meta_file
        """
        try:
            pass
            # self.db = pd.read_csv(self.meta_path, dtype={'amount_new': pd.Int64Dtype(),
            #                                              'amount_urls': pd.Int64Dtype(),
            #                                              'extr_number': 'object'})
        except Exception as e:
            print(e)
            sys.exit()

if __name__ == "__main__":
    
    root = ThemedTk()
    # Window icon
    root.wm_title('Rapid duplicates checker')
    
    # Load meta data file for visualizations
    meta_path = ff.meta_path()[0]
    dataframe = Data_frame()
    
    # Configure grid
    root.rowconfigure(0,weight=0)
    root.rowconfigure(1,weight=200)
    root.rowconfigure(2,weight=0)
    root.rowconfigure(3,weight=0)
    root.columnconfigure(0,weight=1)
    root.columnconfigure(1,weight=20)
    
    # Create an instance of each UI class
    details = Details(dataframe, root)
    details.grid(row=1,column=1, rowspan=2, padx=(0,20), pady=(20,20), sticky='nsew')
    
    # Create a filler label, just to fill the space before any folder would be loaded
    fill_space = tk.Label(root, width=172, height=350)
    fill_space.grid(row=0,column=0, rowspan=2, padx=20, pady=(20,0), sticky='nsew')
    
    fnavigator = FileNavigator(root, dataframe, details, fill_space)
    
    prog = Prog_Bar()
    prog.grid(row=2,column=0, padx=(20,20),pady=(20,20), sticky='nsew')
    
    buttons = Buttons(root, fnavigator, details, prog)
    buttons.grid(row=0,column=1, padx=20, pady=(40,0), sticky='ns')
    
    credits = Credits()
    credits.grid(row=3,column=0, columnspan=2, sticky='we')
    
    # Add exit confirmation windows
    root.protocol('WM_DELETE_WINDOW', lambda: Message_box(root, "Confirm exit", "Do you want to quit?", "exit"))
    
    root.mainloop()