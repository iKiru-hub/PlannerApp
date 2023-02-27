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
general_logger = logging.getLogger(f"Clock")
general_logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")
stdout.setFormatter(fmt)
general_logger.addHandler(stdout)


class ClockWindow(Screen):

    def __init__(self, **kwargs):

        super(ClockWindow, self).__init__(**kwargs)

        self.start_time = time.time()
        self.job = 0
        self.app = App.get_running_app()

    def on_enter(self, *args):

        general_logger.info("ClockWindow entered")
        
        # check if "display" is an attribute
        if hasattr(self, "display"):
            general_logger.debug("'on_enter': display attribute exists")
        else:
            general_logger.error("'on_enter': display attribute does not exist")

        self.initialize()

    def on_leave(self, *args):

        general_logger.info("ClockWindow left")

    def initialize(self):

        """ Initializes the clock """
        
        # check if "display" is an attribute
        if hasattr(self, "display"):
            general_logger.debug("'initialize': display attribute exists")
        else:
            general_logger.error("'initialize': display attribute does not exist")

        self.start_time = time.time()
        self.job = Clock.schedule_interval(self.update_clock, 1)
        input()
        self.update_clock()
        general_logger.debug(f"current time is: {time.localtime()}")
        general_logger.debug(f"clock display: {self.display}")

    def update_clock(self, *args):

        """ Updates the clock """

        now = time.localtime()
        self.display.text = f"{now.tm_hour:02d}:{now.tm_min:02d}"

    def quit(self):

        general_logger.info("quitting")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass


class WindowManager(ScreenManager):
    def on_resize(self):

        pass


kv_file = Builder.load_file("clock_window.kv")

Window.size = (250, 200)

class ClockApp(App):
    def build(self):
        return kv_file

if __name__ == "__main__":
    ClockApp().run()
