import os
import logging

logging.basicConfig(filename='logfile.txt',
                    filemode='a',
                    format='%(asctime)s, %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y - %H:%M:%S',
                    level=logging.DEBUG)

def recursive_scandir(path: str, recursion_limit: int=2, current_recurs_step: int=1):
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
        #if current_recurs_step < 2:
        try:
            sorted_scandir = sorted(os.scandir(path), key = lambda obj:(obj.is_file(), obj.name.casefold()))
            
            for object in sorted_scandir:
                if object.is_dir(follow_symlinks=False):
                    yield object
                    current_recurs_step += 1
                    if current_recurs_step <= recursion_limit:
                        
                        iterator = os.scandir(object.path)
                        try: 
                            elem = next(iterator)
                            print(elem)
                            yield elem
                        except:
                            pass
                        
                        #yield from recursive_scandir(object.path, current_recurs_step=current_recurs_step)
                        current_recurs_step = 1
                else:
                    yield object
                    
        except PermissionError as message:
            logging.debug(message)
            pass
        
        # else:
        #     iterator = os.scandir(path)
        #     try: 
        #         elem = next(iterator)
        #         print(elem)
        #         yield elem
        #     except:
        #         pass
            
            