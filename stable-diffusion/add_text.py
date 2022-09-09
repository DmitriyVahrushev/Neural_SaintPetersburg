from PIL import Image, ImageDraw, ImageFont


def break_text(txt: str, font, max_width: int):

    # We share the subset to remember the last finest guess over
    # the text breakpoint and make it faster
    subset: int = len(txt)

    text_size = len(txt)
    while text_size > 0:

        # Let's find the appropriate subset size
        while True:
            width, height = font.getsize(txt[:subset])
            letter_size: float = width / subset

            # min/max(..., subset +/- 1) are to avoid looping infinitely over a wrong value
            if width < max_width - letter_size and text_size >= subset:  # Too short
                subset = max(int(max_width * subset / width), subset + 1)
            elif width > max_width:  # Too large
                subset = min(int(max_width * subset / width), subset - 1)
            else:  # Subset fits, we exit
                break

        yield txt[:subset]
        txt = txt[subset:]
        text_size = len(txt)


def add_txt(title: str, img_path: str):
    """Adding text on image"""

    img = Image.open(img_path, "r")
    img_width, _ = img.size

    drawing = ImageDraw.Draw(img)

    font = ImageFont.truetype("font/font.ttf", 20)  # шрифт и размера

    for i, line in enumerate(break_text(title, font, img_width)):
        drawing.text((0, 22 * i), line, font=font, fill="white")

    return img
