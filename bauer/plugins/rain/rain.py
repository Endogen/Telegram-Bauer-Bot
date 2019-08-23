from bauer.plugin import BauerPlugin, Category
from telegram import ParseMode


# TODO: Use 'split_msg' from utils here
class Rain(BauerPlugin):

    def __enter__(self):
        statement = self.get_resource("create_rain.sql")
        self.execute_sql(statement)
        return self

    def get_handle(self):
        return "rain"

    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # TODO: Implement

    def get_usage(self):
        return f"`/{self.get_handle()}`"

    def get_description(self):
        return "Rain BIS coins"

    def get_category(self):
        return Category.BISMUTH
