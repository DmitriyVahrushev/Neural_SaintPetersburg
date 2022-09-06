import logging
from PIL import Image, ImageDraw, ImageFont

from configs import TELEGRAM_API_TOKEN
from image_generation import generate_image
from telegram import __version__ as TG_VER
from telegram import ForceReply, Update

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def add_txt(title: str, img_path: str):
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def general_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to the user text."""
    # stable diffusion part
    text_prompt = update.message.text
    img_path = generate_image(text_prompt)
    await update.message.reply_photo(open(img_path, "rb"))

    # adding text part
    await update.message.reply_text("Add text on photo")
    text = update.message.text
    image = add_txt(text)
    image.save("test.jpg")
    await update.message.reply_photo(open(img_path, "rb"))


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, general_reply)
    )
    application.run_polling()


if __name__ == "__main__":
    main()
