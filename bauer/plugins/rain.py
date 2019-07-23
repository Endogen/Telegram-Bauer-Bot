from bauer.plugin import BauerPlugin, Category


class Rain(BauerPlugin):

    def get_handle(self):
        return "rain"

    @BauerPlugin.only_owner
    @BauerPlugin.send_typing
    def get_action(self, bot, update, args):
        # TODO: Implement
        pass

    def get_usage(self):
        return f"`/{self.get_handle()}`"

    def get_description(self):
        return "Rain BIS coins"

    def get_category(self):
        return Category.BISMUTH
