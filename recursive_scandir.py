import os

def recursive_scandir(path: str):
        """
        This generator recursively scans a directory.
        
        Arguments:
        ---------
        path: str
            path-like object, the path of the directory to be scanned.
        
        Yields:
        ------
        Directory or file object from a given root directory.
        """
        try:
            for object in os.scandir(path):
                if object.is_dir(follow_symlinks=False):
                    yield object
                    yield from recursive_scandir(object.path)
                else:
                    yield object
        except PermissionError:
            pass