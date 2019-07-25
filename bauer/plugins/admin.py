import bauer.utils as utl
import bauer.emoji as emo

from telegram import ParseMode
from bauer.plugin import BauerPlugin
from bauer.config import ConfigManager as Cfg


class Admin(BauerPlugin):

    def get_handle(self):
        return "admin"

    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        args = [s.lower() for s in args]
        command = args[0].lower()

        # Execute raw SQL
        if command == "sql":
            if Cfg.get("database", "use_db"):
                args.pop(0)

                sql = " ".join(args)
                data = self.tgb.db.execute_sql(sql)

                if data["error"]:
                    msg = data["error"]
                elif data["result"]:
                    msg = '\n'.join(str(s) for s in data["result"])
                else:
                    msg = f"{emo.INFO} No data returned"

                update.message.reply_text(msg)
            else:
                update.message.reply_text(f"{emo.INFO} Database not enabled")

        # Change configuration
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
                Cfg.set(v, *args)
            except Exception as e:
                return self.handle_error(e, update)

            update.message.reply_text(f"{emo.CHECK} Config changed")

        # Manage plugins
        elif command == "plg":
            args.pop(0)

            try:
                # Add plugin
                if args[0].lower() == "add":
                    result = self.tgb.add_plugin(args[1])

                # Remove plugin
                elif args[0].lower() == "remove":
                    result = self.tgb.remove_plugin(args[1])

                # Wrong sub-command
                else:
                    update.message.reply_text(
                        text="Only `add` and `remove` are supported",
                        parse_mode=ParseMode.MARKDOWN)
                    return

                # Reply with message
                if result["success"]:
                    update.message.reply_text(f"{emo.CHECK} {result['msg']}")
                else:
                    update.message.reply_text(f"{emo.ERROR} {result['msg']}")
            except Exception as e:
                update.message.reply_text(text=f"{emo.ERROR} {e}")

        else:
            update.message.reply_text(
                text=f"Unknown command `{args[0]}`",
                parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_handle()} sql <statement>`\n" \
               f"`/{self.get_handle()} cfg <key> (<sub-key>) <value>`\n" \
               f"`/{self.get_handle()} plg add|remove <plugin name>`"
