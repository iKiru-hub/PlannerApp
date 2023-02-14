from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.lang import Builder

import time
import sys

import cache_module


# cache module 
cache_module_obj = cache_module.CacheInterface()


class SimpleTimerSetting(Screen):

    def __init__(self, **kwargs):

        super(SimpleTimerSetting, self).__init__(**kwargs)

        self.duration = 0.0

        self.saved = False
        self.validity = False

    def on_enter(self, *args):

        print("\n--------------------- Simple Timer Setting ---------------------")

    def on_leave(self, *args):

        self.reset()

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

        except ValueError:
            print(f'\n!Error: "{self.timer_time.text}" is not an integer')

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

        print("\nsession settings saved:\n", self.duration)

        self.saved = True

        # save cache
        cache_module_obj.save_timer_cache(timer_cache={"duration": self.duration})

        time.sleep(0.5)

    def get_duration(self):

        return self.duration

    def change_image(self, pressed=False):

        if pressed:
            self.timer_setting_image.source = (
                r"media/Timer window/timer_settings_return.png"
            )

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

        print("\n--------- Focus Timer Window ---------")

        self._load_duration()

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
            print("\n!Error: timer cache not found")
            sys.exit("<timer aborted>")

        # delete cache
        #cache_module_obj.delete_timer_cache()

        # define timer data
        duration = timer_cache['duration']
        ongoing = True  # <--------------------------- ugly
        self.tot_duration = duration * 60
        self.checkpoint = duration * 60
        self.current_time = [duration, 0]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        self.app = App.get_running_app()

        if ongoing:

            print("\ntimer ongoing")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

            # change button name to pause
            # self.play_pause_icon.source = "media/pause_iconG.png"

        else:
            print("\nfocus waiting to start")

            # new state
            self.state = "paused"

            # change button name to pause
            # self.play_pause_icon.source = "media/play_iconG.png"

        print(
            "\n% timer interval loaded: ",
            self.current_time,
            f" [{duration*60}s] % ",
            self.state,
        )

    def update(self):

        # finished + play button: start
        if self.state == "paused":

            print("\nfocus #play")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

            # change button name to pause
            # self.play_pause_icon.source = "media/pause_iconG.png"

        # running + pause button : pause
        elif self.state == "running":

            print("\nfocus #pause")

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

        self.duration = int(time.time() - self.start_time)

        # control for absurd time difference, usually when the timer isn't event started
        if self.duration > 24 * 60 * 60:
            self.duration = 0

        print("tracked: ", self.duration, "s")

    def close(self):

        print("\ntimer #close")

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

        print("\nfocus #reset ", self.state)

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

        print("\ntimer #quit")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass


    def change_image(self, flag="", pressed=False):

        print("state ", self.state, " pressed: ", pressed)

        # running -> stopped
        if flag == "" and self.state == "running" and not pressed:
            self.timer_image.source = r"media/Timer window/timer_nogo.png"

        # pressed running -> stopped
        elif flag == "" and self.state == "running" and pressed:
            self.timer_image.source = r"media/Timer window/timer_go_stop.png"

        # stopped -> running
        elif flag == "" and self.state == "paused" and not pressed:
            self.timer_image.source = r"media/Timer window/timer_go.png"

        # pressed stopped -> running
        elif flag == "" and self.state == "paused" and pressed:
            self.timer_image.source = r"media/Timer window/timer_nogo_play.png"

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

        print("\n--------- Extra Simple Timer Window ---------")

        self.app = App.get_running_app()

    def close(self):

        print("\nsimple timer #close")

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
