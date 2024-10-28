from telegram import ReplyKeyboardMarkup

def create_fixed_keyboard(commands: list, cols=2):
    """
    Given a list of commands, returns a permanent custom keyboard layout.
    
    Args:
    commands (list): List of strings representing command names for the keyboard.

    Returns:
    ReplyKeyboardMarkup: Telegram custom keyboard layout.
    """
    keyboards = []
    for i in range(0, len(commands), cols):
        row = commands[i:i+cols]
        keyboards.append(row)

    # Create and return the keyboard
    return ReplyKeyboardMarkup(keyboards, resize_keyboard=True, one_time_keyboard=False)
