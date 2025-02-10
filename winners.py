import os
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = 933120000 # needed for 4k

with open('ignore/paths.txt') as f:
    paths = [line.strip() for line in f.readlines()]


input_dir = paths[8]
output_dir = paths[9]
padding = 60
border_padding = 180
caption_padding = 40
font_path = paths[10] # Path to a .ttf font file
font_size = 80
center_images = False  # whether the images should be truly centered or rather kind of centered and proportionally aligned
custom_order = True  # whether the resulting canvas ordering should be done differently from the strict 4 image layout / 2x2 grid


debug = False  # Add geometric lines to show where calculations are made, useful for debugging the cells, quadrants, alignment etc.

canvas_height = 2160
canvas_width = 3840

num_files_saved = 0


def create_radial_gradient(width, height, center_color, edge_color):
    """
    Creates a radial gradient from center_color to edge_color.

    Args:
        width (int): Width of the image
        height (int): Height of the image
        center_color (tuple): RGB color for the center (e.g., (200, 200, 200))
        edge_color (tuple): RGB color for the edges (e.g., (150, 150, 150))

    Returns:
        PIL.Image: Image with radial gradient
    """
    # Create an image with alpha channel for smooth blending
    image = Image.new('RGBA', (width, height))

    # Get center point
    center_x = width // 2
    center_y = height // 2

    # Calculate the maximum distance from center to corner
    #max_distance = math.sqrt((center_x) ** 2 + (center_y) ** 2)
    max_distance = (center_x ** 2 + center_y ** 2)**0.5

    # Create pixel array
    pixels = image.load()

    # Generate gradient
    for y in range(height):
        for x in range(width):
            # Calculate distance from center
            #distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2)**0.5

            # Convert to ratio (0 to 1)
            ratio = min(distance / max_distance, 1.0)

            # Create gradient color
            r = int(center_color[0] * (1 - ratio) + edge_color[0] * ratio)
            g = int(center_color[1] * (1 - ratio) + edge_color[1] * ratio)
            b = int(center_color[2] * (1 - ratio) + edge_color[2] * ratio)

            pixels[x, y] = (r, g, b, 255)

    return image


def create_canvas_with_gradient(width=canvas_width, height=canvas_height, center_color=(200, 200, 200), edge_color=(75, 75, 75)):
    """
    Creates a canvas with a radial gradient background. Wraps the create_radial_gradient function for convenience and quick changes.

    Args:
        width (int): Canvas width
        height (int): Canvas height
        center_color (tuple): RGB color for the center (default: light gray)
        edge_color (tuple): RGB color for the edges (default: darker gray)

    Returns:
        tuple: (PIL.Image, PIL.ImageDraw) - The canvas and its draw object
    """

    #canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    #draw = ImageDraw.Draw(canvas)


    # Create the gradient background
    canvas = create_radial_gradient(width, height, center_color, edge_color)

    # Convert to RGB mode for compatibility with other operations
    canvas = canvas.convert('RGB')

    # Create draw object
    draw = ImageDraw.Draw(canvas)

    return canvas, draw



#dateinamen mit leerzeichen kommen mir nicht ins haus // reinsert spaces into pascal case text
def add_spaces_to_project_name(project):
    return ''.join([' ' + char if char.isupper() and ((i == 0 or not project[i - 1].isspace())and (i - 1)>=0) else char for i, char in
                    enumerate(project)])


def create_image(images, output_path, class_level ,year, name, project= 'Europa Wettbewerb Gewinner'):
    image = images
    caption = (f'{name}, {class_level} gewinnt beim 71. Europa Wettbewerb')



    cell_height = canvas_height - 2 * border_padding - 2 * padding - font_size - caption_padding
    cell_width = canvas_width - 2 * border_padding - 2 * padding

    #canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    #draw = ImageDraw.Draw(canvas)
    canvas, draw = create_canvas_with_gradient(width=canvas_width, height=canvas_height)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        print(f"Error: Cannot open font resource at {font_path}")
        return

    # Calculate the reference frame for the image
    image_ratio = image.width / image.height
    frame_ratio = cell_width / cell_height

    if image_ratio > frame_ratio:
        new_width = cell_width
        new_height = int(new_width / image_ratio)
    else:
        new_height = cell_height
        new_width = int(new_height * image_ratio)

    # Center the image within the canvas
    image = image.resize((new_width, new_height), Image.LANCZOS)
    image_x = (canvas_width - new_width) // 2
    image_y = (canvas_height - new_height) // 2
    canvas.paste(image, (image_x, image_y))

    # Add caption directly below the image
    try:
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = image_x + (new_width - text_width) // 2
        text_y = image_y + new_height + caption_padding
        draw.text((text_x, text_y), caption, fill="black", font=font)
    except TypeError as e:
        print(f"Error processing caption: {caption}, type: {type(caption)}")
        print(f"Error details: {e}")
        # Use a default caption if there's an error
        caption = "Untitled"
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = image_x + (new_width - text_width) // 2
        text_y = image_y + new_height + caption_padding
        draw.text((text_x, text_y), caption, fill="black", font=font)

    # Draw the original cell bounds in blue if debug is True
    if debug:
        draw.rectangle([(border_padding, border_padding),
                        (canvas_width - border_padding, canvas_height - border_padding)],
                       outline="blue", width=2)

    # Draw the reference frame in red if debug is True
    if debug:
        draw.rectangle([image_x, image_y, image_x + new_width, image_y + new_height], outline="red", width=2)


    canvas.save(output_path)


for file in os.listdir(input_dir):
    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        print(f"Processing file: {file}")
        image = Image.open(os.path.join(input_dir, file))


        root=file.replace('.jpg','').replace('.png','').replace('.jpeg','').replace('.bmp','').replace('.gif','').replace('.JPG','')
        class_level = root.split('_')[0]
        forename = root.split('_')[2]
        surname = root.split('_')[1]

        output_filename = f'{class_level}_{forename}_{surname}.jpg'
        output_path = os.path.join(output_dir, output_filename)
        year = '23/24'
        create_image(image, year=year, name =f'{forename} {surname}' , output_path=output_path, class_level=class_level)
        num_files_saved += 1

print(f"Processed {num_files_saved} images")