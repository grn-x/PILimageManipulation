import os
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = 933120000 # needed for 4k

with open('ignore/paths.txt') as f:
    paths = [line.strip() for line in f.readlines()]


input_dir = paths[18] #15
output_dir = paths[19]
padding = 20
border_padding = 90
caption_padding = 20
font_path = paths[2] # Path to a .ttf font file
font_size = 40
font_size_info = 60
center_images = False  # whether the images should be truly centered or rather kind of centered and proportionally aligned
custom_order = True  # whether the resulting canvas ordering should be done differently from the strict 4 image layout / 2x2 grid


maintain_size = True  # only of importance for pages with less than 3 images,
# decides whether to take the whole canvas, or stay at a quarter

debug = True  # Add geometric lines to show where calculations are made, useful for debugging the cells, quadrants, alignment etc.

ignore_folders = paths[3:6] #why is the end index non inclusive?

canvas_height = 2160
canvas_width = 3840

num_files_saved = 0


def get_unique_filename(output_dir, filename):
    print(f"Checking for unique filename for {filename}")
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(output_dir, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        print(f"Filename already exists, trying {new_filename} counter: {counter}")
        counter += 1

    return new_filename

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


def create_canvas_with_gradient(width=canvas_width, height=canvas_height, center_color=(200, 200, 200), edge_color=(60, 60, 60)):#edge_color=(75, 75, 75)):
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


def adjust_text_right_dpr(text, font, available_width, draw):
    #available_width = math.floor(available_width) # todo floor division instead in calling function instead //
    available_width = available_width//1
    lines = text.split('\n')
    adjusted_lines = []

    for line in lines:
        while draw.textbbox((0, 0), line, font=font)[2] > available_width:
            if len(line) <= available_width:
                break
            for i in range(min(available_width, len(line)), 0, -1):
                if line[i] == ' ':
                    adjusted_lines.append(line[:i])
                    line = line[i + 1:]
                    break
            else:
                adjusted_lines.append(line[:available_width - 2] + '-')
                line = line[available_width - 2:]
        adjusted_lines.append(line)

    return '\n'.join(adjusted_lines)

#quick and dirty fix to replace keywords and patch up naming errors
def adjust_text(text, font = None, available_width= 0, draw = None):
    initial_text = text
    # Hardcoding replacements
    text = text.replace(' Landschaften ', '\nLandschaften')
    text = text.replace('Phantastische ', 'Phantastische \n')
    #text = text.replace('Alles Fuer ', 'Alles Für \n')
    text = text.replace('Alles Fuer ', 'Alles Für ')
    text = text.replace('Minimal', 'Minimal Leben')
    #text = text.replace('Gesunde ', 'Gesunde \n')
    text = text.replace('Höhlenmalerei Misch=??', 'Gesunde \n')
    text = text.replace('Reise Durch Europa ', 'Reise Durch Europa\n')
    text = text.replace(' Bildmontage', '\nBildmontage')
    text = text.replace('Linolschnitt', '')
    text = text.replace('Kaefersammler', 'Käfersammler')
    text = text.replace('Vielfrass', 'Vielfraß')
    text = text.replace('MigrationUeberschreitetGrenzen', 'Migration\nüberschreitet\nGrenzen')
    text = text.replace('Migration Ueberschreitet Grenzen', 'Migration\nüberschreitet\nGrenzen')
    text = text.replace('Duerer', 'Dürer')
    text = text.replace('Doodle2', 'Doodle')
    text = text.replace('Gefässe', 'Gefäße')
    text = text.replace('Griech', 'Griechische Vasen')
    text = text.replace('Griechische Vasenische Vasen', 'Griechische Vasen')
    text = text.replace('Perspektivisches ', 'Perspektivisches\n')

    return text

#dateinamen mit leerzeichen kommen mir nicht ins haus // reinsert spaces into pascal case text
def add_spaces_to_project_name(project):
    return ''.join([' ' + char if char.isupper() and ((i == 0 or not project[i - 1].isspace())and (i - 1)>=0) else char for i, char in
                    enumerate(project)])


def create_canvas_one(images, captions, output_path, project, class_level,year, single_double_full_size, text_left=True):
    image = images[0]
    caption = str(captions[0])

    # Determine the size of each cell
    if single_double_full_size:
        cell_height = (canvas_height - 2 * border_padding - 3 * padding - 2 * font_size - caption_padding) // 2
        cell_width = (canvas_width - 2 * border_padding - 3 * padding) // 2
    else:
        cell_height = canvas_height - 2 * border_padding - 2 * padding - font_size - caption_padding
        cell_width = canvas_width - 2 * border_padding - 2 * padding

    #canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    #draw = ImageDraw.Draw(canvas)
    canvas, draw = create_canvas_with_gradient(width=canvas_width, height=canvas_height)

    try:
        font = ImageFont.truetype(font_path, font_size)
        font_info = ImageFont.truetype(font_path, font_size_info)
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

    # Add info text next to the image
    info_text = add_spaces_to_project_name(project) + f'\nKlasse {class_level}\nJahr {year}'
    info_text = adjust_text(info_text, font_info, canvas_width, draw)

    if text_left:
        text_x = image_x - padding - draw.textbbox((0, 0), info_text, font=font_info)[2]
    else:
        text_x = image_x + new_width + padding

    text_y = image_y
    draw.text((text_x, text_y), info_text, fill="black", font=font_info)

    if debug:
        text_bbox = draw.textbbox((text_x, text_y), info_text, font=font_info)
        draw.rectangle(text_bbox, outline="red", width=2)

    canvas.save(output_path)
def create_canvas_two(images, captions, output_path, project, class_level,year, single_double_full_size):
    # Determine the size of each cell
    cell_width = (canvas_width - 2 * border_padding - 3 * padding) // 2
    if single_double_full_size:
        cell_height = (canvas_height - 2 * border_padding - 3 * padding - 2 * font_size - caption_padding) // 2
    else:
        cell_height = canvas_height - 2 * border_padding - 2 * padding - font_size - caption_padding

    #canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    #draw = ImageDraw.Draw(canvas)
    canvas, draw = create_canvas_with_gradient(width=canvas_width, height=canvas_height)

    try:
        font = ImageFont.truetype(font_path, font_size)
        font_info = ImageFont.truetype(font_path, font_size_info)
    except OSError:
        print(f"Error: Cannot open font resource at {font_path}")
        return

    # Calculate the reference frames for all images
    reference_frames = []
    for image in images:
        image_ratio = image.width / image.height
        frame_ratio = cell_width / cell_height

        if image_ratio > frame_ratio:
            new_width = cell_width
            new_height = int(new_width / image_ratio)
        else:
            new_height = cell_height
            new_width = int(new_height * image_ratio)

        reference_frames.append((new_width, new_height))

    # Identify the smallest width reference frame
    smallest_frame = min(reference_frames, key=lambda x: x[0])
    smallest_frame_index = reference_frames.index(smallest_frame)
    widest_frame = max(reference_frames, key=lambda x: x[0])

    # Calculate the positions of the cells to center them on the canvas
    cell_positions = [
        (border_padding + padding, (canvas_height - cell_height) // 2),
        (border_padding + cell_width + 2 * padding, (canvas_height - cell_height) // 2),
        (border_padding + padding, (canvas_height - cell_height) // 2 + cell_height + 2 * padding + font_size + caption_padding),
        (border_padding + cell_width + 2 * padding, (canvas_height - cell_height) // 2 + cell_height + 2 * padding + font_size + caption_padding)
    ]

    smallest_middle_x = 0
    smallest_image_x = 0

    for i, (pos, image, caption) in enumerate(zip(cell_positions, images, captions)):
        new_width, new_height = reference_frames[i]
        image = image.resize((new_width, new_height), Image.LANCZOS)

        # Move the reference frame as far inwards as possible
        if i % 2 == 0:  # Left column
            ref_x = pos[0] + cell_width - widest_frame[0]
        else:  # Right column
            ref_x = pos[0]
        ref_y = pos[1] + (cell_height - widest_frame[1]) // 2

        # Center the image within its reference frame
        image_x = ref_x + (widest_frame[0] - new_width) // 2
        image_y = pos[1] + (cell_height - new_height) // 2

        canvas.paste(image, (image_x, image_y))

        if i == smallest_frame_index:
            smallest_middle_x = image_x + new_width // 2
            smallest_image_x = pos[0]

        # Add caption directly below the image
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = image_x + (new_width - text_width) // 2
        text_y = image_y + new_height + caption_padding
        draw.text((text_x, text_y), caption, fill="black", font=font)

        # Draw the original cell bounds in blue if debug is True
        if debug:
            draw.rectangle([pos, (pos[0] + cell_width, pos[1] + cell_height)], outline="blue", width=2)

        # Draw the widest reference frame in red if debug is True
        if debug and i == reference_frames.index(widest_frame):
            draw.rectangle([ref_x, ref_y, ref_x + widest_frame[0], ref_y + widest_frame[1]], outline="red", width=2)

        # Draw the induced reference frame in black if debug is True
        if debug and i != reference_frames.index(widest_frame):
            draw.rectangle([ref_x, ref_y, ref_x + widest_frame[0], ref_y + widest_frame[1]], outline="black", width=2)

    # Add info text next to the smallest width image
    smallest_index = reference_frames.index(smallest_frame)
    smallest_pos = cell_positions[smallest_index]
    info_text = add_spaces_to_project_name(project) + f'\nKlasse {class_level}\nJahr {year}'
    info_text = adjust_text(info_text, font_info, canvas_width, draw)

    if smallest_index % 2 == 0:  # Left column
        text_x = smallest_middle_x - (smallest_frame[0] / 2) - padding - draw.textbbox((0, 0), info_text, font=font_info)[2]
        available_space = (smallest_middle_x - (smallest_frame[0] / 2) - padding)
        if debug:
            draw.line([(smallest_middle_x, smallest_pos[1]), (smallest_middle_x, smallest_pos[1] + smallest_frame[1])], fill="orange", width=2)
            draw.line([(smallest_middle_x - (smallest_frame[0] / 2), smallest_pos[1]), (smallest_middle_x - (smallest_frame[0] / 2), smallest_pos[1] + smallest_frame[1])], fill="yellow", width=2)
    else:  # Right column
        text_x = smallest_middle_x + (smallest_frame[0] / 2) + padding
        available_space = canvas_width - (smallest_middle_x + (smallest_frame[0] / 2) + padding)
        if debug:
            draw.line([(smallest_middle_x, smallest_pos[1]), (smallest_middle_x, smallest_pos[1] + smallest_frame[1])], fill="orange", width=2)
            draw.line([(smallest_middle_x + (smallest_frame[0] / 2), smallest_pos[1]), (smallest_middle_x + (smallest_frame[0] / 2), smallest_pos[1] + smallest_frame[1])], fill="yellow", width=2)

    text_bbox = draw.textbbox((text_x, smallest_pos[1]), info_text, font=font_info)
    draw.text((text_x, smallest_pos[1]), info_text, fill="black", font=font_info)

    if debug:
        draw.rectangle(text_bbox, outline="red", width=2)

    canvas.save(output_path)


def create_canvas_three(images, captions, output_path, project, class_level, year):
    # Determine the size of each quadrant
    quadrant_width = (canvas_width - 2 * border_padding - 3 * padding) // 2
    quadrant_height = (canvas_height - 2 * border_padding - 3 * padding - 2 * font_size - caption_padding) // 2

    #canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    #draw = ImageDraw.Draw(canvas)
    canvas, draw = create_canvas_with_gradient(width=canvas_width, height=canvas_height)

    try:
        font = ImageFont.truetype(font_path, font_size)
        font_info = ImageFont.truetype(font_path, font_size_info)
    except OSError:
        print(f"Error: Cannot open font resource at {font_path}")
        return

    # Calculate the reference frames for all images
    reference_frames = []
    for image in images:
        image_ratio = image.width / image.height
        frame_ratio = quadrant_width / quadrant_height

        if image_ratio > frame_ratio:
            new_width = quadrant_width
            new_height = int(new_width / image_ratio)
        else:
            new_height = quadrant_height
            new_width = int(new_height * image_ratio)

        reference_frames.append((new_width, new_height))

    # Identify the smallest width reference frame
    smallest_frame = min(reference_frames, key=lambda x: x[0])
    smallest_frame_index = reference_frames.index(smallest_frame)
    widest_frame = max(reference_frames, key=lambda x: x[0])

    # Draw the original quadrants if debug is True
    if debug:
        for pos in [(border_padding + padding, border_padding + padding),
                    (border_padding + quadrant_width + 2 * padding, border_padding + padding),
                    (border_padding + padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding),
                    (border_padding + quadrant_width + 2 * padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding)]:
            draw.rectangle([pos, (pos[0] + quadrant_width, pos[1] + quadrant_height)], outline="blue", width=2)

    # Paste images onto the canvas, skipping the upper left quadrant
    positions = [(border_padding + quadrant_width + 2 * padding, border_padding + padding),
                 (border_padding + padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding),
                 (border_padding + quadrant_width + 2 * padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding)]

    smallest_middle_x = 0
    smallest_image_x = 0

    for i, (pos, image, caption) in enumerate(zip(positions, images, captions)):
        new_width, new_height = reference_frames[i]
        image = image.resize((new_width, new_height), Image.LANCZOS)

        # Move the reference frame as far to the top or bottom as possible
        if i < 1:  # Top row
            ref_y = pos[1] + quadrant_height - widest_frame[1]
        else:  # Bottom row
            ref_y = pos[1]

        if i == 1:  # not i%2 == 0:  # left column
            ref_x = pos[0] + quadrant_width - widest_frame[0]
        else:  # Right column
            ref_x = pos[0]

        # Place the image centered widthwise
        image_x = ref_x + (widest_frame[0] - new_width) // 2

        # Align the top edge of the image with the top line of the reference frame for the bottom row
        # Align the bottom edge of the image with the bottom line of the reference frame for the top row
        if i < 1:  #not 2 Top row
            image_y = ref_y + widest_frame[1] - new_height
        else:  # Bottom row
            image_y = ref_y

        canvas.paste(image, (image_x, image_y))

        if i == smallest_frame_index:
            smallest_middle_x = image_x + new_width // 2
            smallest_image_x = ref_x

        # Draw the reference frame of the widest picture in red if debug is True
        if debug and i == reference_frames.index(widest_frame):
            draw.rectangle([ref_x, ref_y, ref_x + widest_frame[0], ref_y + widest_frame[1]], outline="red", width=2)

        # Draw the projected frame onto the other quadrants in black if debug is True
        if debug and i != reference_frames.index(widest_frame):
            draw.rectangle([ref_x, ref_y, ref_x + widest_frame[0], ref_y + widest_frame[1]], outline="black", width=2)

        # Add caption
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = image_x + (new_width - text_width) // 2
        text_y = image_y + new_height + caption_padding
        draw.text((text_x, text_y), caption, fill="black", font=font)

    # Move the widest reference frame into the upper left quadrant, aligning its bottom right corner with the quadrant's lower right corner
    widest_frame_x = border_padding + padding + quadrant_width - widest_frame[0]
    widest_frame_y = border_padding + padding + quadrant_height - widest_frame[1]

    if debug:
        draw.rectangle([widest_frame_x, widest_frame_y, widest_frame_x + widest_frame[0], widest_frame_y + widest_frame[1]], outline="green", width=2)

    # Add info text centered inside the widest reference frame
    info_text = add_spaces_to_project_name(project) + f'\nKlasse {class_level}\nJahr {year}'
    info_text = adjust_text(info_text, font_info, canvas_width, draw)
    text_bbox = draw.textbbox((0, 0), info_text, font=font_info)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = widest_frame_x + (widest_frame[0] - text_width) // 2
    text_y = widest_frame_y + (widest_frame[1] - text_height) // 2
    draw.text((text_x, text_y), info_text, fill="black", font=font_info)

    if debug:
        draw.rectangle([text_x, text_y, text_x + text_width, text_y + text_height], outline="red", width=2)

    canvas.save(output_path)

def create_canvas(images, captions, output_path, project, class_level, year):
    if custom_order:
        if(len(images)>=4):
            pass
        elif len(images) == 3:
            create_canvas_three(images, captions, output_path, project, class_level, year)
            return
        elif len(images) == 2:
            create_canvas_two(images, captions, output_path, project, class_level,year, maintain_size)
            return
        elif len(images) == 1:
            create_canvas_one(images, captions, output_path, project, class_level,year, maintain_size)
            return
            #pass
    # Determine the size of each quadrant
    quadrant_width = (canvas_width - 2 * border_padding - 3 * padding) // 2
    quadrant_height = (canvas_height - 2 * border_padding - 3 * padding - 2 * font_size - caption_padding) // 2

    #canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    #draw = ImageDraw.Draw(canvas)
    canvas, draw = create_canvas_with_gradient(width=canvas_width, height=canvas_height)

    try:
        font = ImageFont.truetype(font_path, font_size)
        font_info = ImageFont.truetype(font_path, font_size_info)
    except OSError:
        print(f"Error: Cannot open font resource at {font_path}")
        return

    # Calculate the reference frames for all images
    reference_frames = []
    for image in images:
        image_ratio = image.width / image.height
        frame_ratio = quadrant_width / quadrant_height

        if image_ratio > frame_ratio:
            new_width = quadrant_width
            new_height = int(new_width / image_ratio)
        else:
            new_height = quadrant_height
            new_width = int(new_height * image_ratio)

        reference_frames.append((new_width, new_height))

    # Identify the smallest width reference frame
    smallest_frame = min(reference_frames, key=lambda x: x[0])
    smallest_frame_index = reference_frames.index(smallest_frame)
    widest_frame = max(reference_frames, key=lambda x: x[0])

    # Draw the original quadrants
    if debug:
        for pos in [(border_padding + padding, border_padding + padding),
                    (border_padding + quadrant_width + 2 * padding, border_padding + padding),
                    (border_padding + padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding),
                    (border_padding + quadrant_width + 2 * padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding)]:
            draw.rectangle([pos, (pos[0] + quadrant_width, pos[1] + quadrant_height)], outline="blue", width=2)

    # Paste images onto the canvas
    positions = [(border_padding + padding, border_padding + padding),
                 (border_padding + quadrant_width + 2 * padding, border_padding + padding),
                 (border_padding + padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding),
                 (border_padding + quadrant_width + 2 * padding, border_padding + quadrant_height + 2 * padding + font_size + caption_padding)]


    smallest_middle_x = 0
    smallest_image_x = 0

    for i, (pos, image, caption) in enumerate(zip(positions, images, captions)):
        new_width, new_height = reference_frames[i]
        image = image.resize((new_width, new_height), Image.LANCZOS)

        # Move the reference frame as far to the top or bottom as possible
        if i < 2:  # Top row
            ref_y = pos[1] + quadrant_height - widest_frame[1]
        else:  # Bottom row
            ref_y = pos[1]

        if i % 2 == 0:  # Left column
            ref_x = pos[0] + quadrant_width - widest_frame[0]
        else:  # Right column
            ref_x = pos[0]

        # Place the image centered widthwise
        image_x = ref_x + (widest_frame[0] - new_width) // 2

        # Align the top edge of the image with the top line of the reference frame for the bottom row
        # Align the bottom edge of the image with the bottom line of the reference frame for the top row
        if i < 2:  # Top row
            image_y = ref_y + widest_frame[1] - new_height
        else:  # Bottom row
            image_y = ref_y

        canvas.paste(image, (image_x, image_y))

        if i == smallest_frame_index:
            smallest_middle_x = image_x + new_width // 2
            smallest_image_x = ref_x

        # Draw the reference frame of the widest picture in red if debug is True
        if debug and i == reference_frames.index(widest_frame):
            draw.rectangle([ref_x, ref_y, ref_x + widest_frame[0], ref_y + widest_frame[1]], outline="red", width=2)

        # Draw the projected frame onto the other quadrants in black if debug is True
        if debug and i != reference_frames.index(widest_frame):
            draw.rectangle([ref_x, ref_y, ref_x + widest_frame[0], ref_y + widest_frame[1]], outline="black", width=2)

        # Add caption
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = image_x + (new_width - text_width) // 2
        text_y = image_y + new_height + caption_padding
        draw.text((text_x, text_y), caption, fill="black", font=font)

    # Add info text next to the smallest width image
    smallest_index = reference_frames.index(smallest_frame)
    smallest_pos = positions[smallest_index]
    info_text = add_spaces_to_project_name(project) + f'\nKlasse {class_level}\nJahr {year}'
    info_text = adjust_text(info_text, font_info, canvas_width, draw)
    # Calculate the x-coordinate for the yellow line
    half_smallest_width = smallest_frame[0] // 2
    center_x = smallest_pos[0] + (widest_frame[0] - smallest_frame[0]) // 2 + half_smallest_width

    """
        if smallest_index % 2 == 0:  # Left column
            text_x = center_x - padding - draw.textbbox((0, 0), info_text, font=font_info)[2]
            if debug:
                draw.line([(center_x, smallest_pos[1]), (center_x, smallest_pos[1] + smallest_frame[1])], fill="yellow", width=2)
                draw.line([(center_x, smallest_pos[1] + smallest_frame[1] // 2), (text_x, smallest_pos[1] + smallest_frame[1] // 2)], fill="orange", width=2)
                draw.line([(center_x, smallest_pos[1]), (center_x, smallest_pos[1] + smallest_frame[1])], fill="orange", width=2)
        else:  # Right column
            text_x = center_x + padding
            if debug:
                draw.line([(center_x, smallest_pos[1]), (center_x, smallest_pos[1] + smallest_frame[1])], fill="yellow", width=2)
                draw.line([(center_x, smallest_pos[1] + smallest_frame[1] // 2), (text_x, smallest_pos[1] + smallest_frame[1] // 2)], fill="orange", width=2)
                draw.line([(center_x, smallest_pos[1]), (center_x, smallest_pos[1] + smallest_frame[1])], fill="orange", width=2)
    """
    #adjusted_text = adjust_text(info_text, font_info, canvas_width, draw)
    if smallest_index % 2 == 0:  # Left column
        text_x = smallest_middle_x - (smallest_frame[0]/2) - padding - draw.textbbox((0, 0), info_text, font=font_info)[2]
        available_space = (smallest_middle_x-(smallest_frame[0]/2) - padding)
        if debug:
            draw.line([(smallest_middle_x, smallest_pos[1]), (smallest_middle_x, smallest_pos[1] + smallest_frame[1])], fill="orange",width=2)
            draw.line([(smallest_middle_x-(smallest_frame[0]/2), smallest_pos[1]), (smallest_middle_x-(smallest_frame[0]/2), smallest_pos[1] + smallest_frame[1])], fill="yellow", width=2)
        #adjusted_text = adjust_text_left(info_text, font_info, available_space, draw)
    else:  # Right column
        text_x = smallest_middle_x +(smallest_frame[0]/2) + padding
        available_space = canvas_width- (smallest_middle_x +(smallest_frame[0]/2) + padding)
        if debug:
            draw.line([(smallest_middle_x, smallest_pos[1]), (smallest_middle_x, smallest_pos[1] + smallest_frame[1])], fill="orange",width=2)
            draw.line([(smallest_middle_x+(smallest_frame[0]/2), smallest_pos[1]), (smallest_middle_x+(smallest_frame[0]/2), smallest_pos[1] + smallest_frame[1])], fill="yellow", width=2)
        #adjusted_text = adjust_text_right(info_text, font_info, available_space, draw)

    text_bbox = draw.textbbox((text_x, smallest_pos[1]), info_text, font=font_info)
    draw.text((text_x, smallest_pos[1]), info_text, fill="black", font=font_info)

    if debug:
        draw.rectangle(text_bbox, outline="red", width=2)

    canvas.save(output_path)

for root, dirs, files in os.walk(input_dir):
    if any(ignored in root for ignored in ignore_folders):
        continue

    images = []
    captions = []
    for file in files[:4]:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            image = Image.open(file_path)
            images.append(image)
            captions.append(os.path.splitext(file)[0])

    if images:
        project = root.split('\\')[-1].split('_')[0]
        class_level = root.split('_')[-1]
        output_filename = f'{class_level}_{project}.jpg'
        output_filename = get_unique_filename(output_dir, output_filename)
        output_path = os.path.join(output_dir, output_filename)
        year = root.split('\\')[-2].replace('_', '/')
        #create_canvas(images, ['','','',''], output_path, project, class_level, year) # overwrite captions/names with empty strings as per request by teacher
        create_canvas(images, captions, output_path, project, class_level, year)
        num_files_saved += 1

print(f"Processed {num_files_saved} images")