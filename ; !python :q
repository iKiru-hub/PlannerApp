from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.lang import Builder

import time
import sys
import coloredlogs, logging

import cache_module


# cache module 
cache_module_obj = cache_module.CacheInterface()

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

    def on_leave(self, *args):

        self.reset()
        
        general_logger.info("Simple Timer Setting Window left")

    def reset(self, *args):

        # reset
        self.duration = 0.0
        self.start_button.color = (0.1, 0.1, 0.1, 1)
        self.saved = False

    def check_inputs(self):

        """check if the inputs are valid"""

        # timer time
        try:
            _ = int(self.timer_time.text)
            self.validity = True
            self.start_button.color = (0.1, 0.9, 0.1, 1)

            # save data and build intervals
            self.save()
            
            general_logger.debug(f"valid timer time: {self.timer_time.text}")

        except ValueError:
            general_logger.error(f'"{self.timer_time.text}" is not an integer')

            self.timer_time.text = ""
            self.validity = False
            self.start_button.color = (0.9, 0.1, 0.1, 1)

    def save(self):

        """
        save and jump to the session

        Returns
        -------
        None
        """

        self.duration = int(self.timer_time.text)

        general_logger.info(f"timer settings saved: {self.duration}")

        self.saved = True

        # save cache
        cache_module_obj.save_timer_cache(timer_cache={"duration": self.duration})

        time.sleep(0.5)

    def get_duration(self):

        return self.duration

    def change_image(self, pressed=False):

        """
        change the image after pressing the exit button

        Parameters
        ----------
        pressed : bool, optional
            if the button is pressed, by default False
        """

        if pressed:
            self.timer_setting_image.source = (
                r"media/Timer window/timer_settings_return.png"
            )
            general_logger.debug("exit button pressed")

        else:
            self.timer_setting_image.source = r"media/Timer window/timer_settings.png"

    def quit(self):

        Window.size = (700, 500)
        self.timer_setting_image.source = r"media/Timer window/timer_settings.png"


