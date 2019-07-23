from bauer.plugin import BauerPlugin, Category


class Toplist(BauerPlugin):

    def get_handle(self):
        return "top"

    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        # TODO: Implement
        pass

    def get_usage(self):
        return f"`/{self.get_handle()}`"

    def get_description(self):
        return "Show toplist for /rain and /tip"

    def get_category(self):
        return Category.BISMUTH
