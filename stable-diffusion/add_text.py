from PIL import Image, ImageDraw, ImageFont


def add_txt(title: str, img_path: str):
    """Adding text on image"""

    img = Image.open(img_path, "r")
    img_width, img_height = img.size

    drawing = ImageDraw.Draw(img)

    font = ImageFont.truetype("stable-diffusion/font/font.ttf", 30)  # шрифт и размера
    text_width, text_height = drawing.textsize(title, font)

    pos = (
        (img_width - text_width) // 2,
        (img_height - text_height),
    )

    drawing.text(pos, title, font=font, fill="white")

    return img