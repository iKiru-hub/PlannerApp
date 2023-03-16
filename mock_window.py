from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.lang import Builder

import time
import sys
import coloredlogs, logging

# general logger
general_logger = logging.getLogger(f"Timer")
general_logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")
stdout.setFormatter(fmt)
general_logger.addHandler(stdout)


class SimpleTimerSetting(Screen):

    def __init__(self, **kwargs):

        super(SimpleTimerSetting, self).__init__(**kwargs)

        self.duration = 0.0
        self.saved = False
        self.validity = False

    def on_enter(self, *args):

        general_logger.info("Simple Timer Setting Window entered")

        # check if "display" is an attribute
        if hasattr(self, "display"):
            general_logger.debug("'on_enter': display attribute exists")
        else:
            general_logger.error("'on_enter': display attribute does not exist")

    def on_leave(self, *args):
        
        general_logger.info("Simple Timer Setting Window left")

    def quit(self):

        """quit the app"""

        general_logger.info("Clock App closed")


class WindowManager(ScreenManager):
    def on_resize(self):

        pass

kv_file = Builder.load_file("mock_window.kv")

Window.size = (250, 200)


class TimerApp(App):
    def build(self):
        return kv_file


if __name__ == "__main__":
    TimerApp().run()
    general_logger.info("Timer App closed")
    time.sleep(2)
