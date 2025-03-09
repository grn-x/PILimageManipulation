# Image Processing Scripts

This repository contains various scripts for processing images, creating collages, converting image formats, and generating images with text.

Specifically these were used to render image compilations from past school projects to then be shown in a presentation slideshow video whatever.

<details>
<summary>The scripts were created to be used in an environment like this: </summary>
 

```plaintext
├───21_22
│   ├───Projectname_12
│   │       forename1 surname1.jpg
│   │       forename2 surname2.jpg
│   │       forename3 surname3.jpg
│   │       forename4 surname4.jpg
│   │
│   ├───Projectname_6
│   │       forename1 surname1.jpg
│   │       forename2 surname2.jpg
│   │       forename3 surname3.jpg
│   │
│   └───Projectname_9
│           forename1 surname1.jpg
│
├───22_23
│   ├───Projectname_11
│   │       forename1 surname1.jpg
│   │       forename2 surname2.jpg
│   │
│   ├───Projectname_7
│   │       forename1 surname1.jpg
│   │       forename2 surname2.jpg
│   │       forename3 surname3.jpg
│   │       forename4 surname4.jpg
│   │       forename5 surname5.jpg
│   │
│   ├───Projectname_8
│   │       forename1 surname1.jpg
│   │       forename2 surname2.jpg
│   │
│   └───Projectname_10
│           forename1 surname1.jpg
│           forename2 surname2.jpg
│           forename3 surname3.jpg
│           forename4 surname4.jpg
│           forename5 surname5.jpg
│           forename6 surname6.jpg
│
└───23_24
    ├───Projectname_9
    │       forename1 surname1.jpg
    │
    ├───Projectname_7
    │       forename1 surname1.jpg
    │       forename2 surname2.jpg
    │       forename3 surname3.jpg
    │       forename4 surname4.jpg
    │       forename5 surname5.jpg
    │
    └───Projectname_10
            forename1 surname1.jpg
            forename2 surname2.jpg
```

</details>

## `CanvasV9.py`
This script creates a canvas with multiple images and captions, arranging them in a custom layouts depending on the number of images, and flags set.

### Functions:
- **`get_unique_filename(output_dir, filename)`**  
  Generates a unique filename by appending a number to the name if it already exists in the output directory.
- **`create_radial_gradient(width, height, center_color, edge_color)`**  
  Creates a radial gradient from the center color to the edge color.
- **`create_canvas_with_gradient(width, height, center_color, edge_color)`**  
  Creates a canvas with a radial gradient background.
- **`adjust_text(text, font, available_width, draw)`**  
  Remove or replace hard-coded blacklisted words from the text.
- **`add_spaces_to_project_name(project)`**  
  Adds spaces to PascalCase project names.
- **`create_canvas(images, captions, output_path, project, class_level, year)`**  
  Creates a canvas with multiple images and captions.
  - **`create_canvas_x`**  
    Group of child functions emerged from the original `create_canvas` function, to handle cases of 1, 2, 3 (with the root function 4) images.

### Flags:
- `center_images`: Is responsible for either strictly centering the pictures in the middle of their quadrant,
or take their aspect ratios into account and ensure a more organic and visually pleasing layout (default: **False**).


- `custom_order`: Decides, if, in cases where less than 4 images are passed, the default 2x2 layout should be used,
which consequently results in ugly empty cells. If set to `True`, the layout will be adjusted to fit the number of images,
the `create_canvas` function will then delegate to the appropriate `create_canvas_x` function (default: **True**).


- `maintain_size`: A flag to specify whether to enforce a maximum picture size comparable to a cell/quadrant in the default
2x2 layout or allow the pictures to fill the whole canvas (default: **True**).
> [!IMPORTANT]  
> The `maintain_size` flag is only relevant when `custom_order` is set to `True` **AND** less than 3 images are passed.
> In which case the bottom row of the 2x2 layout would not be filled, and `create_canvas` would delegate to `create_canvas_one` or `create_canvas_two`.

- `debug`: Boolean flag to add geometric lines for debugging (default: **False**).

---

## `winners.py`
This script outputs images, each with a single picture and caption below it.
Because we deal with only one picture per created image, the centering is much easier, hence this is simply a simplified
version of `CanvasV9.py`.


### Functions:
- **`create_radial_gradient(width, height, center_color, edge_color)`**  
  Creates a radial gradient from the center color to the edge color.
- **`create_canvas_with_gradient(width, height, center_color, edge_color)`**  
  Creates a canvas with a radial gradient background.
- **`create_image(images, output_path, class_level, year, name, project)`**  
  Creates an image with the specified details and saves it to the specified output path.

---

## `Text.py`
This script outputs an image with text on a radial gradient background.  

### Functions:
- **`create_radial_gradient(width, height, center_color, edge_color)`**  
  Creates a radial gradient from the center color to the edge color.
- **`create_canvas_with_gradient(width, height, center_color, edge_color)`**  
  Creates a canvas with a radial gradient background.
- **`create_text_image(text, output_path, width, height, font_path, font_size, highlight_word)`**  
  Creates an image with the specified text, highlighting a specific word if provided, and saves it to the specified output path.

---

## `collage.py`
This script creates a collage from images in a specified folder and its subfolders. It supports various image formats, including `.png`, `.jpg`, `.jpeg`, `.heic`, and `.webp`.  

### Functions:
- **`get_all_images(folder_path)`**  
  Recursively retrieves all image files from the specified folder and its subfolders.
- **`make_collage(images, filename, width, init_height)`**  
  Creates a collage image with the specified width and initial height from the list of images and saves it to the specified filename.
- **`create_collage_from_folder(input_folder, output_filename, width=7680, init_height=400, shuffle=False)`**  
  Creates a high-resolution collage from all image files in the input folder and its subfolders. The width is set to 8K (7680 pixels) by default.

### Flags:
- `width`: Width of the collage (default: **7680 pixels**).
- `init_height`: Initial height of the images in the collage (default: **400 pixels**).
- `shuffle`: Boolean flag to shuffle the images before creating the collage (default: **False**).


<br>
<br>

---

# Additional non-image-processing, helper scripts

---

---

## `HeicToJpg.py`
This script converts `.heic` files to `.jpg` format using the Pillow library.  

### Functions:
- **`convert_heic_to_jpg(input_dir)`**  
  Converts all `.heic` files in the specified directory to `.jpg`.
- **`universal_to_jpg(input_dir)`**  
  Converts all image files in the specified directory to `.jpg`.
- 
---

## `collect.py`
This script contains three independent functions to collect, convert, and sort images in a specified directory.

### Functions:
- **`collect()`**  
  Copies every file from the input partition to the output directory.
- **`convert(HeicOnly=True)`**  
  Converts `.heic` files to `.jpg` in the output directory. If `HeicOnly` is `False`, it converts all image files to `.jpg`.
> [!NOTE]
> Internally, the above `HeicToJpg.py` script is used to convert `.heic` files to `.jpg`.
- **`sort()`**  
  Moves non-image files from the output directory to a separate sorting directory.

### Flags:
- `HeicOnly`: Boolean flag to specify whether only `.heic` files should be converted (default: **True**).





