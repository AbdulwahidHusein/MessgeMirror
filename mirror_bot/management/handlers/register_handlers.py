from mirror_bot.management.handlers import get_pairs, get_whitelist, add_pair, remove_pair, add_whitelist, remove_whitelist, settings, help, admin, start


def register(bot_app):
    get_pairs.register(bot_app)
    get_whitelist.register(bot_app)
    add_pair.register(bot_app)
    remove_pair.register(bot_app)
    add_whitelist.register(bot_app)
    remove_whitelist.register(bot_app)
    settings.register(bot_app)
    help.register(bot_app)
    admin.register(bot_app)
    start.register(bot_app)