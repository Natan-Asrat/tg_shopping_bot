from telegram import KeyboardButton, ReplyKeyboardMarkup

def get_main_buttons():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Search products")],
            [KeyboardButton("View sellers")],
            [KeyboardButton("Help")]
        ],
        resize_keyboard=True
    )

def get_restart_button():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Start again")]],
        resize_keyboard=True
    )