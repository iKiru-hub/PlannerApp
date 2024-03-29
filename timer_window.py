
# make window size fixed
from kivy import Config
Config.set('graphics', 'resizable', False)

from kivy.core.window import Window
Window.size = (250, 200)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

from kivy.lang import Builder

import time
import sys
import logging

import cache_module

# cache module 
cache_module_obj = cache_module.CacheInterface()

# general logger
logger = logging.getLogger(f"TimerLogs")
logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")
stdout.setFormatter(fmt)
logger.addHandler(stdout)


class SimpleTimerSetting(Screen):

    def __init__(self, **kwargs):

        super(SimpleTimerSetting, self).__init__(**kwargs)

        self.duration = 0.0
        self.saved = False
        self.validity = False

        self._loaded_duration = 0.0

    def _load_cache(self):

        """
        load the cache
        """

        # retrieve time cache 
        present, timer_cache = cache_module_obj.get_timer_cache()

        if present:

            logger.debug("timer cache found")
            
            # go to Simple Timer Window
            logger.debug(f"dir start button: {self.ids}")

            # define timer data
            self._loaded_duration = timer_cache['duration']

            return 

        logger.debug("no timer cache found")

    def _load_duration(self):

        """
        load duration retrieved from cache
        """

        if self._loaded_duration != 0.0:

            self.timer_time.text = str(self._loaded_duration)

            logger.debug(f"loaded duration: {self._loaded_duration}")

    def on_enter(self, *args):


        # check if "display" is an attribute
        if hasattr(self, "display"):
            logger.debug("'on_enter': display attribute exists")
        else:
            logger.error("'on_enter': display attribute does not exist")

        logger.info("Simple Timer Setting Window entered")

        # load cache
        self._load_cache()

        # print window size
        logger.debug(f"window size: {Window.size}")
    
    def on_leave(self, *args):

        self.reset()
        
        logger.info("Simple Timer Setting Window left")

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
            
            logger.debug(f"valid timer time: {self.timer_time.text}")

        except ValueError:
            logger.error(f'"{self.timer_time.text}" is not an integer')

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

        logger.info(f"timer settings saved: {self.duration}")

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
            logger.debug("exit button pressed")

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

        logger.info("Simple Timer Window entered")
        
        # check if "dislay" is an attribute
        if not hasattr(self, "display"):
            logger.debug("'on_enter': display attribute not found")
        else:
            logger.debug("'on_enter': display attribute found")
        
        self._load_cache()

    def on_leave(self, *args):

        logger.info("Simple Timer Window left")

    def _load_cache(self):

        """
        load the interval

        Return
        ------
        None
        """

        # retrieve time cache 
        present, timer_cache = cache_module_obj.get_timer_cache()

        if not present:
            logger.error("timer cache not found")
            sys.exit("<timer aborted>")

        # delete cache
        #cache_module_obj.delete_timer_cache()
        # check if "dislay" is an attribute
        if not hasattr(self, "display"):
            logger.debug("'load duration': display attribute not found")
        else:
            logger.debug("'load duration': display attribute found")

        # define timer data
        duration = timer_cache['duration']
        ongoing = True  # <--------------------------- ugly
        self.tot_duration = duration * 60
        self.checkpoint = duration * 60
        self.current_time = [duration, 0]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        self.app = App.get_running_app()

        if ongoing:

            logger.debug("timer ongoing")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

            # change button name to pause
            # self.play_pause_icon.source = "media/pause_iconG.png"

        else:
            logger.debug("timer paused")

            # new state
            self.state = "paused"

            # change button name to pause
            # self.play_pause_icon.source = "media/play_iconG.png"

        logger.debug(
            "timer interval loaded: %s [%ss] %s",
            self.current_time,
            duration * 60,
            self.state,
        )

    def update(self):

        """ Update timer status """

        # finished + play button: start
        if self.state == "paused":

            logger.debug("timer started")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

            # change button name to pause
            # self.play_pause_icon.source = "media/pause_iconG.png"

        # running + pause button : pause
        elif self.state == "running":

            logger.debug("timer paused")

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

        logger.info(f"tracked: {self.duration} s")

    def close(self):

        """ Close timer """

        logger.info("quitting timer")

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


    def reset(self):

        """reset to the original values"""

        logger.info("resetting timer")

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
            logger.info("timer ticking")

        # pressed running -> stopped
        elif flag == "" and self.state == "running" and pressed:
            self.timer_image.source = r"media/Timer window/timer_go_stop.png"
            logger.info("pause button pressed")

        # stopped -> running
        elif flag == "" and self.state == "paused" and not pressed:
            self.timer_image.source = r"media/Timer window/timer_go.png"
            logger.info("timer stopped")

        # pressed stopped -> running
        elif flag == "" and self.state == "paused" and pressed:
            self.timer_image.source = r"media/Timer window/timer_nogo_play.png"
            logger.info("play button pressed")

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

        logger.info("Extra Simple Timer Window entered")

        self.app = App.get_running_app()

    def close(self):

        logger.info("Extra Simple Timer Window closed")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass


class WindowManager(ScreenManager):
    def on_resize(self):

        pass

kv_file = Builder.load_file("timer_window.kv")


class TimerApp(App):
    def build(self):
        return kv_file


if __name__ == "__main__":
    TimerApp().run()
    logger.info("Timer App closed")
    time.sleep(2)
