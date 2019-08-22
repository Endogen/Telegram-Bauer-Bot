from telegram import ParseMode
from bauer.plugin import BauerPlugin, Category


class About(BauerPlugin):

    ABOUT_FILE = "about.md"

    def get_handle(self):
        return "about"

    @BauerPlugin.threaded
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        update.message.reply_text(
            text=self.get_res(self.ABOUT_FILE),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return None

    def get_description(self):
        return "Information about bot"

    def get_category(self):
        return Category.BOT
