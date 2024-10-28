from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_keyboard(buttons: list, cols=2):
    """
    Given a list of tuples (text, callback_data), returns an inline keyboard layout.
    
    Args:
    buttons (list): List of tuples where each tuple contains the button text and its callback data.

    Returns:
    InlineKeyboardMarkup: Inline keyboard layout.
    """
    # Create a list of inline keyboard buttons
    keyboards = []
    for index in range(0, len(buttons), cols):
        row = [InlineKeyboardButton(text, callback_data=callback_data) for text, callback_data in buttons[index:index+cols]]
        keyboards.append(row)
        
    # Return the inline keyboard
    return InlineKeyboardMarkup(keyboards)
