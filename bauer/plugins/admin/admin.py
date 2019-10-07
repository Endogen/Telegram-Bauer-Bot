import os
import logging
import bauer.utils as utl
import bauer.emoji as emo

from telegram import ParseMode
from bauer.config import ConfigManager
from bauer.plugin import BauerPlugin


class Admin(BauerPlugin):

    @BauerPlugin.owner
    @BauerPlugin.private
    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def execute(self, bot, update, args):
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        command = args[0].lower()
        args.pop(0)

        plugin = args[0].lower()
        args.pop(0)

        # ---- Execute raw SQL ----
        if command == "sql":
            db = args[0].lower()
            args.pop(0)

            sql = " ".join(args)
            res = self.execute_sql(sql, plugin=plugin, db_name=db)

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
            conf = args[0].lower()
            args.pop(0)

            get_set = args[0].lower()
            args.pop(0)

            # SET a config value
            if get_set == "set":
                # Get value for key
                value = args[-1].replace("__", " ")
                args.pop(-1)

                # Check value for boolean
                if value.lower() == "true" or value.lower() == "false":
                    value = utl.str2bool(value)

                # Check value for integer
                elif value.isnumeric():
                    value = int(value)

                # Check value for null
                elif value.lower() == "null" or value.lower() == "none":
                    value = None

                try:
                    if plugin == "-":
                        value = self.global_config.set(value, *args)
                    else:
                        cfg_file = f"{conf}.json"
                        plg_conf = self.get_cfg_path(plugin=plugin)
                        cfg_path = os.path.join(plg_conf, cfg_file)
                        ConfigManager(cfg_path).set(value, *args)
                except Exception as e:
                    logging.error(e)
                    msg = f"{emo.ERROR} {e}"
                    update.message.reply_text(msg)
                    return

                update.message.reply_text(f"{emo.DONE} Config changed")

            # GET a config value
            elif get_set == "get":
                try:
                    if plugin == "-":
                        value = self.global_config.get(*args)
                    else:
                        cfg_file = f"{conf}.json"
                        plg_conf = self.get_cfg_path(plugin=plugin)
                        cfg_path = os.path.join(plg_conf, cfg_file)
                        value = ConfigManager(cfg_path).get(*args)
                except Exception as e:
                    logging.error(e)
                    msg = f"{emo.ERROR} {e}"
                    update.message.reply_text(msg)
                    return

                update.message.reply_text(value)

            # Wrong syntax
            else:
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)

        # ---- Manage plugins ----
        elif command == "plg":
            try:
                # Start plugin
                if args[0].lower() == "add":
                    res = self.add_plugin(plugin)

                # Stop plugin
                elif args[0].lower() == "remove":
                    res = self.remove_plugin(plugin)

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
                text=f"Unknown command `{command}`",
                parse_mode=ParseMode.MARKDOWN)
