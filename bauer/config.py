import os
import json
import logging
import bauer.constants as con

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigManager(FileSystemEventHandler):

    _cfg_file = con.FILE_CFG
    _cfg = dict()

    _ignore = False
    _old = 0

    def __init__(self, config_file):
        self._cfg_file = config_file
        cfg_dir = os.path.dirname(self._cfg_file)

        # Watch for config file changes in realtime
        observer = Observer()
        observer.schedule(self, cfg_dir)
        observer.start()

    def on_modified(self, event):
        if event.src_path == self._cfg_file:
            stat = os.stat(event.src_path)
            new = stat.st_mtime

            # Workaround for watchdog bug
            # https://github.com/gorakhargosh/watchdog/issues/93
            if (new - self._old) > 0.5:
                if self._ignore:
                    self._ignore = False
                else:
                    self._read_cfg()

            self._old = new

    def _read_cfg(self):
        try:
            if os.path.isfile(self._cfg_file):
                with open(self._cfg_file) as config_file:
                    self._cfg = json.load(config_file)
        except Exception as e:
            err = f"Couldn't read '{self._cfg_file}'"
            logging.error(f"{repr(e)} - {err}")

    def _write_cfg(self):
        try:
            if not os.path.exists(os.path.dirname(self._cfg_file)):
                os.makedirs(os.path.dirname(self._cfg_file))
            with open(self._cfg_file, "w") as config_file:
                json.dump(self._cfg, config_file, indent=4)
        except Exception as e:
            err = f"Couldn't write '{self._cfg_file}'"
            logging.error(f"{repr(e)} - {err}")

    def get(self, *keys):
        if not self._cfg:
            self._read_cfg()

        value = self._cfg
        for key in keys:
            try:
                value = value[key]
            except Exception as e:
                err = f"Couldn't read '{key}' from {self._cfg_file}"
                logging.debug(f"{repr(e)} - {err}")
                return None

        return value if value is not None else None

    def set(self, value, *keys):
        if not self._cfg:
            self._read_cfg()

        tmp_cfg = self._cfg

        for key in keys[:-1]:
            try:
                tmp_cfg = tmp_cfg.setdefault(key, {})
                tmp_cfg[keys[-1]] = value

                self._ignore = True
                self._write_cfg()
            except Exception as e:
                err = f"Couldn't set '{key}' in {self._cfg_file}"
                logging.debug(f"{repr(e)} - {err}")

    def remove(self, keys):
        if not self._cfg:
            self._read_cfg()

        try:
            del self._cfg[keys[0]][keys[1]]
            self._ignore = True
            self._write_cfg()
        except KeyError as e:
            err = f"Can't remove key '{keys}'"
            logging.debug(f"{repr(e)} - {err}")
