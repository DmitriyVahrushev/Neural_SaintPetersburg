# https://drive.google.com/file/d/1C3kBnJJ0CNypcDymwohIpvkH92REEj_3/view?usp=sharing
from PIL import Image, ImageDraw, ImageFont


def text_wrap(text: str, font, max_width: int):
    lines = list()

    # If the text width is smaller than the image width, then no need to split
    # just add it to the line list and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(" ")
        i = 0
        # append every word to a line while its width is shorter than the image width
        while i < len(words):
            line = ""
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line)

    return lines


def add_txt(text: str, img_path: str):
    """Adding text on image"""

    image = Image.open(img_path, "r")

    # Create draw object
    draw = ImageDraw.Draw(image)
    # Draw text on image
    color = "rgb(255,255,255)"  # white color
    x, y = 10, 20  # initial coordinates

    font_path = "/content/font.ttf"
    font = ImageFont.truetype(font=font_path, size=30)

    lines = text_wrap(text, font, image.size[0])
    line_height = font.getsize("hg")[1]  # line weight

    for line in lines:
        draw.text((x, y), line, fill=color, font=font)

        y = y + line_height  # update y-axis for new line

    return image
