import os
from PIL import Image

def make_output_path(base: str, meta: dict, filename: str) -> str:
    """
    Build output directory structure: patient/study/view and ensure it exists.
    """
    out_dir = os.path.join(base, meta['patient_id'], meta['study_id'], meta['view_plane'])
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, filename)


def save_image(img: Image.Image, path: str):
    """
    Save a PIL Image to disk.
    """
    img.save(path)