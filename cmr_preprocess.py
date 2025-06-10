import os
import pydicom
from collections import defaultdict
from pprint import pprint

# --- Define classification rules ---
def classify_view(description: str) -> str:
    desc = description.upper()
    if 'SAX' in desc or 'SHORTAXIS' in desc:
        return 'SA'
    elif '2CH' in desc:
        return 'LA_2CH'
    elif '3CH' in desc:
        return 'LA_3CH'
    elif '4CH' in desc:
        return 'LA_4CH'
    elif 'LONGAXIS' in desc or 'LAX' in desc:
        return 'LA_OTHER'
    else:
        return 'OTHER'

# --- Parse one series ---
def parse_series(series_path):
    data = []
    for f in os.listdir(series_path):
        if f.lower().endswith('.dcm'):
            try:
                dcm = pydicom.dcmread(os.path.join(series_path, f), stop_before_pixels=True)
                data.append(dcm)
            except:
                continue
    if not data:
        return None

    first = data[0]
    series_info = {
        "SeriesDescription": getattr(first, "SeriesDescription", "Unknown"),
        "SeriesInstanceUID": getattr(first, "SeriesInstanceUID", os.path.basename(series_path)),
        "ViewType": classify_view(getattr(first, "SeriesDescription", "")),
        "Modality": first.Modality,
        "NumFrames": len(set(getattr(dcm, "InstanceNumber", i) for i, dcm in enumerate(data))),
        "SlicePositions": sorted(set(
            tuple(getattr(dcm, "ImagePositionPatient", [0, 0, i]))[2]
            for i, dcm in enumerate(data)
            if hasattr(dcm, "ImagePositionPatient")
        )),
        "Resolution": (getattr(first, "Rows", None), getattr(first, "Columns", None))
    }
    series_info["NumSlices"] = len(series_info["SlicePositions"])
    return series_info

# --- Traverse all series in a patient/study directory ---
def summarize_study(study_path):
    summary = []
    for subfolder in os.listdir(study_path):
        full_path = os.path.join(study_path, subfolder)
        if os.path.isdir(full_path):
            info = parse_series(full_path)
            if info:
                summary.append(info)
    return summary

# --- Group and summarize overall stats ---
def summarize_by_type(series_list):
    counts = defaultdict(list)
    for s in series_list:
        counts[s['ViewType']].append(s)

    summary = {}
    for view_type, series in counts.items():
        summary[view_type] = {
            "NumSeries": len(series),
            "TotalFrames": sum(s["NumFrames"] for s in series),
            "TotalSlices": sum(s["NumSlices"] for s in series),
            "Resolutions": list(set(s["Resolution"] for s in series)),
            "SeriesDescriptions": [s["SeriesDescription"] for s in series]
        }
    return summary

# --- Main ---
if __name__ == "__main__":
    root_dir = "/path/to/extracted/study"  # <- UPDATE THIS PATH
    series_data = summarize_study(root_dir)
    summary = summarize_by_type(series_data)

    print(f"\n--- Study Summary for: {root_dir} ---\n")
    pprint(summary)





import os, pydicom
from PIL import Image
import numpy as np

root_dir = "/path/to/extracted/study"  # ← update this

target_series = [
    'SAX-st FGRE CINE BH',
    '2CH FGRE CINE BH',
    '3CH FGRE CINE BH',
    '4CH FGRE CINE BH'
]

def find_target_series_folders(root_dir):
    results = []
    for sub in os.listdir(root_dir):
        path = os.path.join(root_dir, sub)
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith(".dcm"):
                    try:
                        dcm = pydicom.dcmread(os.path.join(path, f), stop_before_pixels=True)
                        desc = getattr(dcm, "SeriesDescription", "").strip()
                        if desc in target_series:
                            results.append((desc, path))
                        break
                    except: continue
    return results

series_list = find_target_series_folders(root_dir)
out_root = os.path.expanduser("~/cmr_samples")
os.makedirs(out_root, exist_ok=True)

for desc, path in series_list:
    desc_safe = desc.replace(" ", "_").replace(":", "_")
    out_series = os.path.join(out_root, desc_safe)
    os.makedirs(out_series, exist_ok=True)
    dicoms = []
    for f in os.listdir(path):
        if f.lower().endswith(".dcm"):
            try:
                dicoms.append(pydicom.dcmread(os.path.join(path, f)))
            except: continue
    def get_z(d): return round(d.ImagePositionPatient[2], 3) if "ImagePositionPatient" in d else 0
    def get_t(d): return getattr(d, "InstanceNumber", 0)
    grouped = {}
    for d in dicoms:
        z = get_z(d)
        grouped.setdefault(z, []).append(d)
    for i, (z, frames) in enumerate(sorted(grouped.items())):
        frames.sort(key=get_t)
        slice_dir = os.path.join(out_series, f"slice_{i:02d}")
        os.makedirs(slice_dir, exist_ok=True)
        for t, dcm in enumerate(frames):
            img = dcm.pixel_array.astype(np.float32)
            img -= img.min(); img /= img.max(); img *= 255
            Image.fromarray(img.astype(np.uint8)).convert("L").save(os.path.join(slice_dir, f"frame_{t:02d}.jpg"))
    print(f"Saved {sum(len(v) for v in grouped.values())} frames in {desc}")
