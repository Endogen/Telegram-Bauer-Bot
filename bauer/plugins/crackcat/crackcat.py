import logging
import requests
import bauer.emoji as emo

from bauer.plugin import BauerPlugin


class Crackcat(BauerPlugin):

    URL = "http://crackcat.de"

    def __enter__(self):
        interval = self.config.get("interval")
        self.repeat(self.crackcat_job, interval)
        return self

    @BauerPlugin.threaded
    def crackcat_job(self, bot, job):
        logging.debug(f"Entering '{self.get_name()}'")

        response = requests.get(self.URL)

        if response.status_code != 200:
            code = str(response.status_code)
            plugin = self.get_name()
            logging.error(f"Plugin '{plugin}': Receiving status code: {code}")

            user_id = self.global_config.get("admin", "ids")[0]
            text = f"{emo.ALERT} Crackcat.de not accessible anymore!"
            bot.send_message(chat_id=user_id, text=text)

        logging.debug(f"Exiting '{self.get_name()}'")
