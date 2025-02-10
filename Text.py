import os
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = 933120000  # needed for 4k

with open('ignore/paths.txt') as f:
    paths = [line.strip() for line in f.readlines()]

input_dir = paths[8]
output_dir = paths[9]
padding = 60
border_padding = 180
caption_padding = 40
font_path = paths[10]  # Path to a .ttf font file
bold_font_path = paths[17]  # Path to a bold .ttf font file
font_size = 80
center_images = False  # whether the images should be truly centered or rather kind of centered and proportionally aligned
custom_order = True  # whether the resulting canvas ordering should be done differently from the strict 4 image layout / 2x2 grid

debug = False  # Add geometric lines to show where calculations are made, useful for debugging the cells, quadrants, alignment etc.

canvas_height = 2160
canvas_width = 3840

num_files_saved = 0


def create_radial_gradient(width, height, center_color, edge_color):
    image = Image.new('RGBA', (width, height))
    center_x = width // 2
    center_y = height // 2
    max_distance = (center_x ** 2 + center_y ** 2) ** 0.5
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            ratio = min(distance / max_distance, 1.0)
            r = int(center_color[0] * (1 - ratio) + edge_color[0] * ratio)
            g = int(center_color[1] * (1 - ratio) + edge_color[1] * ratio)
            b = int(center_color[2] * (1 - ratio) + edge_color[2] * ratio)
            pixels[x, y] = (r, g, b, 255)

    return image


def create_canvas_with_gradient(width=canvas_width, height=canvas_height, center_color=(200, 200, 200), edge_color=(60, 60, 60)):
    canvas = create_radial_gradient(width, height, center_color, edge_color)
    canvas = canvas.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    return canvas, draw


"""def create_text_image(text, output_path, width=canvas_width, height=canvas_height, font_path=None, font_size=120,
                      highlight_word=''):
    canvas, draw = create_canvas_with_gradient(width, height)

    try:
        regular_font = ImageFont.truetype(font_path, font_size)
        bold_font = ImageFont.truetype(font_path.replace('-Regular.tff', '-Bold.tff'), int(font_size * 1.5))  # 20% larger
        #bold_font_path
    except OSError:
        print(f"Error: Cannot open font resource at {font_path}")
        return

    lines = text.split('\n')
    max_line_width = max(draw.textbbox((0, 0), line, font=regular_font)[2] for line in lines)
    total_text_height = sum(draw.textbbox((0, 0), line, font=regular_font)[3] for line in lines)

    text_x = (width - max_line_width) // 2
    text_y = (height - total_text_height) // 2

    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=regular_font)[2]
        line_x = text_x + (max_line_width - line_width) // 2

        if highlight_word and highlight_word in line:
            parts = line.split(highlight_word)
            current_x = line_x

            for i, part in enumerate(parts):
                if part:
                    draw.text((current_x, text_y), part.strip(), fill="black", font=regular_font)
                    current_x += draw.textbbox((0, 0), part, font=regular_font)[2]

                if i < len(parts) - 1:
                    draw.text((current_x, text_y), highlight_word, fill="black", font=bold_font)
                    current_x += draw.textbbox((0, 0), highlight_word, font=bold_font)[2]
        else:
            draw.text((line_x, text_y), line, fill="black", font=regular_font)

        text_y += draw.textbbox((0, 0), line, font=regular_font)[3]

    canvas.save(output_path)"""

def create_text_image(text, output_path, width=canvas_width, height=canvas_height, font_path=None, font_size=120, highlight_word=''):
    canvas, draw = create_canvas_with_gradient(width, height)

    try:
        regular_font = ImageFont.truetype(font_path, font_size)
        bold_font = ImageFont.truetype(bold_font_path, font_size)  # Same size, just bold
    except OSError:
        print(f"Error: Cannot open font resource at {font_path}")
        return

    lines = text.split('\n')
    max_line_width = max(draw.textbbox((0, 0), line, font=regular_font)[2] for line in lines)
    total_text_height = sum(draw.textbbox((0, 0), line, font=regular_font)[3] for line in lines)

    text_x = (width - max_line_width) // 2
    text_y = (height - total_text_height) // 2

    for line in lines:
        line = line.strip()
        line_width = draw.textbbox((0, 0), line, font=regular_font)[2]
        line_x = text_x + (max_line_width - line_width) // 2

        if highlight_word and highlight_word in line:
            parts = line.split(highlight_word)
            current_x = line_x

            for i, part in enumerate(parts):
                if part:
                    draw.text((current_x, text_y), part, fill="black", font=regular_font)
                    current_x += draw.textbbox((0, 0), part, font=regular_font)[2]

                if i < len(parts) - 1:
                    draw.text((current_x, text_y), highlight_word, fill="black", font=bold_font)
                    current_x += draw.textbbox((0, 0), highlight_word, font=bold_font)[2]
        else:
            draw.text((line_x, text_y), line, fill="black", font=regular_font)

        text_y += draw.textbbox((0, 0), line, font=regular_font)[3]

    canvas.save(output_path)



if __name__ == '__main__':
    create_text_image(
    f'''Die
    Fachschaft Kunst
    stellt sich
    vor''', highlight_word='Kunst',
                      output_path=output_dir + '/text_image1.jpg',
                      font_path=font_path, font_size=180)

