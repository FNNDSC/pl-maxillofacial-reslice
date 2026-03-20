"""
Developed by Arman Avesta, MD, PhD
FNNDSC | Boston Children's Hospital | Harvard Medical School
"""

# ----------------------------------------------- ENVIRONMENT SETUP ---------------------------------------------------
# Project imports:


# System imports:
import copy
from pathlib import Path
from shutil import rmtree
import numpy as np
import pydicom
from pydicom.uid import generate_uid

# ---------------------------------------------- HELPER FUNCTIONS -----------------------------------------------------

def load_dicoms(dicoms_dir):

    paths = sorted(Path(dicoms_dir).glob("*.dcm"))
    datasets = [pydicom.dcmread(p) for p in paths]
    try:
        datasets = sorted(datasets, key=lambda d: int(d.InstanceNumber))
    except Exception:
        pass

    return datasets


def save_dicoms(stack, template, dicoms_dir, pixel_spacing, slice_spacing, orientation):

    series_uid = generate_uid()
    origin = np.array(getattr(template, "ImagePositionPatient", [0.0, 0.0, 0.0]), dtype=float)
    row = np.array(orientation[0:3], dtype=float)
    col = np.array(orientation[3:6], dtype=float)
    normal = np.cross(row, col)

    for idx, slice_data in enumerate(stack, start=1):
        ds = copy.deepcopy(template)
        ds.Rows, ds.Columns = slice_data.shape
        ds.PixelSpacing = [float(pixel_spacing[0]), float(pixel_spacing[1])]
        ds.SpacingBetweenSlices = float(slice_spacing)
        ds.InstanceNumber = idx
        ds.SeriesInstanceUID = series_uid
        ds.SOPInstanceUID = generate_uid()

        if hasattr(ds, "file_meta"):
            ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

        ds.ImageOrientationPatient = list(orientation)
        ds.ImagePositionPatient = list(origin + normal * float((idx - 1) * slice_spacing))
        ds.PixelData = np.asarray(slice_data, dtype=template.pixel_array.dtype).tobytes()
        
        ds.save_as(dicoms_dir / f"{dicoms_dir.name}_{idx:04d}.dcm", write_like_original=False)

# ----------------------------------------------- MAIN FUNCTIONS ------------------------------------------------------

def axial_reslice(axial_dicoms_dir, coronal_dicoms_dir, sagittal_dicoms_dir):

    datasets = load_dicoms(axial_dicoms_dir)
    if not datasets:
        return

    first = datasets[0]
    spacing_y, spacing_x = [float(x) for x in first.PixelSpacing]
    spacing_z = float(getattr(first, "SpacingBetweenSlices", getattr(first, "SliceThickness", 1.0)))

    stack = np.stack([ds.pixel_array for ds in datasets], axis=0)  # (z, y, x)

    coronal = np.transpose(stack, (1, 0, 2))   # (y, z, x) -> rows=z, cols=x, step=y
    sagittal = np.transpose(stack, (2, 0, 1))  # (x, z, y) -> rows=z, cols=y, step=x

    # Delete coronal and sagittal folders if they exist
    if coronal_dicoms_dir.exists():
        rmtree(coronal_dicoms_dir)
    if sagittal_dicoms_dir.exists():
        rmtree(sagittal_dicoms_dir)

    # Create coronal and sagittal folders
    coronal_dicoms_dir.mkdir()
    sagittal_dicoms_dir.mkdir()

    save_dicoms(
        stack=coronal,
        template=first,
        dicoms_dir=coronal_dicoms_dir,
        pixel_spacing=(spacing_z, spacing_x),
        slice_spacing=spacing_y,
        orientation=(0, 0, 1, 1, 0, 0),
    )
    save_dicoms(
        stack=sagittal,
        template=first,
        dicoms_dir=sagittal_dicoms_dir,
        pixel_spacing=(spacing_z, spacing_y),
        slice_spacing=spacing_x,
        orientation=(0, 0, 1, 0, 1, 0),
    )

# ----------------------------------------------- CODE TESTING --------------------------------------------------------

if __name__ == "__main__":

    axial_dicoms_dir = Path('/Users/arman/projects/pl-maxillofacial-reslice/images/axial')
    coronal_dicoms_dir = Path('/Users/arman/projects/pl-maxillofacial-reslice/images/coronal')
    sagittal_dicoms_dir = Path('/Users/arman/projects/pl-maxillofacial-reslice/images/sagittal')

    axial_reslice(axial_dicoms_dir, coronal_dicoms_dir, sagittal_dicoms_dir)

    # pixel_keywords = [
    #     "Rows", "Columns", "NumberOfFrames",
    #     "PixelSpacing", "SliceThickness", "SpacingBetweenSlices",
    #     "ImagePositionPatient", "ImageOrientationPatient",
    #     "SamplesPerPixel", "PhotometricInterpretation",
    #     "BitsAllocated", "BitsStored", "HighBit", "PixelRepresentation",
    #     "RescaleSlope", "RescaleIntercept",
    #     "WindowCenter", "WindowWidth",
    # ]
    #
    # for kw in pixel_keywords:
    #     if kw in ds:
    #         print(f"{kw}: {getattr(ds, kw)}")


