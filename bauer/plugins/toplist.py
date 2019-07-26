import bauer.emoji as emo

from bauer.plugin import BauerPlugin, Category
from telegram import ParseMode
from bauer.config import ConfigManager as Cfg


class Toplist(BauerPlugin):

    def get_handle(self):
        return "top"

    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not Cfg.get("database", "use_db"):
            update.message.reply_text(
                text=f"{emo.INFO} *Database not enabled*\n"
                     f"Not possible to use `/{self.get_handle()} command`",
                parse_mode=ParseMode.MARKDOWN)
            return

        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        args = [s.lower() for s in args]

        if args == "rain":
            # TODO
            pass
        elif args == "tip":
            statement = self.tgb.db.get_sql("top_tip")
            result = self.tgb.db.execute_sql(statement)
            # TODO: Work with the result
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_handle()} rain|tip`"

    def get_description(self):
        return "Show toplist for /rain and /tip"

    def get_category(self):
        return Category.BISMUTH
