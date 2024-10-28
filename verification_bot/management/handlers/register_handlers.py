from verification_bot.management.handlers import add_pair, remove_pair, add_whitelist, get_pairs, check_whitelist, remove_whitelist, settings, start



def register(application):
    add_pair.register(application)
    remove_pair.register(application)
    add_whitelist.register(application)
    get_pairs.register(application)
    check_whitelist.register(application)
    remove_whitelist.register(application)
    settings.register(application)
    start.register(application)