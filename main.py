# self made cookie clicker bot project - took 7 days

# todo: write some code to make the program click the cookie x times based on the current cookie amount, so we arent buying low upgrades
# todo: if a golden cookie is clicked, click the cookie as long as the golden cookie active, and while active also check for other golden cookies
import time

from selenium.webdriver.common.by import By

from game.constants import CURRENCY_OPTIONS, VALUES
from game.formatting_text import black_format_text, yellow_format_text
from game.game_functions import Gamefunctions


# prints blue text
def blue_format_text(text: str) -> str:
    return f"\033[34m{text}\033[0m"


with Gamefunctions() as bot:
    upgrades_list = [
        12000,
        130000,
        1400000,
        20000000,
        330000000,
        5100000000,
        75000000000,
        1000000000000,
        14000000000000,
        170000000000000,
        2100000000000000,
        26000000000000000,
        310000000000000000,
    ]

    bot.land_website()
    bot.click_language_popup()
    bot.remove_cookies()
    bot.import_from_file(bot.load_json, bot.dump_json)
    bot.get_gc_coount(bot.load_json, bot.dump_json, bot.check_golden)

    def main():
        upgrades_to_find = 3
        big_cookie = bot.find_element(By.ID, "bigCookie")
        for i in range(1, 100000):
            # click the cookie 300 times
            for _ in range(300):
                bot.click(
                    bot.click,
                    big_cookie,
                    bot.check_golden,
                    black_format_text,
                    bot.load_json,
                    bot.dump_json,
                    yellow_format_text,
                )

            # check if there is a golden cookie on the screen
            bot.implicitly_wait(0.01)
            bot.check_golden(
                bot.load_json,
                bot.dump_json,
                yellow_format_text,
            )
            bot.check_active_gc(
                bot.click,
                big_cookie,
                bot.check_golden,
                black_format_text,
                bot.load_json,
                bot.dump_json,
                yellow_format_text,
            )

            # get cookies
            cookies = bot.get_cookie_count()
            cookies = bot.conv(cookies, CURRENCY_OPTIONS, VALUES, bot.list_convert)
            print(blue_format_text(f"cookie count = {cookies}"))

            # check if we need to look for more buildings to upgrade
            if cookies > upgrades_list[0]:
                upgrades_to_find += 1
                del upgrades_list[0]

            # get boosts and apply if possible
            time.sleep(0.2)
            boost = bot.get_boosts()
            bot.check_boost(boost)

            # get building upgrades and prices
            upgrades, prices = bot.get_upgrade_prices(
                upgrades_to_find, bot.list_convert
            )
            bot.check_upgrades(cookies, prices, upgrades, upgrades_to_find)

            # export and check for achievements each 15 times
            if i % 15 == 0:
                bot.export(bot.load_json, bot.dump_json)
                time.sleep(0.2)
            bot.remove_achievements()
            bot.gc_loop = 0

    main()
    # if program ends, export
    bot.export(bot.load_json, bot.dump_json)