class SimpleTimer(Screen):

    def __init__(self, **kwargs):
        super(SimpleTimer, self).__init__(**kwargs)

        self.tot_duration = 0
        self.duration = 0  # how long it has run so far
        self.state = "running"  # state: finished, running, paused
        self.start_time = 0.0  # time at which it started
        self.checkpoint = 0.0  # paused time

        self.current_time = [0, 0]

        self.job = 0
        self.app = ""

    def on_enter(self, *args):

        general_logger.info("Simple Timer Window entered")
        
        # check if "dislay" is an attribute
        if not hasattr(self, "display"):
            general_logger.debug("'on_enter': display attribute not found")
        else:
            general_logger.debug("'on_enter': display attribute found")
        
        self._load_duration()

    def on_leave(self, *args):

        general_logger.info("Simple Timer Window left")

    def _load_duration(self):

        """
        load the interval

        Return
        ------
        None
        """

        # retrieve time cache 
        present, timer_cache = cache_module_obj.get_timer_cache()

        if not present:
            general_logger.error("timer cache not found")
            sys.exit("<timer aborted>")

        # delete cache
        #cache_module_obj.delete_timer_cache()
        # check if "dislay" is an attribute
        if not hasattr(self, "display"):
            general_logger.debug("'load duration': display attribute not found")
        else:
            general_logger.debug("'load duration': display attribute found")

        # define timer data
        duration = timer_cache['duration']
        ongoing = True  # <--------------------------- ugly
        self.tot_duration = duration * 60
        self.checkpoint = duration * 60
        self.current_time = [duration, 0]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        self.app = App.get_running_app()

        if ongoing:

            general_logger.debug("timer ongoing")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

            # change button name to pause
            # self.play_pause_icon.source = "media/pause_iconG.png"

        else:
            general_logger.debug("timer paused")

            # new state
            self.state = "paused"

            # change button name to pause
            # self.play_pause_icon.source = "media/play_iconG.png"

        general_logger.debug(
            "timer interval loaded: %s [%ss] %s",
            self.current_time,
            duration * 60,
            self.state,
        )

    def update(self):

        """ Update timer status """

        # finished + play button: start
        if self.state == "paused":

            general_logger.debug("timer started")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

            # change button name to pause
            # self.play_pause_icon.source = "media/pause_iconG.png"

        # running + pause button : pause
        elif self.state == "running":

            general_logger.debug("timer paused")

            # stop clock
            self.job.cancel()

            # new state
            self.state = "paused"

            # checkpoint
            self.checkpoint = self.current_time[0] * 60 + self.current_time[1]

            # change button name to play
            # self.play_pause_icon.source = "media/play_iconG.png"

            # track interval run
            self.tracking()

    def ticking(self, *args):

        """ Update timer """

        elapsed = int(self.checkpoint - (time.time() - self.start_time))
        self.current_time[1] = int(elapsed % 60)
        self.current_time[0] = int(elapsed // 60)

        if elapsed <= 0:

            # cancel
            self.job.cancel()

            # record
            self.tracking()

            #
            self.display.text = "00:00"
            self.state = "finished"
            Clock.usleep(10000)

            self.close()
            return

        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

    def tracking(self):

        """ Track time """

        self.duration = int(time.time() - self.start_time)

        # control for absurd time difference, usually when the timer isn't event started
        if self.duration > 24 * 60 * 60:
            self.duration = 0

        general_logger.info(f"tracked: {self.duration} s")

    def close(self):

        """ Close timer """

        general_logger.info("quitting timer")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()

        # next

        self.app.root.current = "extra_simple_timer"
        self.app.root.transition.direction = "left"

        self.total_reset()

    def reset(self):

        """reset to the original values"""

        general_logger.info("resetting timer")

        # cancel
        self.job.cancel()

        Clock.usleep(1000)

        # reset values to original
        self.checkpoint = self.tot_duration
        self.current_time = [int(self.tot_duration // 60), int(self.tot_duration % 60)]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        # record
        if self.state == "running":
            self.tracking()

            # restart
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

    def quit(self):

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

    def change_image(self, flag="", pressed=False):

        """
        change the image of the timer window

        Parameters
        ----------
        flag : str
            the flag of the button pressed
        pressed : bool
            True if the button is pressed, False otherwise
        """

        #### edit 

        # running -> stopped
        if flag == "" and self.state == "running" and not pressed:
            self.timer_image.source = r"media/Timer window/timer_nogo.png"
            general_logger.info("timer ticking")

        # pressed running -> stopped
        elif flag == "" and self.state == "running" and pressed:
            self.timer_image.source = r"media/Timer window/timer_go_stop.png"
            general_logger.info("pause button pressed")

        # stopped -> running
        elif flag == "" and self.state == "paused" and not pressed:
            self.timer_image.source = r"media/Timer window/timer_go.png"
            general_logger.info("timer stopped")

        # pressed stopped -> running
        elif flag == "" and self.state == "paused" and pressed:
            self.timer_image.source = r"media/Timer window/timer_nogo_play.png"
            general_logger.info("play button pressed")

        # pressed running reset
        elif flag == "reset" and self.state == "running":
            self.timer_image.source = r"media/Timer window/timer_go_reset.png"
            

        # pressed running return
        elif flag == "return" and self.state == "running":
            self.timer_image.source = r"media/Timer window/timer_go_return.png"

        # pressed stopped reset
        elif flag == "reset" and self.state == "paused":
            self.timer_image.source = r"media/Timer window/timer_nogo_reset.png"

        # pressed stopped return
        elif flag == "return" and self.state == "paused":
            self.timer_image.source = r"media/Timer window/timer_nogo_return.png"

        # void
        elif flag == "void" and self.state == "running":
            self.timer_image.source = r"media/Timer window/timer_go.png"

        elif flag == "void" and self.state == "paused":
            self.timer_image.source = r"media/Timer window/timer_nogo.png"


class ExtraSimpleTimer(Screen):
    def __init__(self, **kwargs):
        super(ExtraSimpleTimer, self).__init__(**kwargs)

        self.app = ""

    def on_enter(self, *args):

        general_logger.info("Extra Simple Timer Window entered")

        self.app = App.get_running_app()

    def close(self):

        general_logger.info("Extra Simple Timer Window closed")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass


class WindowManager(ScreenManager):
    def on_resize(self):

        pass

kv_file = Builder.load_file("timer_window.kv")

Window.size = (250, 200)


class TimerApp(App):
    def build(self):
        return kv_file


if __name__ == "__main__":
    TimerApp().run()
