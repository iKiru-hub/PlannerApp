from kivy.config import Config
Config.set('graphics', 'resizable', False)
from kivy.lang import Builder
from planner_lib import *


""" APP """

kv = Builder.load_file("planner.kv")

Window.size = (640, 498)


class PlannerApp(App):

    def build(self):
        return kv


if __name__ == "__main__":
    PlannerApp().run()


