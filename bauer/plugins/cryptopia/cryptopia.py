import logging
import requests
import bauer.emoji as emo

from bauer.plugin import BauerPlugin
from bs4 import BeautifulSoup


class Cryptopia(BauerPlugin):

    RICHEST_URL = "http://bismuth.online/richest"
    ADDRESS = "8b447aa5845a2b6900589255b7d811a0a40db06b9133dcf9569cdfa0"
    AMOUNT = 5214229.9

    def __enter__(self):
        interval = self.config.get("interval")
        self.repeat(self.cryptopia_job, interval)
        return self

    @BauerPlugin.threaded
    def cryptopia_job(self, bot, job):
        logging.debug(f"Entering '{self.get_name()}'")

        response = requests.get(self.RICHEST_URL)

        if response.status_code != 200:
            code = str(response.status_code)
            plugin = self.get_name()
            logging.error(f"Plugin '{plugin}': Ending with status code: {code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        for table in soup.find_all(class_="table"):
            for tr in table.find_all("tr")[1:]:
                data = tr.find_all("td")

                address = data[0].get_text()
                amount = float(data[2].get_text())

                if address == self.ADDRESS:
                    if amount == self.AMOUNT:
                        break

                    user_id = self.global_config.get("admin", "ids", plugin=False)[0]
                    text = f"{emo.ALERT} Cryptopia BIS wallet amount changed!"
                    bot.send_message(chat_id=user_id, text=text)
                    logging.info(f"AMOUNT CHANGED!")
                    break

        logging.debug(f"Exiting '{self.get_name()}'")
