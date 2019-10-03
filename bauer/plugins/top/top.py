import bauer.emoji as emo
import bauer.utils as utl
import math

from bauer.plugin import BauerPlugin
from telegram import ParseMode


class Top(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
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

        # ---- TIP toplist ----
        elif args[0] == "tip":

            # ---- Who gave the most ----
            sql = self.get_resource("top_tip_giver.sql")
            res = self.execute_sql(sql, plugin="tip")

            if not res["success"]:
                update.message.reply_text(
                    text=f"{emo.ERROR} {res['data']}",
                    parse_mode=ParseMode.MARKDOWN)
                return

            length = 0
            first = True
            msg = f"*Tip Toplist*\n\nWho gave the most:\n"

            for data in res["data"]:
                user = f"@{utl.esc_md(data[0])}"
                amount = f"{math.ceil(data[1] * 100) / 100:.2f}"

                if first:
                    first = False
                    length = len(amount)

                msg += f"`{amount:>{length}}` {user}\n"

            # ---- Who received the most ----
            msg += "\nWho received the most:\n"

            sql = self.get_resource("top_tip_taker.sql")
            res = self.execute_sql(sql, plugin="tip")

            if not res["success"]:
                update.message.reply_text(
                    text=f"{emo.ERROR} {res['data']}",
                    parse_mode=ParseMode.MARKDOWN)
                return

            length = 0
            first = True

            for data in res["data"]:
                user = f"@{utl.esc_md(data[0])}"
                amount = f"{math.ceil(data[1] * 100) / 100:.2f}"

                if first:
                    first = False
                    length = len(amount)

                msg += f"`{amount:>{length}}` {user}\n"

            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

        # ---- Everything else ----
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
