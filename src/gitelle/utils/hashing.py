"""
Hashing utility functions for GitEllE.
"""
import hashlib
from typing import Union


def sha1_hash(data: Union[bytes, str]) -> str:
    """
    Calculate the SHA-1 hash of data.

    Args:
        data: The data to hash

    Returns:
        The SHA-1 hash as a hexadecimal string
    """
    if isinstance(data, str):
        data = data.encode()

    return hashlib.sha1(data).hexdigest()


def sha1_hash_file(file_path: str) -> str:
    """
    Calculate the SHA-1 hash of a file.

    Args:
        file_path: The path to the file

    Returns:
        The SHA-1 hash as a hexadecimal string
    """
    sha1 = hashlib.sha1()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in 64k chunks
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()
