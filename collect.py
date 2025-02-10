import os
import shutil

import HeicToJpg

paths = [line.strip() for line in open('ignore/paths.txt').readlines()]
input_partition = paths[12]
output_dir = paths[13]
sort_dir = paths[16]

def collect():
    #copy every file to the output directory
    for root, dirs, files in os.walk(input_partition):
        for file in files:
            full_path = os.path.join(root, file)
            shutil.copy(full_path, output_dir)
            print(f"Moved {full_path} to {output_dir}")
def convert(HeicOnly=True):
    if(HeicOnly):
        HeicToJpg.convert_heic_to_jpg(output_dir)
    HeicToJpg.universal_to_jpg(output_dir)

def sort():
    filetypes = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    for file in os.listdir(output_dir):
        if not (file.lower().endswith(filetypes)):
            shutil.move(os.path.join(output_dir, file), sort_dir)


collect()
#convert()
sort()
