import pydicom
from PIL import Image
import numpy as np

def read_dcm(path: str) -> np.ndarray:
    """
    Read a DICOM (.dcm) file and return the pixel array.
    """
    ds = pydicom.dcmread(path)
    arr = ds.pixel_array
    return arr


def convert_to_jpg(img_array: np.ndarray) -> Image.Image:
    """
    Convert a NumPy image array to a PIL JPEG image.
    """
    # Normalize and convert
    img = Image.fromarray((255 * (img_array - img_array.min()) / (img_array.ptp())).astype(np.uint8))