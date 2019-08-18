import bauer.emoji as emo

from bauer.plugin import BauerPlugin, Category
from telegram import ParseMode
from bauer.config import ConfigManager as Cfg


class Toplist(BauerPlugin):

    def get_handle(self):
        return "top"

    @BauerPlugin.threaded
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

        # --- RAIN top-list ----
        if args[0] == "rain":
            # TODO: Implement 'rain'
            update.message.reply_text(
                text="Not yet implemented",
                parse_mode=ParseMode.MARKDOWN)
            pass

        # ---- TIP top-list ----
        elif args[0] == "tip":
            sql = self.get_sql("top_tip")
            res = self.execute_sql(sql, db="tip")

            if not res["success"]:
                update.message.reply_text(
                    text=f"{emo.ERROR} {res['data']}",
                    parse_mode=ParseMode.MARKDOWN)
                return

            msg = str()
            for data in res["data"]:
                user = "{:>11}".format(data[0])
                msg += f"`{data[1]} {user}`\n"

            update.message.reply_text(
                text=f"*Tip Toplist*\n\n"
                     f"Who gave the most:\n"
                     f"{msg}",
                parse_mode=ParseMode.MARKDOWN)

        # ---- Everything else ----
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
