"""
Compression utility functions for GitEllE.
"""
import zlib
from typing import Union


def compress_data(data: Union[bytes, str]) -> bytes:
    """
    Compress data using zlib.

    Args:
        data: The data to compress

    Returns:
        The compressed data
    """
    if isinstance(data, str):
        data = data.encode()

    return zlib.compress(data)


def decompress_data(data: bytes) -> bytes:
    """
    Decompress data using zlib.

    Args:
        data: The compressed data

    Returns:
        The decompressed data
    """
    return zlib.decompress(data)
