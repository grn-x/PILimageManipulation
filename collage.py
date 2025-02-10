"""
Collage maker - modified version with recursive directory scanning
Original by: Delimitry http://delimitry.blogspot.com/2014/07/picture-collage-maker-using-python.html
Modified to handle recursive directory scanning
"""

import os
from PIL import Image


def get_all_images(folder_path):
    """
    Recursively get all image files from folder_path and its subfolders
    """
    images = []
    # More comprehensive list of possible image extensions and variations
    extensions = (
        '.png', '.PNG',
        '.jpg', '.JPG', '.jpeg', '.JPEG',
        '.Jpg', '.Jpeg', '.JPeg'
    )
    valid_extensions = ('.png', '.jpg', '.jpeg')

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(valid_extensions):  # Removed .lower() to catch all variations
                full_path = os.path.join(root, file)
                images.append(full_path)
                print(f"Found image: {full_path}")

    print(f"Total images found: {len(images)}")
    return images

def make_collage(images, filename, width, init_height):
    """
    Make a collage image with a width equal to `width` from `images` and save to `filename`.
    """
    if not images:
        print('No images for collage found!')
        return False

    margin_size = 2
    # run until a suitable arrangement of images is found
    while True:
        # copy images to images_list
        images_list = images[:]
        coefs_lines = []
        images_line = []
        x = 0
        while images_list:
            # get first image and resize to `init_height`
            img_path = images_list.pop(0)
            img = Image.open(img_path)
            img.thumbnail((width, init_height))
            # when `x` will go beyond the `width`, start the next line
            if x > width:
                coefs_lines.append((float(x) / width, images_line))
                images_line = []
                x = 0
            x += img.size[0] + margin_size
            images_line.append(img_path)
        # finally add the last line with images
        coefs_lines.append((float(x) / width, images_line))

        # compact the lines, by reducing the `init_height`, if any with one or less images
        if len(coefs_lines) <= 1:
            break
        if any(map(lambda c: len(c[1]) <= 1, coefs_lines)):
            # reduce `init_height`
            init_height -= 10
        else:
            break

    # get output height
    out_height = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            out_height += int(init_height / coef) + margin_size
    if not out_height:
        print('Height of collage could not be 0!')
        return False

    collage_image = Image.new('RGB', (width, int(out_height)), (35, 35, 35))
    # put images to the collage
    y = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            x = 0
            for img_path in imgs_line:
                img = Image.open(img_path)
                # if need to enlarge an image - use `resize`, otherwise use `thumbnail`, it's faster
                k = (init_height / coef) / img.size[1]
                if k > 1:
                    img = img.resize((int(img.size[0] * k), int(img.size[1] * k)), Image.LANCZOS)
                else:
                    img.thumbnail((int(width / coef), int(init_height / coef)), Image.LANCZOS)
                if collage_image:
                    collage_image.paste(img, (int(x), int(y)))
                x += img.size[0] + margin_size
            y += int(init_height / coef) + margin_size
    collage_image.save(filename)
    return True

def create_collage_from_folder(input_folder, output_filename, width=7680, init_height=400, shuffle=False):
    """
    Create a high-resolution collage from all image files in input_folder and its subfolders
    Width is set to 8K (7680 pixels) by default
    Initial height is increased to 400 to better handle the larger canvas
    """
    # Set PIL's maximum image size limit higher to handle 8K
    Image.MAX_IMAGE_PIXELS = None  # Disable limit

    # Get all images from the folder and subfolders
    images = get_all_images(input_folder)
    if shuffle:
        import random
        random.shuffle(images)

    if not images:
        print(f"No images found in {input_folder} or its subfolders!")
        return False

    print(f"Found {len(images)} images")
    print(f"Creating {width}px wide collage...")
    result = make_collage(images, output_filename, width, init_height)

    if result:
        print(f"Collage saved as {output_filename}")
    else:
        print("Failed to create collage")

    return result


# Usage example:
if __name__ == '__main__':
    with open('ignore/paths.txt') as f:
        paths = [line.strip() for line in f.readlines()]
    input_folder = paths[6].strip()
    output_file = paths[7].strip()
    print(f"Creating 8K collage from images in {input_folder} and saving to {output_file}")
    create_collage_from_folder(input_folder, output_file, shuffle=True)  # Will create 8K width collage