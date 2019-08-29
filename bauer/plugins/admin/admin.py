import logging
import bauer.utils as utl
import bauer.emoji as emo

from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Admin(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        args = [s.lower() for s in args]
        command = args[0]

        # ---- Execute raw SQL ----
        if command == "sql":
            args.pop(0)

            plugin = args[0].lower()
            args.pop(0)

            sql = " ".join(args)
            res = self.execute_sql(sql, plugin=plugin)

            if res["success"]:
                if res["data"]:
                    msg = '\n'.join(str(s) for s in res["data"])
                else:
                    msg = f"{emo.INFO} No data returned"
            else:
                msg = f"{emo.ERROR} {res['data']}"

            update.message.reply_text(msg)

        # ---- Change configuration ----
        elif command == "cfg":
            args.pop(0)
            v = args[-1]
            v = v.lower()
            args.pop(-1)

            # Convert to boolean
            if v == "true" or v == "false":
                v = utl.str2bool(v)

            # Convert to integer
            elif v.isnumeric():
                v = int(v)

            # Convert to null
            elif v == "null" or v == "none":
                v = None

            try:
                self.cfg_set(v, *args, plugin=False)
            except Exception as e:
                logging.error(e)
                msg = f"{emo.ERROR} {e}"
                update.message.reply_text(msg)
                return

            update.message.reply_text(f"{emo.DONE} Config changed")

        # ---- Manage plugins ----
        elif command == "plg":
            args.pop(0)

            try:
                # Add plugin
                if args[0].lower() == "add":
                    res = self.add_plugin(args[1])

                # Remove plugin
                elif args[0].lower() == "remove":
                    res = self.remove_plugin(args[1])

                # Wrong sub-command
                else:
                    update.message.reply_text(
                        text="Only `add` and `remove` are supported",
                        parse_mode=ParseMode.MARKDOWN)
                    return

                # Reply with message
                if res["success"]:
                    update.message.reply_text(f"{emo.DONE} {res['msg']}")
                else:
                    update.message.reply_text(f"{emo.ERROR} {res['msg']}")
            except Exception as e:
                update.message.reply_text(text=f"{emo.ERROR} {e}")

        else:
            update.message.reply_text(
                text=f"Unknown command `{args[0]}`",
                parse_mode=ParseMode.MARKDOWN)
