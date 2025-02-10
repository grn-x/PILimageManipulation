import os
from PIL import Image
from pillow_heif import register_heif_opener
import shutil

register_heif_opener()

with open('ignore/paths.txt') as f:
    paths = [line.strip() for line in f.readlines()]

input_dir = paths[11]

for file in os.listdir(input_dir):
    if file.endswith('.HEIC'):
        file_path = os.path.join(input_dir, file)

        image = Image.open(file_path)

        output_file_path = os.path.join(input_dir, f'{os.path.splitext(file)[0]}.jpg')
        print(output_file_path)
        print(file_path)
        image.save(output_file_path, "JPEG")

        os.remove(file_path)
