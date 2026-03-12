import os
import struct
from typing import Optional, List, Tuple

# DDS header constants
DDS_MAGIC = b'DDS '
DDS_HEADER_SIZE = 124

class DDSFormatError(Exception):
    pass

def is_dds_file(file_path: str) -> bool:
    """Check if the file at file_path is a valid DDS file."""
    try:
        with open(file_path, "rb") as f:
            magic = f.read(4)
            return magic == DDS_MAGIC
    except Exception:
        return False

def read_dds(file_path: str) -> bytes:
    """
    Reads a DDS file and returns its raw bytes.
    Raises DDSFormatError if the file is not a valid DDS file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DDS file not found: {file_path}")
    with open(file_path, "rb") as f:
        magic = f.read(4)
        if magic != DDS_MAGIC:
            raise DDSFormatError("File is not a valid DDS file (missing DDS magic).")
        data = magic + f.read()
    return data

def write_dds(file_path: str, dds_data: bytes):
    """
    Writes raw DDS bytes to file_path.
    Validates the DDS header before writing.
    """
    if not dds_data.startswith(DDS_MAGIC):
        raise DDSFormatError("DDS data does not start with DDS magic.")
    with open(file_path, "wb") as f:
        f.write(dds_data)

def get_dds_info(dds_data: bytes) -> Optional[dict]:
    """
    Extracts basic info from DDS header.
    Returns a dict with width, height, mipmap count, and pixel format.
    """
    if not dds_data.startswith(DDS_MAGIC):
        return None
    if len(dds_data) < 4 + DDS_HEADER_SIZE:
        return None
    header = dds_data[4:4 + DDS_HEADER_SIZE]
    # DDS header structure: https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    # struct DDS_HEADER {
    #   DWORD dwSize;
    #   DWORD dwFlags;
    #   DWORD dwHeight;
    #   DWORD dwWidth;
    #   DWORD dwPitchOrLinearSize;
    #   DWORD dwDepth;
    #   DWORD dwMipMapCount;
    #   DWORD dwReserved1[11];
    #   DDS_PIXELFORMAT ddspf;
    #   DWORD dwCaps;
    #   DWORD dwCaps2;
    #   DWORD dwCaps3;
    #   DWORD dwCaps4;
    #   DWORD dwReserved2;
    # }
    try:
        dwSize, dwFlags, dwHeight, dwWidth, dwPitchOrLinearSize, dwDepth, dwMipMapCount = struct.unpack("<7I", header[:28])
        # Pixel format is at offset 76, 32 bytes
        ddspf = header[76:76+32]
        pf_size, pf_flags, pf_fourcc = struct.unpack("<I I 4s", ddspf[:12])
        info = {
            "width": dwWidth,
            "height": dwHeight,
            "mipmap_count": dwMipMapCount,
            "pixel_format": pf_fourcc.decode(errors="ignore")
        }
        return info
    except Exception:
        return None

def validate_dds(dds_data: bytes) -> bool:
    """
    Validates DDS data for basic header correctness.
    """
    info = get_dds_info(dds_data)
    return info is not None

def extract_dds_textures(dds_paths: List[str]) -> List[bytes]:
    """
    Reads multiple DDS files and returns a list of their raw bytes.
    """
    textures = []
    for path in dds_paths:
        textures.append(read_dds(path))
    return textures

def save_dds_textures(dds_datas: List[bytes], dds_paths: List[str]):
    """
    Saves multiple DDS byte arrays to the specified file paths.
    """
    if len(dds_datas) != len(dds_paths):
        raise ValueError("dds_datas and dds_paths must have the same length.")
    for data, path in zip(dds_datas, dds_paths):
        write_dds(path, data)