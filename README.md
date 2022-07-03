# Duplicate Catalyst GUI app
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1Hv0j33qYxzmLlCD3ZIyAVVdzwPkz0Hph">
</p>

## About
This app allows accessing directories and files with the GUI tree views, in a similar way as an OS file explorer.

Any directory can be scanned for duplicates. All the duplicates are then visualized in a separate widget and also can be accessed or deleted.



# Summary
[1. Development tools](#1-development-tools)

[2. Installation](#2-installation)

[3. Functionality](#3-functionality)

&emsp;&emsp;[3.1 Directories loading](#31-directories-loading)

&emsp;&emsp;[3.2 Accessing files and directories](#32-accessing-files-and-directories)

&emsp;&emsp;[3.3 Finding duplicates](#33-finding-duplicates)

&emsp;&emsp;[3.4 Permissions log file](#34-permissions-log-file)

&emsp;&emsp;[3.5 Deleting duplicates](#35-deleting-duplicates)

[4. Development tricks](#4-development-tricks)

&emsp;&emsp;[4.1 Recursive os.scandir()](#41-recursive-osscandir)

&emsp;&emsp;[4.2 Duplicates detection with SHA](#42-duplicates-detection-with-sha)

&emsp;&emsp;[4.3 Collisions](#43-collisions)

[5. Credentials](#5-credentials)

[6. Footnotes](#6-footnotes)

## Acknoledgement
This app was inspired once by a colleague of mine when I did my thesis. He just asked me one day "Hey, I have a folder, there are hundreds of files inside it and there are also some damn duplicates, named differently, in different subfolders. Can't you make a small python script to find all of them?"

Then suddenly a small CLI script became a GUI app to simplify it for anyone who thinks that command line can steal his soul :)


## 1. Development tools
Environment:
`python=3.8.6`

Framework:
`tkinter`

## 2. Installation

Change directory to the app's one:
```
cd *full_path_to_the_app*
```

Install the required packages:
```
pip install -r requirements.txt
```

Start the executive file:
```
python main_exec.py
```

## 3. Functionality
### 3.1 Directories loading
The default directory is not initialized. Please press the "Open Folder" button and load any directory you would like to work with:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1z6_Yf2_vBGX9iAjfbE7IIFiMeMof5TJQ">
</p>

After loading, two tree view widgets become available. The left treeview is the file navigator, and the right one is the duplicates navigator.

The app is designed for the dynamic scan of directories. The recursion limit of the custom scandir function is set to 2 by default. This means that the chosen root folder will be fully scanned (recursion step 1), and the nested directories of the root folder also (recursion step 2). But no the children objects of the nested directories.

To increase the performance, the nested directories are not fully scanned. The app finds the first object inside the directory, available by the `os.scandir()` method, just to visualize the directory as not empty.

If you work with the Windows standard file explorer, you are not aware if the folder you are accessing is empty or not, until you go inside it. This app fixes that.

Check the gif above, the content of the Program Files directory is scanned, but all the nested directories are quasi-empty (currently there's only one random child inside them). But when the user clicks to the directory to expand, it fills with all children. So you the user won't recognize this small trick.

### 3.2 Accessing files and directories
### Expand directories
Any time user clicks the directory on the main tree view widget, it expands (if not empty):
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1l7rIqVO03_qwaHpg_V3RSfVQtwCGTzYG">
</p>

The click event is bound to the recursive scandir method. The clicked object is scanned, all found children then being visualized and nested directories are scanned for being empty/not (the recursion limit is 2  during any access of directories).

### Access files and directories in OS

Whenever the user double clicks on any file, the standard OS program will start this file:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1p-GrYrLX5_TLlHy0yNozKcLpJzP9t9-1">
</p>

In case of any exception, the OS should handle it. If there is no standard program associated with this file extension, it won't be opened.

If the user double clicks on any file, or any directory, with the Alt modifier button the standard OS file explorer will open the directory (parent directory in case of file):
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=12bYhTEucxcWE1OIVNu_Hc5hyA5HZJqa4">
</p>

### 3.3 Finding duplicates
To launch the duplicate finder module, select a directory on the main tree view widget, to be analyzed, and click the "Find Duplicates" button:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1cb3JCnWEn8Orm8rXl8tqq9A8dnQOAZF8">
</p>

If a file is selected instead of the directory, then its parent directory will be scanned:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1uyzyRS7xO3jYnmBtHgpWm7k9Vp6lcfZf">
</p>

To analyze the root directory, click on any file inside it or the directory path at the top.

Each scanning refreshes the widget content.

If the directory is empty or contains no duplicates, the appropriate message will be shown on the duplicates widget.

The duplicates widget, as the file navigator, allows accessing the files and their parent directories with double click for files:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1zHbqIJ3EOWcl1pPyyKAgJjSjLbxcJD6n">
</p>

or ALt + double click for the parent directory:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1DUL18AIU28-kkESzsH5vxy8zi01TZkgY">
</p>

### 3.4 Permissions log file
The grayed "Access Permission File" button becomes available if any OSPermission exception was raised. In this case, the exception is logged in the logfile, and the amount of caught exceptions is visualized on the button.  
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1AsIaobqFNefSzvnDDML5_0K6eToE1ey1">
</p>

Exceptions can be captures during scanning of the duplicates, or just loading of the directory:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1e-sWXT6Y3U0GEY59ufl2OFqb25Rztt3l">
</p>

The log file name and path are defined in the `config.yaml` file. The file resets after each app session, but the lines are added for all duplicate scanning or folder openings exceptions during one app session.


### 3.5 Deleting duplicates
The "Delete Selected File(s)" button takes the selected rows in the **duplicates tree view widget** as entries. After that the `os.remove()` method tries to delete the files, and if the removal is successful, the rows from the main and the duplicates tree views are removed simultaneously:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1ddf6pFJf3Ib6enuHi5HS4kKjFkFwuJg1">
</p>

## 4. Development tricks

### 4.1 Recursive os.scandir()
The conventional way to scan files in python is `os.walk()` method, which can be used to scan all children objects of a directory. However, it extremely lows down the scanning performance for any directory with a quite large number of children objects, as it accesses the object stats. That is why the `os.scandir()` method is used in this project.

A custom recursive function is designed to limit the number of children for a single scan:

```
for object in sorted_scandir:
                # If the object inside the parent directory is unreachable, update the logfile and pass to the next object
                try:
                    if object.is_dir(follow_symlinks=False):
                        yield object
                        current_recurs_step += 1
                        
                        # Continue to scan children if the recursion counter allows it.
                        if current_recurs_step < recursion_limit or recursion_limit == 0:
                            yield from recursive_scandir(object.path,
                                                         config_file_path,
                                                         recursion_limit=recursion_limit,
                                                         current_recurs_step=current_recurs_step)
                            # The recursion counter must be reset to 1 to yield the rest of the root directory
                            current_recurs_step = 1
                        else:
                            # For nested directories, yield only the first object.
                            # This crucially increases the performance
                            first_object = os.scandir(object.path)
                            try: 
                                yield next(first_object)
                            except:
                                pass
                        
                    else:
                        yield object
                except PermissionError as permission_err:
                    logging.basicConfig(**config['logger'])
                    logging.error(permission_err)
                    pass
```

This function is also called by the duplicates finder in order to return all the objects (removing the recursion limit: `recursion_limit=0`) of a directory. These objects are further analyzed stepwise and the non-duplicates are being filter out.


### 4.2 Duplicates detection with SHA

Duplicates finding is designed as follows:

At the first step, the `recursive_scandir()` accesses all the objects (without recursion limit) in the root directory. File sizes are then put as the keys to a dictionary, and the file paths are the values of this dictionary.
```
file_size_dict = defaultdict(list)  # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
        for path in self.paths:
            for object in recursive_scandir(path, self.config_file_path, recursion_limit=0):
                if object.is_file():
                    try:
                        file_size_dict[object.stat().st_size].append(object.path)
                    except OSError as os_err:
                        # not accessible (permissions, etc) - pass on
                        logging.error(os_err)
                        pass
```

At the second step, only the dictionary `items()` with `len(values) > 2` are scanned. The first 1024 bytes segment of the file content is hashed and used as a dictionary key with the file size together. The file paths are the values of this dictionary.
```
for file_size, file_paths in file_dict.items():
            if len(file_paths) < 2:
                continue    # this file size is unique, no need to spend CPU cycles on it

            for single_file_path in file_paths:
                try:
                    file_hash = read_and_hash(single_file_path, first_segment=first_segment)
                    # the key is the hash on the first 1024 bytes plus the size - to
                    # avoid collisions on equal hashes in the first part of the file
                    if first_segment:
                        self._segment_file_size_dict[(file_hash, file_size)].append(single_file_path)
                    else:
                        self._duplicates[file_hash].append(single_file_path)

                except (OSError,):
                    # the file access might've changed till the exec point got here continue
                    if not first_segment:
                        self._duplicates = {f_hash:f_size for (f_hash, f_size) in self._duplicates.items() if len(f_size) > 1}
```

At the third step, the `items()` of the last dictionary are analyzed, again only if `len(values) > 2`. Then the hash of the full file content is taken as the dictionary key (in this case `first_segment: bool=False`). Finally, if the full hash contains several paths, all the duplicates are detected!

### 4.3 Collisions
The default used hash algorithm is SHA1. According to <sup>[1](#myfootnote1)</sup> the worse probability of collision for the SHA1 algorithm is about 4*10<sup>-19</sup>. Thus, we can count that the universe will collapse before any conflict appears :)
You can also change the hash algorithm (it is the `hash_func` keyword argument of the `read_and_hash()` function)


At this example a standard `.doc` file was modified by a single symbol and duplicates scanning was launched. No duplicates detected, as it suppose to be:
<p align="center">
<img src="https://drive.google.com/uc?export=view&id=1k0tYccr3Y9NpfOtL5NSpBBar9oYivM4E">
</p>

## 5. Credentials
The app is developed by Alexis D. [LinkedIn](https://www.linkedin.com/in/dmshnkff/) during the thesis and has been updated multiple times after it :)

## 6. Footnotes
<a name="myfootnote1">1</a>: https://pthree.org/2014/03/06/the-reality-of-sha1/#:~:text=It%20should%20take%202%5E160,of%20only%202%5E61%20operations.