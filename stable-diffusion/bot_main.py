from gzip import READ
import logging
from typing import Dict
from add_text import add_txt
from rugpt3.generate_text import text_generate
#import pymorphy2
from PIL import Image
from configs import TELEGRAM_API_TOKEN
from image_generation import generate_image
from telegram import __version__ as TG_VER
from translation_rus_to_eng import translate
from telegram import ForceReply, Update, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
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

#morph = pymorphy2.MorphAnalyzer()
SPB_PLACES = {'казанский собор':'*', 'лахта':'@', 'зимний дворец':'%'}

CREATE_PACK, SAVE_STICKERPACK_NAME, GENERATE_STICKER, SAVE_STICKER, SAVE_EMOJI, SAVE_STICKERPACK = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Введите команду /create_new_stickerpack, чтобы начать генерацию стикерпака",
        reply_markup=ForceReply(selective=True),
    )
    return CREATE_PACK


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""Введите команду /cancel чтобы начать процесс генерации заново.
    /create_new_stickerpack
    """)


async def create_new_stickerpack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(update.to_dict())
    await update.message.reply_text('Введите название для стикерпака.')
    return SAVE_STICKERPACK_NAME


async def save_stickerpack_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    stickerpack_name = update.message.text
    context.user_data['current_stickerpack_name'] = stickerpack_name.lower().replace(' ','')[:40]
    context.user_data['stickers'] = []
    context.user_data['emojis'] = []
    await update.message.reply_text(('Введите текстовое описание стикера, который хотите сгенерировать.' 
        'beta: Или отправьте боту картинку для режима image2image'))
    return GENERATE_STICKER


async def generate_sticker_img2img(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo_file = await update.message.photo[-1].get_file()
    init_img_path = f'outputs/userphoto_{update.message.chat.id}.png' 
    await photo_file.download(init_img_path)
    size = (512, 512)
    with Image.open(init_img_path) as img:
        img = img.resize(size)
        img.save(init_img_path,format="PNG", resample=Image.Resampling.NEAREST)
    context.user_data['init_img_path'] = init_img_path
    await update.message.reply_text(('Картинка сохранена!'
        'Теперь введие текстовое описание того как вы хотите изменить картинку'))
    return GENERATE_STICKER


async def generate_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Стикер генерируется...')
    text_prompt = update.message.text.lower()
    #prompt_words = text_prompt.split()
    #lemmatized_text = ' '.join([morph.parse(word)[0].normal_form for word in prompt_words])
    for place_name in SPB_PLACES.keys():        
        text_prompt = text_prompt.replace(place_name, SPB_PLACES[place_name]) #use stemming here
    # translating from rus to eng
    eng_text_prompt = translate(text_prompt)
    eng_text_prompt = 'a photo of ' + eng_text_prompt + ', hd'
    print(f'English translation: {eng_text_prompt}')
    if 'init_img_path' in context.user_data:
        if context.user_data['init_img_path'] is not None:
            await update.message.reply_text('Генерация стикера в режиме image2image')
            img_path = generate_image(eng_text_prompt, context.user_data['init_img_path'])
        else:
            img_path = generate_image(eng_text_prompt)
    else:
        img_path = generate_image(eng_text_prompt)
    context.user_data['current_sticker_image_path'] = img_path
    context.user_data['init_img_path'] = None
    await update.message.reply_photo(open(img_path, 'rb'))
    await update.message.reply_text(
        f"""Стикер сгенерирован! 
        Введите команду /save_sticker, чтобы добавить стикер в стикерпак {context.user_data['current_stickerpack_name']}.
        Введите команду /generate_text , чтобы сгенерировать нейросетью подпись к стикеру.
        Введите текст, чтобы добавить самому текст на картинке.
        Введите команду /skip_sticker , чтобы сгенерировать стикер заново
        """
    )
    return SAVE_STICKER
    

async def generate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #text = update.message.text
    text = 'Забавный факт. В Санкт-Петербурге '
    text = text_generate(text) 
    img_path = context.user_data['current_sticker_image_path']
    image = add_txt(text, img_path)
    save_path = img_path#'outputs/img-samples/test-result.jpg'
    image.save(img_path)
    await update.message.reply_photo(open(save_path, "rb"))
    await update.message.reply_text("""Введите команду /save_sticker, чтобы добавить стикер в стикерпак test_sticker_2.
        Введите команду /skip_sticker , чтобы сгенерировать стикер заново""")
    return SAVE_STICKER


async def add_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    img_path = context.user_data['current_sticker_image_path']
    image = add_txt(text, img_path)
    save_path = img_path#'outputs/img-samples/test-result.jpg'
    image.save(img_path)
    await update.message.reply_photo(open(save_path, "rb"))
    await update.message.reply_text("""Введите команду /save_sticker, чтобы добавить стикер в стикерпак test_sticker_2.
        Введите команду /skip_sticker , чтобы сгенерировать стикер заново""")
    return SAVE_STICKER


async def save_stickerpack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.create_new_sticker_set(update.message.chat.id, name=f"{context.user_data['current_stickerpack_name']}_by_neural_spb_bot", 
        title=context.user_data['current_stickerpack_name'], png_sticker=open(context.user_data['stickers'][0], 'rb'),
        emojis=context.user_data['emojis'][0],
        )
    for i in range(1,len(context.user_data['stickers'])):
        await context.bot.add_sticker_to_set(update.message.chat.id, name=f"{context.user_data['current_stickerpack_name']}_by_neural_spb_bot", 
        emojis=context.user_data['emojis'][i], png_sticker=open(context.user_data['stickers'][i], 'rb'),)
    # empty user data
    context.user_data['stickers'] = []
    context.user_data['emojis'] = []
    context.user_data['init_img_path'] = None
    await update.message.reply_text(
        (f"Стикерпак создан! Cсылка на добавление: t.me/addstickers/{context.user_data['current_stickerpack_name']}_by_neural_spb_bot ."
        "Введите команду /create_new_stickerpack , чтобы создать ещё один набор стикеров."
    ))
    return ConversationHandler.END


async def save_sticker_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите эмоджи, который будет связан с этим стикером"
    )
    return SAVE_EMOJI


async def save_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji = update.message.text
    #context.user_data['current_sticker_emoji'] = emoji
    context.user_data['stickers'].append(context.user_data['current_sticker_image_path'])
    context.user_data['emojis'].append(emoji) # append full sticker information to stickerpack
    await update.message.reply_text(
        "Отлично! Стикер сохранен. Введите /save_stickerpack , чтобы сохранить стикерпак. Или /new_sticker , чтобы сгенерировать новый стикер"
    )
    return SAVE_STICKER


async def skip_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        ("Введите описание для стикера." 
        "beta: или отправьте фото боту")
    )
    return GENERATE_STICKER

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    context.user_data['current_stickerpack_name']=''
    context.user_data['current_sticker_image_path'] = ''
    context.user_data['current_sticker_emoji'] = ''
    context.user_data['stickers'] = []
    context.user_data['emojis'] = []
    context.user_data['init_img_path'] = None
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the gathered info."""
    await update.message.reply_text(
        f"This is what you already told me: {facts_to_str(context.user_data)}"
    )


