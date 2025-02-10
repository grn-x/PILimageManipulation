import os
from PIL import Image
from pillow_heif import register_heif_opener
import shutil

register_heif_opener()

def convert_heic_to_jpg(input_dir):
    for file in os.listdir(input_dir):
        if file.endswith('.HEIC'):
            file_path = os.path.join(input_dir, file)

            image = Image.open(file_path)

            output_file_path = os.path.join(input_dir, f'{os.path.splitext(file)[0]}.jpg')
            print(output_file_path)
            print(file_path)
            image.save(output_file_path, "JPEG")

            os.remove(file_path)


def universal_to_jpg(input_dir):
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)

        try:
            image = Image.open(file_path)
            output_file_path = os.path.join(input_dir, f'{os.path.splitext(file)[0]}.jpg')
            print(output_file_path)
            print(file_path)
            image.save(output_file_path, "JPEG")
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")


if __name__ == '__main__':
    with open('ignore/paths.txt') as f:
        paths = [line.strip() for line in f.readlines()]

    input_dir = paths[11]
    convert_heic_to_jpg(input_dir)