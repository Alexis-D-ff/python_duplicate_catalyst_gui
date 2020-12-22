import os
import logging
import yaml

def recursive_scandir(path: str, config_file_path: str, recursion_limit: int=2, current_recurs_step: int=1):
        """
        This generator recursively scans a directory for files and nested directories.
        
        Arguments:
        ---------
        path: str
            path-like object, the path of the root directory to be scanned.
        
        recursion_limit: int, int=2
            the depth of recursion for nested directories. This limit is used for visualization,
            by default only 2nd nested directory is scanned.
            value equal to 0 can be used to turn off the recursion_limit.
        
        current_recurs_step: int=1
            counter of recursion deepness used to cut off the scanning of deeper directories.
            
        config_file_path: str
            path-object containing the path to the configuration yaml file.
        Yields:
        ------
        object: object type
            fetched directory or file object from a given root directory.
            
        next(first_object): object type
            the first fetched object inside a nested directory. This allows visualizing the parent directory as a container
            in tkinter.treeview.
        """
        with open(config_file_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        # Handle empty folders or denied access with try-except statement
        # The dir_availability switch is used to simplify the code, as further another try-except is applied for child objects
        try:
            # For a correct visualization, all the necessary objects (directories and files)
            # should be grouped by: 1. Type (directories-> files); 2. Name (A-Z)  
            sorted_scandir = sorted(os.scandir(path), key = lambda obj:(obj.is_file(), obj.name.casefold()))
            dir_availability = True
            
        except PermissionError as permission_err:
            logging.basicConfig(**config['logger'])
            logging.error(permission_err)
            dir_availability = False
            pass
            
        if dir_availability:
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