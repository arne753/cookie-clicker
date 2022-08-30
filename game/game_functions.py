import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

import game.constants as const
from game.formatting_text import (
    black_format_text,
    cyan_format_text,
    magenta_format_text,
    red_format_text,
    yellow_format_text,
)


class Gamefunctions(webdriver.Chrome):
    def __init__(
        self,
        golden_cookies_clicked_session=0,
        gc_loop=0,
        driver_path=r"C:\Program Files\chromedriver.exe",
        teardown=False,
    ):
        self.driver_path = driver_path
        os.environ["PATH"] += self.driver_path
        self.teardown = teardown
        self.golden_cookies_clicked_session = golden_cookies_clicked_session
        self.gc_loop = gc_loop

        super(Gamefunctions, self).__init__()

        # each time the driver looks for object ex. we will wait 15 seconds (or shorter if the element is found earlier)
        self.implicitly_wait(15)
        self.maximize_window()

    # make the class work when used within context manager
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    # load stats from json file
    def load_json(self) -> dict:
        with open(
            r"C:\Users\arneb\vscode\python\projects\cookie_clicker\stats.json", "r"
        ) as file:
            dict_stats = json.load(file)
        return dict_stats

    # put stats back to the json file
    def dump_json(self, dict_stats) -> None:
        with open(
            r"C:\Users\arneb\vscode\python\projects\cookie_clicker\stats.json", "w"
        ) as file:
            json.dump(dict_stats, indent=4, fp=file)

    # go to the cookie clicker website
    def land_website(self) -> None:
        self.get(const.WEBSITE)

    # click the language popup that appears in the beginning
    def click_language_popup(self) -> None:
        language_element = self.find_element(By.ID, "langSelect-EN")
        language_element.click()

    # remove the element that says that website uses cookies
    def remove_cookies(self) -> None:
        time.sleep(2)
        cookies_element = self.find_element(
            By.CSS_SELECTOR, 'a[data-cc-event="click:dismiss"]'
        )
        cookies_element.click()
        time.sleep(0.2)

    # get the golden cookie count from stats and write it to json file
    def get_gc_coount(self, load_json, dump_json, check_golden) -> None:
        stats_button = self.find_element(By.ID, "statsButton")
        try:
            stats_button.click()
        # if there is a golden cookie in the way, click it
        except:
            check_golden()
            stats_button.click()

        # write the golden cookie clicked count to the json file
        stats = self.find_elements(By.CLASS_NAME, "listing")
        for element in stats:
            innerhtml = str(element.get_attribute("innerHTML")).strip().lower()
            if "golden cookie clicks" in innerhtml:
                dict_stats = load_json()
                dict_stats["golden_cookies_clicked"] = int(innerhtml.split()[3])
                dump_json(dict_stats)
        stats_button.click()

    # remove the achievements on the screen
    def remove_achievements(self) -> None:
        try:
            close_button = self.find_element(
                By.CSS_SELECTOR,
                "div[onclick=\"PlaySound('snd/tick.mp3');Game.CloseNotes();\"]",
            )
            close_button.click()
            print(black_format_text("achievements list removed"))
        except:
            pass

    # get the big cookie element and click it once to avoid errors
    def get_big_cookie(self) -> None:
        big_cookie = self.find_element(By.ID, "bigCookie")
        big_cookie.click()

    # get the save data and paste it in a file
    def export(self, load_json, dump_json) -> None:
        # click the options button on the main screen
        options_button = self.find_element(By.ID, "prefsButton")
        options_button.click()
        time.sleep(0.7)

        # click on the export save button in the options menu
        try:
            export_save = self.find_element(
                By.CSS_SELECTOR,
                r'a[onclick="Game.ExportSave();PlaySound(\'snd/tick.mp3\');"]',
            )
            export_save.click()

            # change some stast in the json file
            dict_stats = load_json()
            dict_stats["exported_time"] += 1
        except:
            print(black_format_text("export failed"))
            try:
                time.sleep(0.7)
                export_save = self.find_element(
                    By.CSS_SELECTOR,
                    r'a[onclick="Game.ExportSave();PlaySound(\'snd/tick.mp3\');"]',
                )
                export_save.click()

                # change some stats in the json file
                dict_stats = load_json()
                dict_stats["exported_time"] += 1
            except:
                print(black_format_text("export failed again"))
                return

        save_data = self.find_element(By.ID, "textareaPrompt").text
        time.sleep(0.10)

        # get rid of the "" at the beginning and the end
        save_data = save_data.replace('"', "")
        dict_stats["save_data"] = save_data

        # click on the done button after copying the save data
        time.sleep(0.10)
        done_button = self.find_element(By.ID, "promptOption0")
        done_button.click()

        # click on the options button again to go to the main screen
        time.sleep(0.10)
        options_button.click()

        print(
            red_format_text(
                "exported | export time = %i" % (dict_stats["exported_time"])
            )
        )
        dump_json(dict_stats)

    # load the sava data from a file
    def import_from_file(self, load_json, dump_json) -> None:
        # click on the options button on the main screen
        options_button = self.find_element(By.ID, "prefsButton")
        options_button.click()
        time.sleep(0.05)

        # click on the import save button in the options menu
        import_save = self.find_element(
            By.CSS_SELECTOR,
            r'a[onclick="Game.ImportSave();PlaySound(\'snd/tick.mp3\');"]',
        )
        import_save.click()
        time.sleep(0.05)

        # click on the input element to input the save data
        text_area = self.find_element(By.ID, "textareaPrompt")
        text_area.clear()
        text_area.click()
        time.sleep(0.05)

        # read the save data from the file and write it to the input field
        dict_stats = load_json()
        time.sleep(0.2)
        text_area.send_keys(dict_stats["save_data"])
        time.sleep(0.05)

        # click on the load button after pasting in the save data
        load_button = self.find_element(By.ID, "promptOption0")
        load_button.click()

        # change json file stats
        dict_stats["imported_time"] += 1

        time.sleep(0.05)
        options_button.click()

        print(
            red_format_text(
                "imported | import time = %i" % (dict_stats["imported_time"])
            )
        )
        dump_json(dict_stats)

    # convert the million, billion etc. behind the cookie count
    def conv(self, cookies_lst, currency_options, values, list_convert) -> int:
        # in case of upgrades, we get cookie count as a string so we need to check that
        if isinstance(cookies_lst, str):
            # in the beginning the third price is empty so we have to return the price of it
            if len(cookies_lst) == 0:
                return 1100
            # we split the cookies string into a list and if the len is higher then 1, it means the cookie had count string like million, billion etc behind its cookie count, so we need to just list convert it then
            cookies_lst = cookies_lst.split()
            if len(cookies_lst) < 2:

                # if cookie didnt have count string, convert it back to a string
                cookies_string = ""
                for i in cookies_lst:
                    cookies_string += i
                    try:
                        cookies_string = cookies_string.replace(",", "")
                        return int(cookies_string)
                    except ValueError:
                        # if we have "" goin in, it means we didnt unlock that item yet, so return a super large number, so the program doesnt think we can buy it
                        return 100**30

            # if the list of the string was of size 2 do the list conversion to cookies
            else:
                cookies = self.list_convert(cookies_lst, currency_options, values)
                return cookies

        # if we got a list going in do the list conversion too
        else:
            cookies = self.list_convert(cookies_lst, currency_options, values)
            return cookies

    # convert cookie count if inputted as a list
    def list_convert(self, cookies_lst, currency_options, values) -> int:
        # if there is no million, billion etc. in the cookie count list, just return the cookie count with , and . replaced
        if cookies_lst[1] not in currency_options:
            cookie_count = cookies_lst[0]
            cookie_count = cookie_count.replace(",", "").replace(".", "")
            return int(cookie_count)

        # convert the million, billion etc to ints
        else:
            cookies = cookies_lst[0]
            index = currency_options.index(cookies_lst[1])
            multiplier = values[index]
            cookies = float(cookies) * multiplier
            return int(cookies)

    # this will return a list with cookie count and some other text [0] is the cookie count
    def get_cookie_count(self):
        cookie_count = self.find_element(By.ID, "cookies").text.split()
        return cookie_count

    # click big cookie
    def click(
        self,
        click,
        big_cookie,
        check_golden,
        black_format_text,
        load_json,
        dump_json,
        yellow_format_text,
    ) -> None:
        # there could be a situation where a golden cookie spawned on top of the big cookie, so the click is intercepted, if that happens click the golden cookie first
        try:
            big_cookie.click()
        except:
            print(black_format_text("big cookie click intercepted"))
            check_golden(
                load_json,
                dump_json,
                yellow_format_text,
            )
            big_cookie.click()

    # check if theres a golden cookie on the screen and click it if there is one
    def check_golden(
        self,
        load_json,
        dump_json,
        yellow_format_text,
    ) -> None:
        try:
            golden = self.find_element(By.CSS_SELECTOR, 'div[alt="Golden cookie"]')
            golden.click()

            # load and write data to stats.json file
            dict_stats = load_json()
            dict_stats["golden_cookies_clicked"] += 1
            self.golden_cookies_clicked_session += 1

            print(
                yellow_format_text(
                    "golden cookie clicked | this session = %i | all time = %i"
                    % (
                        self.golden_cookies_clicked_session,
                        dict_stats["golden_cookies_clicked"],
                    )
                )
            )
            dump_json(dict_stats)

        # if there is no golden cookie on the screen, continue
        except:
            pass

    # check if there is an active golden cookie
    def check_active_gc(
        self,
        click,
        big_cookie,
        check_golden,
        black_format_text,
        load_json,
        dump_json,
        yellow_format_text,
    ):
        # keep clicking the golden cookie as long as the timer is active
        while True:
            # check if the golden cookie is active
            try:
                timer = self.find_element(By.CSS_SELECTOR, 'div[class="pieTimer"]')
            except:
                print(black_format_text("no golden cookie active"))
                self.gc_loop = 0
                break

            # click the cookie 100 times
            for _ in range(100):
                click(
                    click,
                    big_cookie,
                    check_golden,
                    black_format_text,
                    load_json,
                    dump_json,
                    yellow_format_text,
                )

            # if there keep getting golden cookies on the screen and we clicked the big cookie 500 times, quit and buy some upgrades
            self.gc_loop += 1
            print(black_format_text(f"golden cookie click loop = {self.gc_loop}"))
            if self.gc_loop == 10:
                self.gc_loop = 0
                break
            check_golden(
                load_json,
                dump_json,
                yellow_format_text,
            )

    # get a list of all the upgrades and their correspondending prices

    def get_upgrade_prices(self, upgrades_to_find, list_convert) -> list:
        prices = []
        upgrades = []

        for i in range(upgrades_to_find):
            upgrades.append(self.find_element(By.ID, f"productName{str(i)}"))
            price = self.find_element(By.ID, f"productPrice{str(i)}").text

            # convert the price of the upgrade to int and put it in the list
            prices.append(
                Gamefunctions.conv(
                    self, price, const.CURRENCY_OPTIONS, const.VALUES, list_convert
                )
            )

        print(magenta_format_text(f"upgrade prices from high to low = {prices[::-1]}"))
        # both lists are sorted from high to low
        return upgrades[::-1], prices[::-1]

    # click the upgrade found in get_upgrade_prices
    def check_upgrades(self, cookies, prices, upgrades, upgrades_to_find) -> None:
        for i in range(upgrades_to_find):
            upgrade_price = prices[i]
            # list is reversed to find highest possible upgrade
            # we have to revert the list back to the original to find the number of the id for the upgrade html element
            # if we did 1 upgrade we stop
            if cookies > int(upgrade_price):
                reversed_prices = prices[::-1]
                index = reversed_prices.index(upgrade_price)
                upgrade = self.find_element(By.ID, f"product{index}")
                time.sleep(0.1)
                upgrade.click()
                break

    # check if there is a boost available, if available, return boost
    def get_boosts(self):
        for _ in range(const.BOOSTS_TO_FIND):
            try:
                boost = self.find_element(By.ID, f"upgrade{const.UPGRADE_NUM}")
                return boost
            except:
                return False

    # click the boost if one was available from get_boosts
    def check_boost(self, boost) -> None:

        if boost != False:
            status = boost.get_attribute("class")
            if status == "crate upgrade enabled":
                print(cyan_format_text("boost enabled"))
                time.sleep(0.3)
                boost = self.find_element(By.ID, f"upgrade{const.UPGRADE_NUM}").click()