def main() -> None:
    """Start the bot."""
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(TELEGRAM_API_TOKEN).persistence(persistence).build()
    #application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler('create_new_stickerpack',create_new_stickerpack)],
        states={
            CREATE_PACK: [CommandHandler('create_new_stickerpack', create_new_stickerpack)],
            SAVE_STICKERPACK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_stickerpack_name)],
            GENERATE_STICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_sticker), MessageHandler(filters.PHOTO, generate_sticker_img2img)],
            SAVE_STICKER: [CommandHandler('save_sticker', save_sticker_image), 
                            CommandHandler('generate_text', generate_text), 
                            MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_text),
                            CommandHandler('skip_sticker', skip_sticker),
                            CommandHandler('new_sticker', skip_sticker),
                            CommandHandler('save_stickerpack', save_stickerpack)
                        ],
            SAVE_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_emoji)],
            SAVE_STICKERPACK:[CommandHandler('save_stickerpack', save_stickerpack)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="my_conversation",
        persistent=True,
    )
    application.add_handler(conv_handler)

    show_data_handler = CommandHandler("show_data", show_data)
    application.add_handler(show_data_handler)

    # application.add_handler(
    #     MessageHandler(filters.TEXT & ~filters.COMMAND, generate_sticker)
    # )
    application.run_polling()


if __name__ == "__main__":
    main()
