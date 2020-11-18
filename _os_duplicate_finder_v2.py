from typing import List
from collections import defaultdict
import os
from read_and_hash import read_and_hash
from recursive_scandir_v3 import recursive_scandir


class Duplicates_Finder():
    """
    This class scans the root directory, extracts all subdirectories, files and finds all the duplicates during scanning.
    """
    def __init__(self, paths: List[str]):
        """
        Arguments:
        ---------
        paths: List[str]
            list of path-like objects, the paths of the directories to be scanned for duplicates.
        """
        self.paths = paths
        self.file_size_dict = defaultdict(list)  # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
        self.segment_file_size_dict = defaultdict(list)  # dict of (single_segment_size, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
        self.duplicates = defaultdict(list)   # dict of full_file_hash: full_path_to_file_string
    
    def get_files(self, single_segment_size: int=2048):
        """
        This method 
        """
        
        for path in self.paths:
            for object in recursive_scandir(path, recursion_limit=0):
                if object.is_file():
                    try:
                        size_dict[object.stat.st_size].append(object.path)
                    except (OSError,):
                        # not accessible (permissions, etc) - pass on
                        pass

        # For all files with the same file size, get their hash on the 1st 1024 bytes only
        for file_size, file_paths in size_dict.items():
            if len(file_paths) < 2:
                continue    # this file size is unique, no need to spend CPU cycles on it

            for single_file_path in file_paths:
                try:
                    first_segment_hash = read_and_hash(single_file_path, first_segment=True)
                    # the key is the hash on the first 1024 bytes plus the size - to
                    # avoid collisions on equal hashes in the first part of the file
                    # credits to @Futal for the optimization
                    hashes_on_1k[(first_segment_hash, file_size)].append(single_file_path)
                except (OSError,):
                    # the file access might've changed till the exec point got here 
                    continue

        # For all files with the hash on the 1st 1024 bytes, get their hash on the full file - collisions will be duplicates
        for __, paths_list in hashes_on_1k.items():
            if len(paths_list) < 2:
                continue    # this hash of fist 1k file bytes is unique, no need to spend cpy cycles on it

            for file_path in paths_list:
                try: 
                    full_hash = read_and_hash(file_path, first_chunk_only=False)
                    duplicate = hashes_full.get(full_hash)
                    if duplicate:
                        print("Duplicate found: {} and {}".format(filename, duplicate))
                    else:
                        hashes_full[full_hash] = filename
                except (OSError,):
                    # the file access might've changed till the exec point got here 
                    continue
    def check_duplicates(self):
        pass