import os
from concurrent.futures import ProcessPoolExecutor
from .converters import read_dcm, convert_to_jpg
from .metadata import extract_metadata
from .io import make_output_path, save_image


def process_file(path: str, out_base: str, fmt: str = 'jpg'):
    meta = extract_metadata(path)
    arr = read_dcm(path)
    img = convert_to_jpg(arr)
    filename = os.path.splitext(os.path.basename(path))[0] + f'.{fmt}' # TODO: Use frame number (from metadata) instead of original filename.
    out_path = make_output_path(out_base, meta, filename)
    save_image(img, out_path)


def process_directory(in_dir: str, out_base: str, fmt: str = 'jpg', max_workers: int = 1):
    """
    Walks `in_dir` tree, finds .dcm files, and converts them in parallel.
    """
    tasks = []
    for root, _, files in os.walk(in_dir):
        for f in files:
            if f.lower().endswith('.dcm'):
                tasks.append(os.path.join(root, f))

    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        futures = [exe.submit(process_file, p, out_base, fmt) for p in tasks]
        for f in futures:
            f.result()  # propagate exceptions