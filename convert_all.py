# convert_all code from previous attempt

import os
import shutil
from pathlib import Path
import sys

import dicom2jpg

tgz_dir = '/source/transfer_correct/'
temp_dir = '/local-scratch/dest/CMR/temp_store/'
target_dir = '/local-scratch/dest/CMR/CMR_jpg/'

failed_files = []

ii = 0
for tgz_file in os.listdir(tgz_dir):
        if ii>=6000:
                shutil.copyfile(Path(tgz_dir)/Path(tgz_file), Path('/local-scratch/masadi/CMR/tgz_files')/Path(tgz_file))
                print(f"{tgz_file} copied.")
                os.system(f"tar -xzf /local-scratch/dest/CMR/tgz_files/{tgz_file} -C {temp_dir}")
                print(f"{tgz_file} extracted.")
                try:
                        dicom2jpg.dicom2jpg(Path(temp_dir)/Path(os.listdir(temp_dir)[0]), target_root = target_dir)
                        print(f"{tgz_file} converted to jpg.")
                except:
                        print(f"{tgz_file} failed in jpg stage....")
                        failed_files.append(tgz_file)
                os.system(f"rm -rf /local-scratch/dest/CMR/tgz_files/{tgz_file}")
                os.system(f"rm -rf {temp_dir}*")
                print(f"{tgz_file} remains removed.")
                print(f"{ii+1}-th file done...")
        ii += 1
        
print("Failed cases:")
print(failed_files)
