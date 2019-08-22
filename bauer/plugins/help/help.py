from telegram import ParseMode
from bauer.plugin import BauerPlugin, Category


class Help(BauerPlugin):

    def get_handle(self):
        return "help"

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        cat_dict = dict()
        for p in self.tg_bot.plugins:
            if p.get_category() and p.get_description():
                des = f"/{p.get_handle()} - {p.get_description()}\n"

                if p.get_category() not in cat_dict:
                    cat_dict[p.get_category()] = [des]
                else:
                    lst = cat_dict[p.get_category()]
                    lst.append(des)

        msg = "*Available commands*\n\n"
        for c in Category.get_categories():
            v = next(iter(c.values()))

            if v in cat_dict:
                msg += f"*{v}*\n"

                for cmd in sorted(cat_dict[v]):
                    msg += f"{cmd}"

                msg += "\n"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
