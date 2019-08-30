import collections
from collections import OrderedDict

from telegram import ParseMode
from bauer.plugin import BauerPlugin


class Help(BauerPlugin):

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        categories = OrderedDict()

        for p in self.plugins():
            if p.category() and p.description():
                des = f"/{p.handle()} - {p.description()}"

                if p.category() not in categories:
                    categories[p.category()] = [des]
                else:
                    categories[p.category()].append(des)

        msg = "*Available commands*\n\n"

        for category in sorted(categories):
            msg += f"*{category}*\n"

            for cmd in sorted(categories[category]):
                msg += f"{cmd}\n"

            msg += "\n"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
