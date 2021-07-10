from typing import Set
from collections import defaultdict
from read_and_hash import read_and_hash
from recursive_scandir import recursive_scandir
import logging

# Define setting of logging for permission rejections
logging.basicConfig(handlers=[logging.FileHandler('log_file.log', 'w', 'utf-8')],
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S'
                    )

class Duplicates_Finder():
    """
    This class scans the root directory, extracts paths to all files in all subdirectories
    and finds the duplicates during scanning.
    """
    def __init__(self, paths: Set[str], config_file_path: str):
        """
        Args:
        ----
        paths: set{str}
            set of path-like objects, the paths of the directories to be scanned for duplicates.
        config_file_path: str
            path-object containing the path to the configuration yaml file.
        """       
        self.config_file_path = config_file_path
        self.paths = paths
        self._segment_file_size_dict = defaultdict(list)  # dict of (single_segment_size, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
        self._duplicates = defaultdict(list)   # dict of full_file_hash: full_path_to_file_string
    
    def duplicates_getter(self):
        """
        This accessor wraps the scan_files and check_duplicates methods and returns all found duplicates.
        
        Returns:
        -------
        self._duplicates: dict
            a dictionary of all found duplicates inside the root directory : {file_hash: [duplicate_path_1, duplicate_path_2, ...]}
        """
        file_size_dict = self.scan_files()
        self.check_duplicates(file_size_dict, first_segment=True)
        self.check_duplicates(self._segment_file_size_dict, first_segment=False)
        
        return self._duplicates

    def scan_files(self):
        """
        This method scans all objects in the root directory and forms a dictionary of files with the same size.
        
        Returns:
        -------
        file_size_dict: dict
            a dictionary of all files inside root directory : {file_size: [file_path_1, file_path_2]}
        """
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
        
        return file_size_dict

    def check_duplicates(self, file_dict: dict, first_segment: bool=False):
        """
        This method accepts a dictionary of potential duplicates, gets their hashes (partial or full) and append paths of files with
        same hashes to the appropriate attribute dictionary (self._segment_file_size_dict and self._duplicates).
        
        Arguments:
        ---------
        file_dict: dict
            dictionary of potential duplicates in the following form:
            the keys are file properties (file size or tuple(file size, first segment has));
            the values are paths to files with identic properties
        
        first_segment: bool
            switch, toggling the binary reading of the first file segment or full file content 
        """
        # For all files with the same file size, get their hash on the 1st 1024 bytes only
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
                    # the file access might've changed till the exec point got here 
                    continue
        
        if not first_segment:
            self._duplicates = {f_hash:f_size for (f_hash, f_size) in self._duplicates.items() if len(f_size) > 1}