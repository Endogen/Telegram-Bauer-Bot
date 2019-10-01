from bauer.plugin import BauerPlugin
from telegram import ParseMode


# TODO: Use 'split_msg' from utils here
class Rain(BauerPlugin):

    def __enter__(self):
        if not self.table_exists("rain"):
            sql = self.get_resource("create_rain.sql")
            self.execute_sql(sql)
        return self

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        # TODO: Implement
