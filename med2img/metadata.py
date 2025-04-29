import pydicom
import os

def extract_metadata(path: str) -> dict:
    """
    Extract metadata from a DICOM file.
    
    Args:
        path (str): Path to the DICOM file.
        
    Returns:
        dict: Dictionary containing metadata including patient ID, study ID, and view plane.
    """
    try:
        # Check if file exists and has a .dcm extension
        if not os.path.isfile(path) or not path.lower().endswith('.dcm'):
            raise ValueError(f"Invalid DICOM file path: {path}")
        
        # Read the DICOM file
        dicom_data = pydicom.dcmread(path)
        
        # Extract metadata
        metadata = {
            'patient_id': getattr(dicom_data, 'PatientID', 'Unknown'),
            'study_id': getattr(dicom_data, 'StudyID', 'Unknown'),
            'study_description': getattr(dicom_data, 'StudyDescription', 'Unknown'),
            'series_description': getattr(dicom_data, 'SeriesDescription', 'Unknown'),
            'modality': getattr(dicom_data, 'Modality', 'Unknown'),
            'institution_name': getattr(dicom_data, 'InstitutionName', 'Unknown'),
            'manufacturer': getattr(dicom_data, 'Manufacturer', 'Unknown'),
        }
        
        # Try to extract view plane information (often in ImageOrientationPatient)
        if 'ImageOrientationPatient' in dicom_data:
            orientation = dicom_data.ImageOrientationPatient
            # Determine plane based on orientation vectors
            if orientation:
                row_x, row_y, row_z, col_x, col_y, col_z = orientation
                
                # Calculate the normal vector to determine the plane
                normal_x = row_y * col_z - row_z * col_y
                normal_y = row_z * col_x - row_x * col_z
                normal_z = row_x * col_y - row_y * col_x
                
                # Determine the primary orientation
                max_component = max(abs(normal_x), abs(normal_y), abs(normal_z))
                
                if max_component == abs(normal_x):
                    metadata['view_plane'] = 'Sagittal'
                elif max_component == abs(normal_y):
                    metadata['view_plane'] = 'Coronal'
                elif max_component == abs(normal_z):
                    metadata['view_plane'] = 'Axial'
                else:
                    metadata['view_plane'] = 'Oblique'
            else:
                metadata['view_plane'] = 'Unknown'
        else:
            metadata['view_plane'] = 'Unknown'
        
        return metadata
    
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {'error': str(e)}