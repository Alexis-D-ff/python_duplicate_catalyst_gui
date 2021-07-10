from tkinter import ttk
import tkinter as tk
import os
import pathlib
from recursive_scandir_v3 import recursive_scandir

class File_Navigator(ttk.Frame):
    """
    This is the main TreeView widget of the GUI. It visualizes the directory content.
    """
    def __init__(self, filler, directory=None):
        """
        Attributes:
        ----------
        directory 
        """
        ttk.Frame.__init__(self)
        s = ttk.Style()
        s.configure('Treeview', rowheight=24, font=('Segoe UI', 9))
        s.configure('Treeview.Heading', rowheight=24, borderwidth=5, font=('Segoe UI', 9))
        s.map('Treeview', background=[('selected', '#6d6087')])
        
        self.filler = filler
        self.image_loader()
        
        
        self._directory = directory
        self.file_after_renaming = ''
        
        self._tree = ttk.Treeview(self)
        #self._tree['column'] = [*range(1)]
        self._tree.column('#0', anchor='center', stretch='yes', width=900)

        self._tree.heading('#0', text='Double Click to open file or Alt+DoubleClick to open containing folder', anchor='w')
        #self._tree.heading(0, text='Duplicates')

        self.toggle = False
        self.toggle_single = False
        self._tree.bind('<Double-Button-1>', self.clicked_refresh)
        self._tree.bind('<Button-1>', self.indicator_expand)
        self._tree.bind('<Double-Button-1>', lambda x: self.opening_object('file'))
        self._tree.bind('<Alt-Double-Button-1>', lambda x: self.opening_object('folder'))
        
        self._tree['show'] = 'headings tree'
        tree_y_scroll_bar = ttk.Scrollbar(self, command=self._tree.yview, orient='vertical')
        tree_y_scroll_bar.pack(side='right', fill='y')
        self._tree.config(yscrollcommand=tree_y_scroll_bar.set)
        self._tree.pack(side='left', fill="both", expand=True)
    
    def image_loader(self):
        
        def image_wrapper(path: str):
            norm_path = os.path.normpath(path)
            return tk.PhotoImage(file=norm_path)
                
        self.folder_img = image_wrapper(r'images\folder.png')
        img_img = image_wrapper(r'images\img.png')
        pdf_img = image_wrapper(r'images\pdf.png')
        txt_img = image_wrapper(r'images\txt.png')
        word_img = image_wrapper(r'images\word.png')
        xl_img = image_wrapper(r'images\xl.png')
        self.unkwn_img = image_wrapper(r'images\unkn.png')
        
        self.icon = {".png": img_img, ".jpg": img_img, ".jpeg": img_img, ".tif": img_img, ".tiff": img_img, ".gif": img_img, ".ico": img_img,
                     ".pdf": pdf_img,
                     ".txt": txt_img, ".py": txt_img, ".csv": txt_img,
                     ".doc": word_img, ".docx": word_img,
                     ".xls": xl_img, ".xlsx": xl_img,
                     }
    
    def set_folder(self, folder):
        self._directory = pathlib.Path(folder)
        self.refresh()
        self.grid(row=0,column=0, rowspan=2, padx=20, pady=(20,0), sticky='nsew')
    
    def clicked_refresh(self, event=None):
        selected_object = self._tree.item(self._tree.focus())
        if selected_object['tags'][0] == 'Directory':
            self.refresh(clicked_directory=selected_object)
            self.expand_directory(selected_object)
        
        return 'break'
    
    def indicator_expand(self, event=None):
        if self._tree.identify_element(event.x, event.y) == 'Treeitem.indicator':
            selected_object = self._tree.item(self._tree.identify_row(event.y))
            self.refresh(clicked_directory=selected_object)
        
    def refresh(self, clicked_directory=None):
        self.filler.grid_forget()
        if clicked_directory:
            root_directory = clicked_directory['tags'][2]
            self._tree.delete(*self._tree.get_children(root_directory))
            
        else:
            root_directory = self._directory
            self._tree.delete(*self._tree.get_children())
            
            self._tree.insert(parent="",
                          index="end",
                          iid=root_directory,
                          text=root_directory,
                          image=self.folder_img,
                          open=True,
                          tags=("Directory", "root", root_directory))
        
        for object in recursive_scandir(root_directory):
            if object.is_dir():
                directory_parent = pathlib.Path(object.path).parent
                self._tree.insert(parent=directory_parent,
                                    index="end",
                                    iid=object.path,
                                    text=object.name,
                                    image=self.folder_img,
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
                                    image=self.icon.get(file_extension) if self.icon.get(file_extension) else self.unkwn_img,
                                    tags=("File", file_extension, object.path)
                                    )
    
    def select_to_rename(self):
        try:
            if self._tree.item(self._tree.focus())['tags'][0] == 'File':
                item_index = self._tree.index(self._tree.focus())
                return self._tree.item(self._tree.focus())['tags'][2], self._tree.item(self._tree.focus())['text'], item_index
            else:
                return 0
        except:
            pass
    
    def rename_item(self, new_name, new_fullname, item_position):
        extension = os.path.splitext(new_name)[1]
        root = new_fullname.replace(new_name, '')[:-1]
        try:
            self._tree.insert(parent=root,
                            index=item_position,
                            iid=new_fullname,
                            text=new_name,
                            values=(''),
                            image=self.icon.get(extension) if self.icon.get(extension) else self.unkwn_img,
                            tags=("File", extension, new_fullname),
                            )
            
            self._tree.delete(self._tree.focus())
            self.details.refresh(self._tree.selection())
        except tk.TclError:
            pass
    
    def expand_directory(self, current_directory, event=None):
        self._tree.item(current_directory['tags'][2], open=True)
        
        return 'break'
    
    
    def opening_object(self, object, event=None):
        selected_object = self._tree.item(self._tree.focus())['tags']
        selected_obj_type = selected_object[0]
        
        if selected_obj_type == 'File':
            selected_file_path = selected_object[1] if object == 'file' else pathlib.Path(selected_object[1]).parent
            os.startfile(selected_file_path)
        
        return 'break'
    
    def update_duplicates(self, duplicates):
        for _, paths in duplicates.items():
            for path in paths:
                    self._duplicates_tree.insert(parent=hash,
                                                 index='end',
                                                 iid=path,
                                                 text=f'📜 {path}',
                                                 open='yes',
                                                 tags=('file_path', pathlib.Path(path)),
                                                 )
                    path_str_max_length = max(path_str_max_length, len(path))