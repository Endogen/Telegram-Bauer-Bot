import os
import json
import logging
import bauer.constants as con

from argparse import ArgumentParser
from bauer.telegrambot import TelegramBot
from bauer.config import ConfigManager as Cfg
from logging.handlers import TimedRotatingFileHandler


class Bauer:

    def __init__(self):
        # Parse command line arguments
        self.args = self._parse_args()

        # Load config file
        Cfg(os.path.join(con.CFG_DIR, con.CFG_FILE))

        # Set up logging
        self._init_logger()

        # Create Telegram bot
        self.tg = TelegramBot(self._get_bot_token())

    # Parse arguments
    def _parse_args(self):
        desc = "Telegram bot for Bismuth (BIS) cryptocurrency"
        parser = ArgumentParser(description=desc)

        # Save logfile
        parser.add_argument(
            "--no-log",
            dest="savelog",
            action="store_false",
            help="don't save log-files",
            required=False,
            default=True)

        # Log level
        parser.add_argument(
            "-log",
            dest="loglevel",
            type=int,
            choices=[0, 10, 20, 30, 40, 50],
            help="disabled, debug, info, warning, error, critical",
            default=30,
            required=False)

        # Module log level
        parser.add_argument(
            "-mlog",
            dest="mloglevel",
            help="set log level for a module",
            default=None,
            required=False)

        # Bot token
        parser.add_argument(
            "-tkn",
            dest="token",
            help="set Telegram bot token",
            required=False,
            default=None)

        return parser.parse_args()

    # Configure logging
    def _init_logger(self):
        logger = logging.getLogger()
        logger.setLevel(self.args.loglevel)

        log_file = os.path.join(con.LOG_DIR, con.LOG_FILE)
        log_format = "[%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s()] %(message)s"

        # Log to console
        console_log = logging.StreamHandler()
        console_log.setFormatter(logging.Formatter(log_format))
        console_log.setLevel(self.args.loglevel)

        logger.addHandler(console_log)

        # Save logs if enabled
        if self.args.savelog:
            # Create 'log' directory if not present
            log_path = os.path.dirname(log_file)
            if not os.path.exists(log_path):
                os.makedirs(log_path)

            file_log = TimedRotatingFileHandler(
                log_file,
                when="H",
                encoding="utf-8")

            file_log.setFormatter(logging.Formatter(log_format))
            file_log.setLevel(self.args.loglevel)

            logger.addHandler(file_log)

        # Set log level for specified modules
        if self.args.mloglevel:
            for modlvl in self.args.mloglevel.split(","):
                module, loglvl = modlvl.split("=")
                logr = logging.getLogger(module)
                logr.setLevel(int(loglvl))

    # Read bot token from file
    def _get_bot_token(self):
        if self.args.token:
            return self.args.token

        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)

        try:
            if os.path.isfile(token_path):
                with open(token_path, 'r') as file:
                    return json.load(file)["telegram"]
            else:
                exit(f"ERROR: No token file '{con.TKN_FILE}' found at '{token_path}'")
        except KeyError as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
            exit("ERROR: Can't read bot token")

    def start(self):
        if Cfg.get("webhook", "use_webhook"):
            self.tg.bot_start_webhook()
        else:
            self.tg.bot_start_polling()

        self.tg.bot_idle()
