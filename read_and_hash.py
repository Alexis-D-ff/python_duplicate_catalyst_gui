import hashlib
import os

def read_and_hash(file_path: str, single_segment_size: int=512,
                   hash_func=hashlib.sha1, first_segment=False):
    """
    This function reads one or multiple segments of a file and hashes them.
    It returns a single segment has for further comparison.
    Or yields a segment hash for potential duplicates.
    
    Attributes:
    -----------
    file_path: str
        path-like object, the full path of the file to be read.
    
    single_segment_size: int
        the size in bytes of a segment to be read fist. Files of the same size,
        having the same hash of this first segment are considered as potential duplicates.
        
    hash_func: object
        reference to the object of the hashing function.
        
    first_segment: bool
        when true, only the first segment of the file is read and hashed.
        
    Returns:
    -------
    hashed_object.digest()
        The digest of the first segment.
    
    Yields:
    ------
    hashed_object.update(segment)
        The updated with a next segment digest for the file.
    """
    
    hashed_object = hash_func()
    with open(file_path, "rb") as f:
        if first_segment:
            read_first_segment = f.read(single_segment_size)
            hashed_object.update(read_first_segment)
        else:
            full_file = f.read(os.path.getsize(file_path))
            hashed_object.update(full_file)
    
    return hashed_object.hexdigest()