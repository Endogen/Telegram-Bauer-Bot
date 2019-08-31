import bauer.emoji as emo

from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Toplist(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.usage()}",
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
            sql = self.get_resource("top_tip.sql")
            res = self.execute_sql(sql, plugin="tip")

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
                text=f"Usage:\n{self.usage()}",
                parse_mode=ParseMode.MARKDOWN)
