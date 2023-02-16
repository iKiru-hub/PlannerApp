import warnings

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.lang import Builder

from numpy import array, exp
import time
import datetime
import sys
import os
import logging

# app utils 
import cache_module

# set current working directory
os.chdir(cache_module.APP_PATH)


""" SETTINGS """

# constants
FOCUSED_TIME = 30
REST_TIME = 5
RANK_WEIGHTS = (1, 0)
IS_DEADLINE = False

# cache module 
cache_module_obj = cache_module.CacheInterface()

# general logger
general_logger = logging.getLogger(f"General")
general_logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")
stdout.setFormatter(fmt)
general_logger.addHandler(stdout)


""" JOBS """


class NewJob(Screen):

    """
    Window that prompts the settings for a new job in Schedule Window
    """

    def __init__(self, **kwargs):

        super(NewJob, self).__init__(**kwargs)

        self.data = {"validity": False}
        self.original = {}
        self.deadline_values = 0

        self.app = ""

        # logger
        self.logger = logging.getLogger(f"NewJob")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

    def on_enter(self, *args):

        self.logger.info("NewJob Window entered")

    def on_leave(self, *args):

        self.reset()
        self.logger.info("NewJob Window left")

    def load_data(self, data: dict, title: str):

        """
        load info about the new task to create
        
        Parameters
        ----------
        data : dict 
        title : str 

        Returns
        -------
        None
        """
        
        self.app = App.get_running_app()

        self.logger.debug(f"NewJob Window loaded with data: {data}")

        self.data = data
        self.original = data
        self.original["validity"] = True
        self.deadline_values = (
            int(data["deadline"] // 60 // 60),
            int(data["deadline"] // 60 % 60),
        )

        self.job_name.text = data["name"]
        self.priority.text = str(data["priority"])
        self.title.text = title
        self.hours.text = str(int(self.deadline_values[0]))
        self.min.text = str(int(self.deadline_values[1]))

        # set duration
        if "duration" in list(self.data.keys()):
            self.duration.text = str(self.data["duration"])
            self.logger.debug(f"duration found in data: {self.data['duration']}")
        else:
            self.logger.warning("duration not found in data")
            self.duration.text = "-"

        # set type
        self.set_job_type(jobtype=data["type"])

    def check(self):

        """
        check it the proposed task design is valid

        Returns
        -------
        None
        """

        self.data["name"] = self.job_name.text

        triple_check = 0

        # check priority
        try:
            self.data["priority"] = int(self.priority.text)

            # one check
            triple_check += 1

        except ValueError:
            self.logger.error(f'"{self.priority.text}" is an invalid priority')
            self.priority.text = ""
            self.data["priority"] = 0

        # check duration | relevant of for task jobs
        if self.data["type"] == "task":
            try:
                self.data["duration"] = int(self.duration.text)

                # second check
                triple_check += 1

            except ValueError:
                self.logger.error(f'"{self.duration.text}" is an invalid duration')
                self.duration.text = ""
                self.data["duration"] = 0

        # check deadline
        try:
            self.data["deadline"] = (
                int(self.hours.text) * 60 * 60 + int(self.min.text) * 60
            )

            # third
            triple_check += 1

        except ValueError:
            self.logger.error(f"{self.hours.text}h {self.min.text}m are an invalid deadline")
            self.hours.text = ""
            self.min.text = ""
            self.data["deadline"] = 0

        # grant validity
        if triple_check == (2 + 1 * (self.data["type"] == "task")):

            self.data["validity"] = True
            self.logger.debug(f"NewJob Window data is valid: {self.data}")

        else:

            self.data["validity"] = False

    def clear(self):

        """
        clear the data of the task

        Returns
        -------
        None
        """

        self.job_name.text = "give-me-a-name"
        self.priority.text = "0"
        self.hours.text = "0"
        self.min.text = "0"
        self.duration.text = "0"

        self.data = {
            "name": self.job_name.text,
            "priority": 0,
            "duration": 0,
            "deadline": (0, 0),
            "type": "task",
            "validity": False,
        }

        # buttons
        self.type_task.color = (0.3, 0.8, 0.3, 1)
        self.type_project.color = (1, 1, 1, 1)

        self.logger.info('NewJob Window data cleared')

    def submit(self):

        """
        if the user settings are valid, it returned to Schedule Window

        Retuns
        ------
        None
        """

        # valid task design
        if self.data["validity"]:

            print("submitting ", self.data)

            # next
            self.app.root.current = "schedule_window"
            self.app.root.transition.direction = "right"
            self.app.root.current_screen.jobs_manager.save_job(new_job_data=self.data)

            # reset
            self.reset()

            self.logger.info("NewJob Window data submitted")
            return

    def returning(self):

        """
        save the job settings

        Returns
        -------
        None
        """

        # next
        self.app.root.current = "schedule_window"
        self.app.root.transition.direction = "right"
        self.app.root.current_screen.jobs_manager.save_job(new_job_data=self.original)

        # reset
        self.reset()

    def reset(self):

        """
        reset the job settings 

        Returns
        -------
        None
        """

        self.data = {
            "name": self.job_name.text,
            "priority": 0,
            "duration": 0,
            "deadline": (0, 0),
            "type": "task",
            "validity": False,
        }
        self.deadline_values = 0

        self.job_name.text = ""
        self.priority.text = ""
        self.title.text = ""
        self.hours.text = "0"
        self.min.text = "0"
        self.duration.text = ""

        # buttons
        self.type_task.color = (0.3, 0.8, 0.3, 1)
        self.type_project.color = (1, 1, 1, 1)

        self.newjob_window_image.source = r"media/NewJob window/newjob_window.png"

    def set_job_type(self, jobtype="task"):

        """
        change color of the job type buttons

        Parameters
        ----------
        jobtype : str 
            type of job to be set, allowed are "task" and "project",
            default "project"

        Returns
        -------
        None
        """

        if jobtype == "task":

            self.data["type"] = "task"
            self.type_task.color = (0.3, 0.8, 0.3, 1)
            self.type_project.color = (1, 1, 1, 1)
            self.duration.text = "10"

            # delete eventual project-related lists
            if "completed_minitasks" in list(self.data.keys()):
                del self.data["completed_minitasks"]
                del self.data["current_minitasks"]

        elif jobtype == "project":

            self.data["type"] = "project"
            self.type_task.color = (1, 1, 1, 1)
            self.type_project.color = (0.3, 0.8, 0.3, 1)
            self.duration.text = "-"

            # possibly, add project-related lists
            if "current_minitasks" in list(self.data.keys()):
                return

            self.data["current_minitasks"] = []
            self.data["completed_minitasks"] = 0

    def change_image(self, flag=" "):

        """
        change the main image to mark a button press/transition

        Parameters
        ----------
        flag : str 
            query of the new image, default " "

        Returns
        -------
        None
        """

        if flag == " ":
            self.newjob_window_image.source = r"media/NewJob window/newjob_window.png"

        elif flag == "check":
            self.newjob_window_image.source = (
                r"media/NewJob window/newjob_window_check.png"
            )

        elif flag == "clear":
            self.newjob_window_image.source = (
                r"media/NewJob window/newjob_window_clear.png"
            )

        elif flag == "submit":
            self.newjob_window_image.source = (
                r"media/NewJob window/newjob_window_submit.png"
            )

        elif flag == "return":
            self.newjob_window_image.source = (
                r"media/NewJob window/newjob_window_return.png"
            )

        else:
            warnings.warn(f"flag {flag} does not correspond to any newjob_window key")


class JobsManager(FloatLayout):

    """
    Object that manage the available jobs and update their states
    """

    def __init__(self, **kwargs):

        super(JobsManager, self).__init__(**kwargs)

        self.current_jobs = []

        self.completed_jobs = 0

        self.focus_package = {}

        self.refresh_routine = Clock.schedule_interval(self.refresh, 5)

        self.app = ""

        # rank weights
        self.rank_weights = (0.5, 0.5)

        # storage
        self.cache = cache_module_obj

        self.refresh()

        # logging
        self.logger = logging.getLogger("JobsManager")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

    def add_job(self, data=None, title="New Task"):

        """handle the addition of a new task"""

        if data is None:

            data = {
                "name": f"job {len(self.current_jobs)+1}",
                "priority": "1",
                "deadline": 7200,
                "duration": 120,
                "type": "task",
                "validity": False,
            }

        self.app.root.current = "new_job_window"
        self.app.root.current_screen.load_data(data=data, title=title)
        self.app.root.transition.direction = "left"

        self.logger.info(f"adding new job '{title}'")

    def save_job(self, new_job_data: dict):

        """handle the saving of a new task

        Parameters
        ----------
        new_job_data : dict
            dictionary containing the data of the new job

        Returns
        -------
        None
        """

        self.logger.info(f"adding new job")

        # task job
        if new_job_data["type"] == "task":

            new_task_instance = TaskObject(y_pos=0.0, data=new_job_data)
            self.current_jobs += [new_task_instance]

            self.logger.info(f"+new task added")

        # project job
        elif new_job_data["type"] == "project":

            new_task_instance = ProjectObject(y_pos=0.0, data=new_job_data)
            self.current_jobs += [new_task_instance]

            self.logger.info(f"+new project added")

        # update ranking
        self.refresh()

    def edit_job(self, rank: int):

        """handle the edition of a task

        Parameters
        ----------
        rank : int
            rank of the task to edit

        Returns
        -------
        None
        """

        self.logger.info(f"editing job, {rank=}")

        # get task
        job = self.current_jobs[rank]

        # remove from current
        del self.current_jobs[rank]

        # edit copy
        self.add_job(data=job.data, title=f"Editing <{job.name}>")

    def compute_scores(self):

        """
        update of the scores of each available job 

        CURRENTLY : no actual update, all job keep their priority as it was initially set

        Returns
        -------
        None
        """

        # get priorities list
        priorities = [int(job.priority) for job in self.current_jobs]
        #exp_sum = sum([exp(x) for x in priorities])

        # define score #
        # sort by deadline from small to large
        if IS_DEADLINE:
            self.current_jobs.sort(key=lambda u: u.deadline, reverse=True)

        scored = []
        for i, job in enumerate(self.current_jobs):
            # print('computing ', job.type)
            if job.type == "finished task" or job.type == "finished project":
                scored += [job]
                continue

            # relative priority
            if len(priorities) == 1:
                new_priority = 10
            else:
                try:
                    #new_priority = (
                    #    10
                    #    * (int(job.priority) - min(priorities))
                    #    / (max(priorities) - min(priorities))
                    #)
                    #new_priority = round(exp(job.priority) / exp_sum, 2)
                    new_priority = job.priority
                except ZeroDivisionError:
                    # print('\n--same priorities: ', priorities)
                    #new_priority = int(sum(priorities) / len(priorities))
                    raise ValueError('priority not computable, ZeroDivision')

            # relative deadline | considered only if DEADLINE is enabled [IS_DEADLINE]
            #relative_deadline = IS_DEADLINE * 10 * (i + 1) / len(self.current_jobs)

            # update priority
            job.update_priority(priority=new_priority)

            # score
            #value = (RANK_WEIGHTS[0] * new_priority + RANK_WEIGHTS[1] * relative_deadline) / (RANK_WEIGHTS[0] + RANK_WEIGHTS[1])
            # print(f'task {task.name} value: {value} [{new_priority}, {relative_deadline}]')
            job.set_score(value=round(new_priority))
            scored += [job]

        #
        self.current_jobs = scored
        self.current_jobs.sort(key=lambda u: u.value, reverse=True)

    def delete_job(self, rank: int):

        """handle the deletion of an old task

        Parameters
        ----------
        rank : int
            rank of the task to delete

        Returns
        -------
        None
        """

        self.logger.info(f"deleting job, {rank=}")

        del self.current_jobs[rank]

        self.refresh()

    def completed_job(self, rank: int):

        """definition of a "completed task" and substitution of the old task

        Parameters
        ----------
        rank : int
            rank of the task to complete

        Returns
        -------
        None
        """

        self.completed_jobs += 1

        # get completed job
        job = self.current_jobs[rank]

        self.logger.info(f"turning a <{job.type}> into a <finished {job.type}>")

        # define record
        full_record = {}
        full_record["name"] = job.data["name"]
        full_record["type"] = f"finished {job.type}"
        full_record["rank"] = job.data["rank"]
        full_record["priority"] = job.data["priority"]
        full_record["deadline"] = job.data["deadline"]
        full_record["creation"] = job.data["creation"]
        full_record["next_window"] = job.data["next_window"]
        full_record["done"] = True

        # create new finished job
        if job.type == "task":

            # record from the focused session
            full_record["duration"] = job.data["duration"]
            full_record["tot_focus"] = job.data["tot_focus"]
            full_record["tot_rest"] = job.data["tot_rest"]
            full_record["tot_idle"] = job.data["tot_idle"]

            finished_job = FinishedTask(
                y_pos=job.y_pos, priority=-1 * (self.completed_jobs + 1)
            )

        elif job.type == "project":

            full_record["current_minitasks"] = job.data["current_minitasks"]
            full_record["completed_minitasks"] = job.data["completed_minitasks"]

            finished_job = FinishedProject(
                y_pos=job.y_pos, priority=-1 * (self.completed_jobs + 1)
            )

        else:
            raise TypeError(f'type "{job.type}" not recognized')

        # update the finished task instance
        finished_job.set_record(record=full_record)  # records about the task timers

        # delete old instance
        del self.current_jobs[rank]
        self.current_jobs += [finished_job]

        self.refresh()

    def unfinish_project(self, rank: int, updated_data: dict):

        """make a finished project an ongoing project again

        Parameters
        ----------
        rank : int
            rank of the project to unfinish
        updated_data : dict
            data to update

        Returns
        -------
        None
        """

        self.logger.info(f"unfinishing project, {rank=}")

        # get job
        job = self.current_jobs[rank]

        # new project
        project = ProjectObject(
            y_pos=0,
            data={
                "name": job.data["name"],
                "priority": job.data["priority"],
                "duration": 0,
                "deadline": job.data["deadline"],
                "type": "project",
                "current_minitasks": updated_data["current_minitasks"],
                "completed_minitasks": updated_data["completed_minitasks"],
                "validity": True,
            },
        )

        # update project data
        project.data["rank"] = job.data["rank"]
        project.data["done"] = False

        # update
        del self.current_jobs[rank]
        self.current_jobs += [project]

        self.refresh()

    def update_focus_task(self, focus_package: dict):

        """update task from session window

        Parameters
        ----------
        focus_package : dict
            data from the session window

        Returns
        -------
        None
        """

        self.logger.debug(f"updating focus task, package: {focus_package=}")

        job = self.current_jobs[focus_package["rank"]]

        # dont process a finished task
        if job.type == "finished task":
            return

        # wrong job
        if job.type != "task":
            raise TypeError(
                f"trying to update a <{job.type}> with task data, wrong rank"
            )

        # right job
        job.data["tot_focus"] = focus_package["tot_focus"]
        job.data["tot_rest"] = focus_package["tot_rest"]
        job.data["tot_idle"] = focus_package["tot_idle"]
        job.data["done"] = focus_package["done"]

        # check if the task was completed
        if focus_package["done"]:
            self.completed_job(rank=focus_package["rank"])

        self.refresh()

    def update_project(self, updated_data: dict):

        """update project from project window

        Parameters
        ----------
        updated_data : dict
            data from the project window

        Returns
        -------
        None
        """

        self.logger.debug(f"updating project, updated_data: {updated_data=}")

        job = self.current_jobs[updated_data["rank"]]

        # dont process a finished project
        if job.type == "finished project" and updated_data["done"]:
            return

        # unfinish a project
        elif job.type == "finished project" and not updated_data["done"]:
            self.unfinish_project(rank=updated_data["rank"], updated_data=updated_data)
            return

        # wrong job
        elif job.type != "project":
            raise TypeError(
                f'trying to update a <{job.type}> with project data, wrong rank [{job.rank}] | update: {updated_data["done"]}'
            )

        # right job
        job.data["current_minitasks"] = updated_data["current_minitasks"]
        job.data["completed_minitasks"] = updated_data["completed_minitasks"]
        job.data["rank"] = updated_data["rank"]
        job.data["done"] = updated_data["done"]

        # update
        del self.current_jobs[updated_data["rank"]]
        self.current_jobs += [job]

        # check if the project was completed:
        if updated_data["done"]:
            self.completed_job(rank=-1)
            return

        self.refresh()

    def refresh(self, *args):

        # print('\n -- refreshing --')
        self.clear_widgets()
        # self.current_tasks.sort(key=lambda u: u.priority, reverse=True)
        self.compute_scores()

        newly_ordered = []
        for i, job in enumerate(self.current_jobs):

            job.y_pos = 0.9 - i * 0.1
            job.set_rank(rank=i)
            job.update_position()
            # print(f'job {job.name} [{job.type}]: score {job.value}, rank {job.rank}')

            newly_ordered += [job]
            self.add_widget(job)

        self.current_jobs = newly_ordered

    def load_pending(self):

        """load previous pending tasks"""

        global FOCUSED_TIME
        global REST_TIME

        self.logger.debug("loading pending jobs")

        # retrieve
        is_available, saved_objects = self.cache.retrieve_objects()

        if not is_available:
            self.logger.debug("no saved pending tasks")
            return

        # update
        for name, obj in saved_objects.items():
            if name == "settings":
                FOCUSED_TIME = obj["FOCUSED_TIME"]
                REST_TIME = obj["REST_TIME"]
                continue

            self.save_job(new_job_data=obj)

        self.logger.info(f"loaded {len(saved_objects)-1} pending jobs")
        self.logger.debug(f"loaded settings: FOCUSED_TIME={FOCUSED_TIME} REST_TIME={REST_TIME}")

    def save_pending(self):

        """save the pending tasks"""

        ongoing = []
        for job in self.current_jobs:

            # ignore finished tasks
            if job.type != "task" and job.type != "project":
                continue

            ongoing += [job.data]

            self.logger.debug(f"saved job: {job.data}")

        # save
        settings = {"FOCUSED_TIME": FOCUSED_TIME, "REST_TIME": REST_TIME}

        self.logger.debug(f"saving settings: {settings=}")
        self.cache.save_pending_objects(objects=ongoing, settings=settings)


""" TASKS """


class TaskObject(FloatLayout):

    """
    new task object, with buttons
    """

    def __init__(self, y_pos: float, data: dict, **kwargs):
        super(TaskObject, self).__init__(**kwargs)

        # data
        self.name = data["name"]
        self.priority = data["priority"]
        self.duration = data["duration"]
        self.type = data["type"]
        self.deadline = data["deadline"]
        self.deadline_str = self.deadline

        self.rank = 0
        self.value = 0

        self.intervals = self.provide_focus_data()["intervals"]

        self.state = "pending"

        # set creation
        self.data = {
            "name": self.name,
            "type": self.type,
            "rank": self.rank,
            "deadline": self.deadline,
            "priority": self.priority,
            "next_window": "schedule_window",
            "creation": time.time(),
            "done": False,
            "duration": self.duration,
            "tot_focus": 0,
            "tot_rest": 0,
            "tot_idle": 0,
        }

        # labels
        self.label.text = self.name
        self.score.text = str(self.value)
        self.status.text = "pending"
        if IS_DEADLINE:
            self.deadline_clock.text = ""

        # location
        self.y_pos = y_pos
        self.pos_hint = {"x": 0.0, "top": y_pos}

        self.update_position()

        # logger
        self.logger = logging.getLogger(f"Task-{self.name}")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

        self.logger.info(f"created task")

    def set_score(self, value: float):

        self.value = value
        self.score.text = str(self.value)

    def get_icons_position(self):

        return {"x": 0.85, "top": self.pos_hint["top"]}

    def update_priority(self, priority: int):

        self.priority = priority
        self.data["priority"] = priority

    def update_position(self):

        # update position
        self.pos_hint = {"x": 0.0, "top": self.y_pos}
        self.rank_pos.text = str(self.rank)

        # time from creation
        elapsed = time.time() - self.data["creation"]
        timer = self.deadline - elapsed

        # check #
        # beyond deadline
        if elapsed >= self.deadline and IS_DEADLINE:
            self.deadline_clock.text = "0h 0m"

            self.label.color = (0.8, 0.2, 0.2, 1)
            self.status.color = (0.8, 0.2, 0.2, 1)
            self.score.color = (0.8, 0.2, 0.2, 1)
            self.deadline_clock.color = (0.8, 0.2, 0.2, 1)
            return

        # going
        if IS_DEADLINE:
            self.deadline_clock.text = f"{timer // 3600 // 24:.0f}d {timer // 3600 % 25:.0f}h {timer // 60 % 60:.0f}m"

    def provide_focus_data(self):

        """
        compute the intervals as focus-rest-focus-rest... from the total task duration
        :return: list
        """

        # base focus length = FOCUSED_TIME, rest = REST_TIME
        nb_focus = [FOCUSED_TIME] * (self.duration // FOCUSED_TIME) + [
            self.duration % FOCUSED_TIME
        ]
        return {
            "intervals": list(array([[x] + [REST_TIME] for x in nb_focus]).reshape(-1))[
                :-1
            ],
            "rank": self.rank,
            "type": self.type,
            "next_window": "schedule_window",
        }

    def set_rank(self, rank: int):

        """
        set the rank of the task

        Parameters
        ----------
        rank : int
        """

        self.rank = rank

    def start_task(self):

        self.logger.info(f"starting task")

    def edit_task(self):

        self.logger.info(f"editing task")

    def change_image(self, flag=" "):

        """
        change the image of the task object

        Parameters
        ----------
        flag : str
            " " = default
        """

        if flag == " ":
            self.job_icons_image.source = r"media/Job obj/job_icons.png"

        elif flag == "play":
            self.job_icons_image.source = r"media/Job obj/job_icons_play.png"
            self.logger.info("play button pressed")

        elif flag == "delete":
            self.job_icons_image.source = r"media/Job obj/job_icons_delete.png"
            self.logger.info("delete button pressed")

        elif flag == "done":
            self.job_icons_image.source = r"media/Job obj/job_icons_done.png"
            self.logger.info("done button pressed")

        elif flag == "edit":
            self.job_icons_image.source = r"media/Job obj/job_icons_edit.png"
            self.logger.info("edit button pressed")


class FinishedTask(FloatLayout):

    """
    new task object, with buttons
    """

    def __init__(self, y_pos: float, priority: int, **kwargs):
        super(FinishedTask, self).__init__(**kwargs)

        # data
        self.name = ""
        self.data = {}
        self.factual_priority = 0
        self.priority = priority
        self.rank = 0
        self.value = 0
        self.deadline = 0  # fictional

        self.type = "finished task"

        # labels
        if IS_DEADLINE:
            self.deadline_clock.text = ""
        self.label.text = self.name
        self.score.text = str(self.factual_priority)
        self.status.text = "completed"

        # location
        self.y_pos = y_pos
        self.pos_hint = {"x": 0.0, "top": y_pos}

        general_logger.info(f"created finished task")

    def set_rank(self, rank: int):

        """
        set the rank of the task

        Parameters
        ----------
        rank : int
        """

        self.rank = rank

    def update_position(self):

        """
        update the position of the task
        """

        self.pos_hint = {"x": 0.0, "top": self.y_pos}
        self.rank_pos.text = str(self.rank)

    def update_priority(self, priority: int):

        """
        update the priority of the task

        Parameters
        ----------
        priority : int
            priority of the task
        """

        self.priority = priority

    def set_score(self, value: float):

        """
        set the score of the task

        Parameters
        ----------
        value : float
            score of the task
        """

        self.value = value
        self.score.text = str(self.value)

    def set_record(self, record: dict):

        """
        set the record of the task

        Parameters
        ----------
        record : dict
            record of the task
        """

        self.data = record

        # record
        self.name = record["name"]
        self.type = record["type"]
        self.factual_priority = record["priority"]

        # update description
        if IS_DEADLINE:
            self.deadline_clock.text = time.strftime(
                "%H:%M:%S", time.localtime(record["creation"])
            )
        self.label.text = self.name

        general_logger.info(f"finished task '{self.name}' setting a record")

    def change_image(self, flag=" "):

        """
        change the image of the task object

        Parameters
        ----------
        flag : str
            " " = default
        """

        if flag == " ":
            self.job_icons_image.source = r"media/Finished obj/finished_task.png"

        elif flag == "results":
            self.job_icons_image.source = (
                r"media/Finished obj/finished_task_results.png"
            )
            general_logger.info(f"finished task '{self.name}' result button pressed")

        elif flag == "delete":
            self.job_icons_image.source = r"media/Finished obj/finished_task_delete.png"
            general_logger.info(f"finished task '{self.name}' delete button pressed")


""" PROJECTS """


class ProjectWindow(Screen):

    def on_enter(self, *args):

        general_logger.info("ProjectWindow entered")

        self.projects_manager.app = App.get_running_app()

    def on_leave(self, *args):

        general_logger.info("ProjectWindow left")

        pass


class ProjectManager(FloatLayout):

    def __init__(self, **kwargs):

        super(ProjectManager, self).__init__(**kwargs)

        self.name = ""

        self.current_minitasks = []

        self.completed_minitasks = 0
        self.project_rank = 0
        self.done = False

        self.app = ""

        self.updated = False

        # logger
        self.logger = logging.getLogger(f"ProjectManager")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)


    def load_project(self, project_data: dict):

        """load data of the given project

        Parameters
        ----------
        project_data : dict
            the project data, as a dict

        Returns
        -------
        None
        """

        self.name = project_data["name"]
        self.completed_minitasks = project_data["completed_minitasks"]
        self.project_rank = project_data["rank"]
        self.done = project_data["done"]
        self.current_minitasks = []

        # update the minitasks list
        for minijob_data in project_data["current_minitasks"]:
            self.save_mini_task(new_mini_task_data=minijob_data)

        self.refresh()

        self.logger.info(f"loaded {self.name} rank {self.project_rank}")

    def return_project_data(self):

        """return the project data, possibly ready to be saved as json

        Returns
        -------
        dict : the project data
        """

        # every minitask as dict data
        current_minitasks_dict = [minitask.data for minitask in self.current_minitasks]

        data = {
            "current_minitasks": current_minitasks_dict,
            "completed_minitasks": self.completed_minitasks,
            "rank": self.project_rank,
            "done": self.done,
        }

        self.logger.info(f"returning {self.name}, rank {self.project_rank}, done {self.done}")

        return data

    def add_minitask(self, data=None, title="New mini-Task"):

        """handle the addition of a new task

        Parameters
        ----------
        data : dict, optional
            the data of the new task, by default None
        title : str, optional
            the title of the new task, by default "New mini-Task"

        Returns
        -------
        None
        """

        self.logger.info(f"adding minitask '{title}'")

        if data is None:

            data = {
                "name": f"mini-task-{len(self.current_minitasks)+1}",
                "duration": 30,
                "type": "minitask",
                "rank": str(len(self.current_minitasks)),
                "validity": False,
            }

        self.app.root.current = "new_mini_task_window"
        self.app.root.transition.direction = "left"
        self.app.root.current_screen.load_data(data=data, title=title)

    def save_mini_task(self, new_mini_task_data: dict):

        """
        save the new minitask data

        Parameters
        ----------
        new_mini_task_data : dict
            the new minitask data

        Returns
        -------
        None
        """

        self.logger.info(f"adding minitask")

        rank = new_mini_task_data["rank"]

        # new minitask
        if new_mini_task_data["type"] == "minitask":

            mini_task_instance = MiniTask(y_pos=0.0, data=new_mini_task_data)

        # new finished minitask
        elif new_mini_task_data["type"] == "finished minitask":

            mini_task_instance = FinishedMiniTask(
                y_pos=0.0, rank=new_mini_task_data["rank"]
            )

            # update the finished task instance
            mini_task_instance.set_record(
                record=new_mini_task_data
            )  # records about the task timers

        else:
            raise TypeError(f'type <{new_mini_task_data["type"]}> invalid')

        # place at the selected rank and push down the task previous at the selected rank
        new_list = (
            self.current_minitasks[:rank]
            + [mini_task_instance]
            + self.current_minitasks[rank:]
        )

        # save mini task
        self.current_minitasks = new_list

        self.updated = True
        self.refresh(sort=False)

    def edit_minitask(self, rank: int):

        """edit minitask with the provided rank

        Parameters
        ----------
        rank : int
            the rank of the minitask to edit

        Returns
        -------
        None
        """

        # get task
        self.logger.info(f"editing minitask '{minitask.name}' - total minitasks {len(self.current_minitasks)}")
        minitask = self.current_minitasks[rank]

        # remove from current
        del self.current_minitasks[rank]

        # edit copy
        self.add_minitask(data=minitask.get_data(), title=f"Editing <{minitask.name}>")

    def delete_minitask(self, rank: int):

        """handle the deletion of an old task

        Parameters
        ----------
        rank : int
            the rank of the task to delete

        Returns
        -------
        None
        """

        self.logger.info(f"deleting minitask '{self.current_minitasks[rank].name}'")

        del self.current_minitasks[rank]

        self.refresh()

    def completed_minitask(self, rank: int):

        """definition of a "completed minitask" and substitution of the old minitask

        Parameters
        ----------
        rank : int
            the rank of the minitask to complete

        Returns
        -------
        None
        """

        self.completed_minitasks += 1

        # get completed job
        job = self.current_minitasks[rank]

        # define record
        full_record = {}
        full_record["name"] = job.data["name"]
        full_record["type"] = f"finished {job.type}"
        full_record["rank"] = job.data["rank"]
        full_record["next_window"] = job.data["next_window"]
        full_record["duration"] = job.data["duration"]
        full_record["creation"] = job.data["creation"]
        full_record["tot_focus"] = job.data["tot_focus"]
        full_record["tot_rest"] = job.data["tot_rest"]
        full_record["tot_idle"] = job.data["tot_idle"]
        full_record["done"] = True

        finished_job = FinishedMiniTask(y_pos=job.y_pos, rank=job.rank)

        # update the finished task instance
        finished_job.set_record(record=full_record)  # records about the task timers

        # del
        del self.current_minitasks[rank]
        self.current_minitasks += [finished_job]

        self.refresh()

        self.logger.info(f'minitask "{self.current_minitasks[rank].name}" completed')

    def update_focus_minitask(self, focus_package: dict):

        """update the minitask status after a focus session

        Parameters
        ----------
        focus_package : dict
            the focus package

        Returns
        -------
        None
        """

        self.logger.debug(f"updating minitask, package: {focus_package}")

        job = self.current_minitasks[focus_package["rank"]]

        # wrong job
        if job.type != "minitask":
            raise TypeError(
                f"trying to update a <{job.type}> with minitask data, wrong rank"
            )

        # right job
        job.data["tot_focus"] = focus_package["tot_focus"]
        job.data["tot_rest"] = focus_package["tot_rest"]
        job.data["tot_idle"] = focus_package["tot_idle"]
        job.data["done"] = focus_package["done"]

        # check if the task was completed
        if focus_package["done"]:
            self.completed_minitask(rank=focus_package["rank"])

    def refresh(self, sort=True, *args):

        """update the position of the minitask within the project structure"""

        self.clear_widgets()

        if sort:
            self.current_minitasks.sort(key=lambda u: u.rank, reverse=False)

        finished_count = 0
        newly_ordered = []
        for i, minitask in enumerate(self.current_minitasks):

            try:
                minitask.y_pos = 0.9 - i * 0.1
            except AttributeError:
                raise AttributeError(
                    f'minitask "{minitask.name}", y_pos={minitask.y_pos}'
                )

            minitask.update_position()
            minitask.set_rank(rank=i)

            newly_ordered += [minitask]
            self.add_widget(minitask)

            # check minitask status
            if minitask.state == "completed":

                finished_count += 1

        # update
        self.current_minitasks = newly_ordered

        # check project completion
        if (
            finished_count == len(self.current_minitasks)
            and len(self.current_minitasks) > 0
        ):

            print(
                f"\nall {len(self.current_minitasks)} minitasks have been completed! ",
                f' Project "{self.name}" is finished',
            )

            self.done = True

        else:
            self.done = False


class ProjectObject(FloatLayout):

    def __init__(self, y_pos: float, data: dict, **kwargs):
        super(ProjectObject, self).__init__(**kwargs)

        # data
        self.name = data["name"]
        self.priority = data["priority"]
        self.type = "project"

        self.deadline = data["deadline"]  # in seconds
        self.deadline_date = ""

        self.rank = 0
        self.value = 0

        self.state = "pending"

        # project data
        self.data = {
            "name": self.name,
            "type": self.type,
            "rank": self.rank,
            "priority": self.priority,
            "deadline": self.deadline,
            "next_window": "schedule_window",
            "creation": time.time(),
            "done": False,
            "current_minitasks": data["current_minitasks"],
            "completed_minitasks": data["completed_minitasks"],
        }

        # labels
        self.label.text = self.name
        self.score.text = str(self.value)
        self.status.text = "pending"
        if IS_DEADLINE:
            self.deadline_clock.text = ""

        # location
        self.y_pos = y_pos
        self.pos_hint = {"x": 0.0, "top": y_pos}

        self.update_position()

        # logger
        self.logger = logging.getLogger(f"Project-{self.name}")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

        self.logger.info(f"created project")

    def set_score(self, value: float):

        self.value = value
        self.score.text = str(self.value)

    def update_priority(self, priority: int):

        self.priority = priority
        self.data["priority"] = priority

    def update_position(self):

        # update position
        self.pos_hint = {"x": 0.0, "top": self.y_pos}
        self.rank_pos.text = str(self.rank)

        # time from creation
        elapsed = time.time() - self.data["creation"]
        timer = self.deadline - elapsed

        # check #
        # end
        if elapsed >= self.deadline and IS_DEADLINE:
            self.deadline_clock.text = "0h 0m"

            self.label.color = (0.8, 0.2, 0.2, 1)
            self.status.color = (0.8, 0.2, 0.2, 1)
            self.score.color = (0.8, 0.2, 0.2, 1)
            self.deadline_clock.color = (0.8, 0.2, 0.2, 1)

            return

        # going
        if IS_DEADLINE:
            self.deadline_clock.text = f"{timer // 3600 // 24:.0f}d {timer // 3600 % 25:.0f}h {timer // 60 % 60:.0f}m"

    def update_project_data(self, updated_data: dict):

        """update the owned project data from the project window

        Parameters
        ----------
        updated_data : dict

        Returns
        -------
        None
        """

        self.logger.info(f"updating project data")

        self.data["current_minitasks"] = updated_data["current_minitasks"]
        self.data["completed_minitasks"] = updated_data["completed_minitasks"]
        self.data["rank"] = updated_data["rank"]
        self.data["done"] = updated_data["done"]

    def set_rank(self, rank: int):

        self.rank = rank
        self.data["rank"] = rank

    def change_image(self, flag=" "):

        if flag == " ":
            self.job_icons_image.source = r"media/Job obj/job_icons_prj.png"

        elif flag == "open":
            self.job_icons_image.source = r"media/Job obj/job_icons_prj_open.png"
            self.logger.info(f"open button project")

        elif flag == "delete":
            self.job_icons_image.source = r"media/Job obj/job_icons_prj_delete.png"
            self.logger.info(f"delete button project")

        elif flag == "done":
            self.job_icons_image.source = r"media/Job obj/job_icons_prj_done.png"
            self.logger.info(f"done button project")

        elif flag == "edit":
            self.job_icons_image.source = r"media/Job obj/job_icons_prj_edit.png"
            self.logger.info(f"edit button project")


class FinishedProject(FloatLayout):

    def __init__(self, y_pos: float, priority: int, **kwargs):
        super(FinishedProject, self).__init__(**kwargs)

        # data
        self.name = ""
        self.data = {}
        self.factual_priority = 0
        self.priority = priority
        self.rank = "#"
        self.value = 0
        self.deadline = 0  # fictional

        self.type = "finished project"

        # labels
        if IS_DEADLINE:
            self.deadline_clock.text = ""
        self.label.text = self.name
        self.score.text = str(self.factual_priority)
        self.status.text = "completed"

        # location
        self.y_pos = y_pos
        self.pos_hint = {"x": 0.0, "top": y_pos}

        general_logger.info(f"created finished project '{self.name}'")

    def set_rank(self, rank: int):

        """
        set the rank of the project

        Parameters
        ----------
        rank : int
        """

        self.rank = rank
        self.data["rank"] = rank

    def update_position(self):

        """
        update the position of the project
        """

        self.pos_hint = {"x": 0.0, "top": self.y_pos}
        self.rank_pos.text = str(self.rank)

    def update_priority(self, priority: int):

        """
        update the priority of the project

        Parameters
        ----------
        priority : int
        """

        self.priority = priority

    def set_score(self, value: float):

        """
        set the score of the project

        Parameters
        ----------
        value : float
        """

        self.value = value
        self.score.text = str(self.value)

    def set_record(self, record: dict):

        """
        set the record of the project

        Parameters
        ----------
        record : dict
            record of the project
        """

        self.data = record

        # record
        self.name = record["name"]
        self.type = record["type"]
        self.factual_priority = record["priority"]

        # update description
        if IS_DEADLINE:
            self.deadline_clock.text = time.strftime(
                "%H:%M:%S", time.localtime(record["creation"])
            )
        self.label.text = self.name

        general_logger.debug(f"finished project '{self.name}' setting a record")

    def change_image(self, flag=" "):

        """
        change the image of the project

        Parameters
        ----------
        flag : str
            flag to change the image
        """

        if flag == " ":
            self.job_icons_image.source = r"media/Finished obj/finished_prj.png"

        elif flag == "results":
            self.job_icons_image.source = r"media/Finished obj/finished_prj_open.png"
            general_logger(f"finished project '{self.name}' open button finished project")

        elif flag == "delete":
            self.job_icons_image.source = r"media/Finished obj/finished_prj_delete.png"
            general_logger(f"finished project '{self.name}' delete button finished project")


class MiniTask(FloatLayout):

    def __init__(self, y_pos: float, data: dict, **kwargs):

        """
        create a mini task

        Parameters
        ----------
        y_pos : float
            y position of the mini task
        data : dict
            data of the mini task
        """
        super(MiniTask, self).__init__(**kwargs)

        # data
        self.name = data["name"]
        self.duration = data["duration"]
        self.type = data["type"]
        self.rank = data["rank"]

        self.intervals = self.provide_focus_data()["intervals"]

        self.state = "pending"

        self.data = {
            "name": self.name,
            "type": self.type,
            "rank": self.rank,
            "next_window": "project_window",
            "creation": time.time(),
            "done": False,
            "duration": self.duration,
            "tot_focus": 0,
            "tot_rest": 0,
            "tot_idle": 0,
        }

        # labels
        self.label.text = self.name
        self.status.text = "new"

        # location
        self.y_pos = y_pos
        self.pos_hint = {"x": 0.0, "top": y_pos}
        
        # logger
        self.logger = logging.getLogger(f"MiniTask-{self.name}")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

        self.logger.info(f"created mini-task")

    def update_position(self):

        """
        update the position of the mini task
        """

        # update position
        self.pos_hint = {"x": 0.0, "top": self.y_pos}

    def provide_focus_data(self):

        """
        compute the intervals as focus-rest-focus-rest... from the total task duration

        Returns
        -------
        dict : intervals, type, rank, next_window
        """

        # base focus length = 20, rest = 5
        nb_focus = [20] * (self.duration // 20) + [self.duration % 20]
        return {
            "intervals": list(array([[x] + [5] for x in nb_focus]).reshape(-1))[:-1],
            "type": self.type,
            "rank": self.rank,
            "next_window": "project_window",
        }

    def set_rank(self, rank: int):

        """
        set the rank of the mini task

        Parameters
        ----------
        rank : int
        """

        self.rank = rank
        self.data["rank"] = rank
        self.rank_pos.text = f"{rank}"

    def start_task(self):

        self.logger.info(f"starting mini-task")

    def edit_task(self):

        self.logger.info(f"editing mini-task")

    def get_data(self):

        """
        Returns
        -------
        dict : data of the mini task
        """

        return self.data

    def change_image(self, flag=" "):

        """
        change the image of the mini task

        Parameters
        ----------
        flag : str
        """

        if flag == " ":
            self.minitask_icons_image.source = r"media/Mini task obj/minitask_icons.png"

        elif flag == "play":
            self.minitask_icons_image.source = (
                r"media/Mini task obj/minitask_icons_play.png"
            )
            self.logger.info("play button pressed")

        elif flag == "delete":
            self.minitask_icons_image.source = (
                r"media/Mini task obj/minitask_icons_delete.png"
            )
            self.logger.info("delete button pressed")

        elif flag == "done":
            self.minitask_icons_image.source = (
                r"media/Mini task obj/minitask_icons_done.png"
            )
            self.logger.info("done button pressed")

        elif flag == "edit":
            self.minitask_icons_image.source = (
                r"media/Mini task obj/minitask_icons_edit.png"
            )
            self.logger.info("edit button pressed")


class NewMiniTask(Screen):

    def __init__(self, **kwargs):

        super(NewMiniTask, self).__init__(**kwargs)

        self.data = {}

        self.app = ""

        # logger
        self.logger = logging.getLogger(f"NewMiniTask")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

    def on_enter(self, *args):

        self.logger.info("NewMiniTask window entered")

    def on_leave(self, *args):

        self.reset()
        self.logger.info("NewMiniTask window left")

    def load_data(self, data: dict, title: str):

        """load info about the new task to create

        Parameters
        ----------
        data : dict
            data of the task
        title : str
            title of the window
        """

        self.data = data

        self.mini_task_name.text = data["name"]
        self.duration.text = str(self.data["duration"])
        self.rank.text = str(self.data["rank"])

        self.title.text = title
        self.app = App.get_running_app()
        self.data["validity"] = False

        self.logger.debug(f"loaded data: {data}")

    def check(self):

        """check it the proposed task design is valid"""

        print(f'\ntask "{self.mini_task_name.text}" checked!')
        self.data["name"] = self.mini_task_name.text

        double_check = 0

        # check duration
        try:
            self.data["duration"] = int(self.duration.text)

            # one check
            double_check += 1

        except ValueError:
            self.logger.error(f'"{self.duration.text}" is not a valid duration')
            self.duration.text = ""
            self.data["duration"] = 0

        # check rank
        try:
            self.data["rank"] = int(self.rank.text)

            # second check
            double_check += 1

        # invalid
        except ValueError:
            self.logger.error(f'"{self.rank.text}" is not a valid rank')
            self.rank.text = ""
            self.data["rank"] = -1

        # grant validity
        if double_check == 2:
            # enable
            self.data["validity"] = True
            self.logger.debug(f"task {self.data['name']} is valid")

        else:

            # disable
            self.data["validity"] = False

    def clear(self):

        """
        clear the data of the task
        """

        self.data = {
            "name": "",
            "duration": 0,
            "rank": 0,
            "type": "minitask",
            "validity": False,
        }

        self.mini_task_name.text = ""
        self.rank.text = ""
        self.duration.text = ""

        self.logger.debug("cleared data")

    def submit(self, returning=False):

        """
        submit the task design

        Parameters
        ----------
        returning : bool
            if the task is being returned to the project window
        """

        if returning:
            self.check()

        # valid task design
        if self.data["validity"]:

            # next
            self.app.root.current = "project_window"
            self.app.root.transition.direction = "right"
            self.app.root.current_screen.projects_manager.save_mini_task(
                new_mini_task_data=self.data
            )

            # reset
            self.reset()
            self.logger.debug("task submitted")
            return

    def change_image(self, flag=" "):

        """
        change the image of the window

        Parameters
        ----------
        flag : str
            flag to change the image
        """

        if flag == " ":
            self.newminitask_window_image.source = (
                r"media/NewJob window/newjob_window.png"
            )

        elif flag == "check":
            self.newminitask_window_image.source = (
                r"media/NewJob window/newjob_window_check.png"
            )
            self.logger.info("check button pressed")

        elif flag == "clear":
            self.newminitask_window_image.source = (
                r"media/NewJob window/newjob_window_clear.png"
            )
            self.logger.info("clear button pressed")

        elif flag == "submit":
            self.newminitask_window_image.source = (
                r"media/NewJob window/newjob_window_submit.png"
            )
            self.logger.info("submit button pressed")

        elif flag == "return":
            self.newminitask_window_image.source = (
                r"media/NewJob window/newjob_window_return.png"
            )
            self.logger.info("return button pressed")

        else:
            warnings.warn(f"flag {flag} does not correspond to any newjob_window key")

    def reset(self):

        self.data = {}

        self.mini_task_name.text = ""
        self.rank.text = ""
        self.title.text = ""
        self.duration.text = ""

        # buttons
        self.newminitask_window_image.source = r"media/NewJob window/newjob_window.png"


class FinishedMiniTask(FloatLayout):

    """new task object, with buttons"""

    def __init__(self, y_pos: float, rank: int, **kwargs):

        """
        Parameters
        ----------
        y_pos : float
            y position of the task
        rank : int
            rank of the task
        """

        super(FinishedMiniTask, self).__init__(**kwargs)

        # data
        self.name = ""
        self.record = {}
        self.rank = rank
        self.type = ""

        self.data = {}

        # labels
        self.label.text = self.name
        self.status.text = "completed"

        self.state = "completed"

        # location
        self.y_pos = y_pos
        self.pos_hint = {"x": 0.0, "top": y_pos}

        general_logger.info(f"Finished MiniTask created")

    def set_rank(self, rank: int):

        """
        set the rank of the task

        Parameters
        ----------
        rank : int
            rank of the task
        """

        self.rank = rank
        self.rank_pos.text = f"{rank}"

    def update_position(self):

        """
        update the position of the task
        """

        self.pos_hint = {"x": 0.0, "top": self.y_pos}

    def set_record(self, record: dict):

        """
        set the record of the task

        Parameters
        ----------
        record : dict
            record of the task
        """

        self.data = record

        # record
        self.name = record["name"]
        self.type = record["type"]

        # update description
        self.label.text = self.name

        general_logger.info(f'Finished MiniTask "{self.name}" setting a record')

    def change_image(self, flag=" "):

        """
        change the image of the window

        Parameters
        ----------
        flag : str
            flag to change the image
        """

        if flag == " ":
            self.job_icons_image.source = r"media/Finished obj/finished_minitask.png"

        elif flag == "results":
            self.job_icons_image.source = (
                r"media/Finished obj/finished_minitask_results.png"
            )
            general_logger.info(f"finished mini-task '{self.name}' result button pressed")

        elif flag == "delete":
            self.job_icons_image.source = (
                r"media/Finished obj/finished_minitask_delete.png"
            )
            general_logger.info(f"finished mini-task '{self.name}' delete button pressed")


""" SESSION """


class IntervalHandler(Screen):

    def __init__(self, **kwargs):

        super(IntervalHandler, self).__init__(**kwargs)

        # about intervals
        self.intervals = []
        self.idx = 0
        self.max_idx = 0
        self.current_timer = ""

        self.names = ("focus_timer", "rest_timer")

        # about results and interface
        self.results = {
            "tot_focus": 0,
            "tot_rest": 0,
            "tot_idle": 0,
            "done": False,
            "next_window": "activity_window",
            "type": "session",
            "rank": -1,
        }
        self.data = {}
        self.app = ""

    def on_enter(self, *args):

        print("\n--------- Interval Handler Window ---------")

    def load_data(self, data: dict):

        # data
        self.results["rank"] = data["rank"]
        self.results["next_window"] = data["next_window"]
        self.results["type"] = data["type"]

        # intervals
        self.intervals = data["intervals"]
        self.idx = 0
        self.max_idx = len(self.intervals)

        self.app = App.get_running_app()
        print(f"\n% intervals loaded: {self.intervals} %")

        Window.size = (250, 200)

        self.step()

    def step(self):

        # finish
        if self.idx == self.max_idx:

            self.results["done"] = True
            self.close()

            return

        next_interval = self.intervals[self.idx]

        # next interval
        self.current_timer = self.names[int(self.idx % 2)]
        self.app.root.current = self.current_timer
        self.app.root.transition.direction = "left"
        if self.idx == 0:
            self.app.root.current_screen.load_interval(
                interval=next_interval, ongoing=False
            )
        else:
            self.app.root.current_screen.load_interval(interval=next_interval)

        self.idx += 1

    def get_results(self, results: tuple):

        print("\ninterval results: \n", results)

        """ update results """

        names, durations = results

        for name, duration in zip(names, durations):
            self.results[f"tot_{name}"] += duration

    def close(self):

        print("\nsession finished, results: ", self.results)

        # return
        self.app.root.current = "results_window"
        self.app.root.transition.direction = "left"
        self.app.root.current_screen.show(data=self.results)

        Window.size = (700, 500)

        # reset
        self.reset()

    def reset(self):

        # about intervals
        self.intervals = []
        self.idx = 0
        self.max_idx = 0
        self.current_timer = ""

        self.names = ("focus_timer", "rest_timer")

        # about results and interface
        self.results = {
            "tot_focus": 0,
            "tot_rest": 0,
            "tot_idle": 0,
            "done": False,
            "next_window": "activity_window",
        }
        self.data = {}


class NewSessionWindow(Screen):

    def __init__(self, **kwargs):
        super(NewSessionWindow, self).__init__(**kwargs)

        self.settings = {
            "intervals": [],
            "rank": -1,
            "type": "session",
            "next_window": "activity_window",
        }

        self.saved = False
        self.validity = False

    def on_enter(self, *args):

        print("\n--------------------- New Session Settings ---------------------")

    def on_leave(self, *args):

        self.reset()

    def reset(self, *args):

        print("\nleft session: \n", self.settings)

        # reset
        self.settings = {
            "intervals": [],
            "rank": -1,
            "type": "session",
            "next_window": "activity_window",
        }

        self.saved = False
        self.start_button.color = (0.1, 0.1, 0.1, 1)

    def check_inputs(self):

        """check if the inputs are valid"""

        triple_check = 0

        # focus interval
        try:
            _ = int(self.focus_interval.text)
            triple_check += 1

        except ValueError:
            print(
                f'\n!Error: "{self.focus_interval.text}" for the focus interval is not an integer'
            )
            self.focus_interval.text = ""

        # rest interval
        try:
            _ = int(self.focus_interval.text)
            triple_check += 1

        except ValueError:
            print(
                f'\n!Error: "{self.rest_interval.text}" for the rest interval is not an integer'
            )
            self.rest_interval.text = ""

        # repetition
        try:
            _ = int(self.repetition.text)
            triple_check += 1

        except ValueError:
            print(
                f'\n!Error: "{self.repetition.text}" for the repetition is not an integer'
            )
            self.repetition.text = ""

        # grant validity
        if triple_check == 3:
            self.validity = True
            self.start_button.color = (0.1, 0.9, 0.1, 1)

            # save data and build intervals
            self.save()

        else:
            self.validity = False
            self.start_button.color = (0.9, 0.1, 0.1, 1)

    def save(self):

        """save and jump to the session"""

        # calculate intervals
        nb_intervals = int(self.repetition.text)
        self.settings["intervals"] = array(
            [
                [int(self.focus_interval.text)] + [int(self.rest_interval.text)]
                for _ in range(nb_intervals)
            ]
        ).reshape(-1)[:-1]

        print("\nsession settings saved:\n", self.settings)

        self.saved = True

    def get_data(self):
        return self.settings


class FocusTimer(Screen):
    def __init__(self, **kwargs):
        super(FocusTimer, self).__init__(**kwargs)

        self.interval = 0  # how long is this interval
        self.duration = 0  # how long it has run so far
        self.state = "paused"  # state: finished, running, paused
        self.start_time = 0.0  # time at which it started
        self.checkpoint = 0.0  # paused time

        self.current_time = [0, 0]

        self.job = 0
        self.app = ""

    def on_enter(self, *args):

        print("\n--------- Focus Timer Window ---------")

    def load_interval(self, interval: int, ongoing=True):

        """
        load the interval
        :param interval: int, minutes
        :param ongoing: bool
        :return: saved values
        """

        # load
        self.interval = interval * 60
        self.checkpoint = interval * 60
        self.current_time = [interval, 0]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        self.app = App.get_running_app()

        if ongoing:

            print("\nfocus ongoing")

            # start clock
            self.start_time = time.time()
            self.job = Clock.schedule_interval(self.ticking, 0.5)

            # new state
            self.state = "running"

        else:
            print("\nfocus waiting to start")

            # new state
            self.state = "paused"

        print(
            "\n% focus interval loaded: ", self.current_time, f" [{self.interval}s] %"
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
            self.focus_timer_image.source = r"media/Focus session/focus_go.png"

        # running + pause button : pause
        elif self.state == "running":

            print("\nfocus #pause")

            # stop clock
            self.job.cancel()

            # new state
            self.state = "paused"

            # checkpoint
            self.checkpoint = self.current_time[0] * 60 + self.current_time[1]

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

    def change_image(self, flag=" ", pressed=False):

        if pressed:

            # stop
            if flag == " " and self.state == "running":
                self.focus_timer_image.source = r"media/Focus session/focus_go_stop.png"

            elif flag == "next" and self.state == "running":
                self.focus_timer_image.source = r"media/Focus session/focus_go_next.png"

            elif flag == "reset" and self.state == "running":
                self.focus_timer_image.source = (
                    r"media/Focus session/focus_go_reset.png"
                )

            elif flag == "return" and self.state == "running":
                self.focus_timer_image.source = (
                    r"media/Focus session/focus_go_return.png"
                )

            # play
            elif flag == " " and self.state == "paused":
                self.focus_timer_image.source = (
                    r"media/Focus session/focus_nogo_play.png"
                )

            elif flag == "next" and self.state == "paused":
                self.focus_timer_image.source = (
                    r"media/Focus session/focus_nogo_next.png"
                )

            elif flag == "reset" and self.state == "paused":
                self.focus_timer_image.source = (
                    r"media/Focus session/focus_nogo_reset.png"
                )

            elif flag == "return" and self.state == "paused":
                self.focus_timer_image.source = (
                    r"media/Focus session/focus_nogo_return.png"
                )

        else:
            if self.state == "running":
                self.focus_timer_image.source = r"media/Focus session/focus_go.png"

            elif self.state == "paused":
                self.focus_timer_image.source = r"media/Focus session/focus_nogo.png"

    def tracking(self):

        self.duration = int(time.time() - self.start_time)

        # control for absurd time difference, usually when the timer isn't event started
        if self.duration > 24 * 60 * 60:
            self.duration = 0

        print("tracked: ", self.duration, "s")

    def close(self):

        print("\nfocus #close")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()

        # next
        """self.app.root.current = "interval_handler"
        self.app.root.transition.direction = 'right'
        self.app.root.current_screen.get_results(results=self.get_results())
        self.app.root.current_screen.step()"""

        self.app.root.current = "extra_focus_timer"
        self.app.root.transition.direction = "left"
        self.app.root.current_screen.load_results(results=self.get_results())

        self.total_reset()

    def reset(self):

        """reset to the original values"""

        print("\nfocus #reset")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            warnings.warn("timer already reset")
            return

        Clock.usleep(1000)

        # record
        self.tracking()

        # reset values to original
        self.checkpoint = self.interval
        self.current_time = [int(self.interval // 60), int(self.interval % 60)]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        # restart
        self.start_time = time.time()
        self.job = Clock.schedule_interval(self.ticking, 0.5)

    def quit(self):

        print("\nfocus #quit")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()

        # next
        self.app.root.current = "interval_handler"
        self.app.root.transition.direction = "right"
        self.app.root.current_screen.results["done"] = False
        self.app.root.current_screen.close()

        self.total_reset()

    def total_reset(self):

        # reset
        self.interval = 0  # how long is this interval
        self.duration = 0  # how long it has run so far
        self.state = "finished"  # state: finished, running, paused
        self.start_time = 0.0  # time at which it started
        self.checkpoint = 0.0  # paused time

        self.current_time = [0, 0]

        self.job = ""

        self.display.text = "00:00"

    def get_results(self):

        print("\nfocus results: ", self.duration)

        return ["focus"], [self.duration]


class RestTimer(Screen):
    def __init__(self, **kwargs):
        super(RestTimer, self).__init__(**kwargs)

        self.interval = 0  # how long is this interval
        self.duration = 0  # how long it has run so far
        self.start_time = 0.0  # time at which it started

        self.current_time = [0, 0]

        self.job = 0
        self.app = ""

    def on_enter(self, *args):

        print("\n --------- Rest Timer Window ---------")

    def load_interval(self, interval: int):

        """
        load the interval
        :param interval: seconds
        :return: saved values
        """

        # update
        self.interval = interval * 60
        self.current_time = [interval, 0]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        self.start_time = time.time()
        self.job = Clock.schedule_interval(self.ticking, 0.5)

        self.app = App.get_running_app()
        print("\n% rest interval loaded: ", self.current_time, f" [{self.interval}s] %")

    def ticking(self, *args):

        elapsed = int(self.interval - (time.time() - self.start_time))
        self.current_time[1] = int(elapsed % 60)
        self.current_time[0] = int(elapsed // 60)

        if elapsed <= 0:

            # cancel
            self.job.cancel()

            # record
            self.tracking()

            #
            self.display.text = "00:00"
            Clock.usleep(10000)

            self.close()
            return

        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

    def change_image(self, flag=" ", pressed=False):

        if pressed:

            if flag == "next":
                self.rest_timer_image.source = r"media/Focus session/rest_next.png"

            elif flag == "reset":
                self.rest_timer_image.source = r"media/Focus session/rest_reset.png"

            elif flag == "return":
                self.rest_timer_image.source = r"media/Focus session/rest_return.png"

        else:
            self.rest_timer_image.source = r"media/Focus session/rest.png"

    def tracking(self):

        self.duration = int(time.time() - self.start_time)
        print(f"tracked: {self.duration}s")

    def reset(self):
        """reset to the original values"""

        print("\nrest #reset")

        # cancel
        self.job.cancel()
        Clock.usleep(1000)

        # record
        self.tracking()

        # reset values to original
        self.current_time = [int(self.interval // 60), int(self.interval % 60)]
        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

        # restart
        self.start_time = time.time()
        self.job = Clock.schedule_interval(self.ticking, 0.5)

    def close(self):

        print("\nrest #close")

        # cancels
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()

        # towards idle
        self.app.root.current = "idle_timer"
        self.app.root.transition.direction = "left"
        self.app.root.current_screen.start(rest_duration=self.duration)

        self.total_reset()

    def quit(self):

        print("\nrest #quit")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()

        # next
        self.app.root.current = "interval_handler"
        self.app.root.transition.direction = "right"
        self.app.root.current_screen.results["done"] = False
        self.app.root.current_screen.close()

        self.total_reset()

    def total_reset(self):

        # reset
        self.interval = 0  # how long is this interval
        self.duration = 0  # how long it has run so far
        self.start_time = 0.0  # time at which it started

        self.current_time = [0, 0]

        self.job = 0

        self.display.text = "00:00"


class IdleTimer(Screen):
    def __init__(self, **kwargs):
        super(IdleTimer, self).__init__(**kwargs)

        self.interval = 0  # how long is this interval
        self.start_time = 0.0  # time at which it started
        self.current_time = [0, 0]

        self.job = 0
        self.app = ""

        self.durations = [0, 0]

    def on_enter(self, *args):

        print("\n--------- Idle Timer Window ---------")

    def start(self, rest_duration: int):

        # record previous rest duration
        self.durations[0] = rest_duration

        self.start_time = time.time()
        self.job = Clock.schedule_interval(self.ticking, 0.5)
        self.display.text = "00:00"

        self.app = App.get_running_app()

    def change_image(self, flag=" ", pressed=False):

        if pressed:

            if flag == "next":
                self.idle_timer_image.source = r"media/Focus session/idle_next.png"

            elif flag == "done":
                self.idle_timer_image.source = r"media/Focus session/idle_done.png"

            elif flag == "return":
                self.idle_timer_image.source = r"media/Focus session/idle_return.png"

        else:
            self.idle_timer_image.source = r"media/Focus session/idle.png"

    def ticking(self, *args):

        elapsed = int(time.time() - self.start_time)
        self.current_time[1] = elapsed % 60
        self.current_time[0] = elapsed // 60

        self.display.text = f"{self.current_time[0]:02d}:{self.current_time[1]:02d}"

    def tracking(self):

        self.durations[1] += int(time.time() - self.start_time)

    def close(self):

        print("\nidle #close")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()

        # next
        self.app.root.current = "interval_handler"
        self.app.root.transition.direction = "right"
        self.app.root.current_screen.get_results(results=self.get_results())
        self.app.root.current_screen.step()

        self.total_reset()

    def quit(self, completed=False):

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # record
        self.tracking()
        print("\nidle #quit", f" [durations: {self.durations}]")

        # next
        self.app.root.current = "interval_handler"
        self.app.root.transition.direction = "right"
        self.app.root.current_screen.get_results(results=self.get_results())
        self.app.root.current_screen.results["done"] = completed
        self.app.root.current_screen.close()

        self.total_reset()

    def total_reset(self):

        # reset
        self.interval = 0  # how long is this interval
        self.durations = [0, 0]  # how long it has run so far
        self.start_time = 0.0  # time at which it started
        self.current_time = [0, 0]

        self.job = 0

        self.display.text = "00:00"

    def get_results(self):

        print("\nrest & idle results = ", self.durations)

        return ["rest", "idle"], self.durations


class ExtraFocusTimer(Screen):
    def __init__(self, **kwargs):
        super(ExtraFocusTimer, self).__init__(**kwargs)

        self.results = {}
        self.app = ""

    def on_enter(self, *args):

        print("\n--------- Extra Focus Timer Window ---------")

        self.app = App.get_running_app()

    def go(self):

        print("\nidle #close")

        # cancel
        try:
            self.job.cancel()
        except AttributeError:
            pass

        # next
        self.app.root.current = "interval_handler"
        self.app.root.transition.direction = "right"
        self.app.root.current_screen.get_results(results=self.results)
        self.app.root.current_screen.step()

    def load_results(self, results):

        self.results = results


class ResultsWindow(Screen):
    def __init__(self, **kwargs):

        super(ResultsWindow, self).__init__(**kwargs)

        self.next_window = ""
        self.data = {}
        self.obj_type = ""
        self.app = ""

    def on_enter(self, *args):

        print("\n--------- Result  Window ---------")

    def show(self, data: dict):

        print("Result window: results received: \n", data)

        focused = data["tot_focus"]
        rested = data["tot_rest"]
        idled = data["tot_idle"]
        self.tot_focus.text = f"{focused//60:02d}:{focused%60:02d}"
        self.tot_rest.text = f"{rested//60:02d}:{rested%60:02d}"
        self.tot_idle.text = f"{idled//60:02d}:{idled%60:02d}"
        self.state.text = str(data["done"])
        self.next_window = data["next_window"]
        self.obj_type = data["type"]

        self.data = data

        if data["done"]:
            self.state.color = (0.1, 0.9, 0.1, 1)
        else:
            self.state.color = (0.9, 0.1, 0.1, 1)

    def forward_data(self):

        self.app = App.get_running_app()

        self.app.root.current = self.next_window
        self.app.root.transition.direction = "right"

        if self.next_window == "schedule_window" and self.obj_type == "task":
            self.app.root.current_screen.jobs_manager.update_focus_task(
                focus_package=self.data
            )

        elif self.next_window == "project_window" and self.obj_type == "minitask":
            self.app.root.current_screen.projects_manager.update_focus_minitask(
                focus_package=self.data
            )

    def on_leave(self, *args):

        self.reset()

    def reset(self):

        self.next_window = ""
        self.data = {}


""" GENERAL SETTINGS """


class GeneralSettings(Screen):

    """
    Window in which the user can change the General Settings
    """

    def __init__(self, **kwargs):
        super(GeneralSettings, self).__init__(**kwargs)

        self.focused_time = FOCUSED_TIME
        self.rest_time = REST_TIME

        self.saved = False

    def on_enter(self, *args):

        general_logger.info("GeneralSettings window entered")

        # self.app = App.get_running_app()

        # self.reset()
        self.focus_interval.text = str(FOCUSED_TIME)
        self.rest_interval.text = str(REST_TIME)

    def on_leave(self, *args):

        self.reset()

        general_logger.info("GeneralSettings window left")

    def save(self):

        """
        save the input prompted for Focus time and Rest time
        
        Returns
        -------
        None
        """

        global FOCUSED_TIME
        global REST_TIME

        validity = 2
        try:
            self.focused_time = int(self.focus_interval.text)
        except ValueError:
            validity -= 1
            general_logger.error(f"Invalid input for focused time: {self.focus_interval.text}")

        try:
            self.rest_time = int(self.rest_interval.text)
        except ValueError:
            validity -= 1
            general_logger.error(f"Invalid input for rest time: {self.rest_interval.text}")

        # valid inputs
        if validity == 2:

            self.saved = True
            FOCUSED_TIME = self.focused_time
            REST_TIME = self.rest_time

            self.save_button.color = (0.1, 0.9, 0.1, 1)
            general_logger.info(f"General settings saved: {FOCUSED_TIME} - {REST_TIME}")

        else:
            self.save_button.color = (0.3, 0.1, 0.1, 1)

    def reset(self):

        # reset
        self.focused_time = FOCUSED_TIME
        self.rest_time = REST_TIME

        self.saved = False
        self.save_button.color = (0.1, 0.1, 0.1, 1)


""" SIMPLE TIMER """


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
        cache_module_obj.delete_timer_cache()

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

        # record
        self.tracking()

        Window.size = (700, 500)

        # next
        self.app.root.current = "activity_window"
        self.app.root.transition.direction = "right"

        self.total_reset()

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

    def total_reset(self):

        # reset
        self.tot_duration = 0  # how long is this interval
        self.duration = 0  # how long it has run so far
        self.state = "finished"  # state: finished, running, paused
        self.start_time = 0.0  # time at which it started
        self.checkpoint = 0.0  # paused time

        self.current_time = [0, 0]

        self.job = ""

        self.display.text = "00:00"

    def get_results(self):

        print("\nfocus results: ", self.duration)

        return ["focus"], [self.duration]


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

        # next
        self.app.root.current = "activity_window"
        self.app.root.transition.direction = "right"

        Window.size = (700, 500)


""" STAR """

class Routines(Screen):

    """
    Window in which the user can activate routines 
    """

    def __init__(self, **kwargs):
        super(Routines, self).__init__(**kwargs)

        self.minutes = 0.

        # logger
        self.logger = logging.getLogger("Routines")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

    def on_enter(self, *args):

        self.logger.info("Routines window entered")

    def on_leave(self, *args):

        self.logger.info("Routines window left")

    def end_work_day(self):

        """
        timer to the end of the usual work day

        Returns
        -------
        None
        """

        # get end time <-- edit for the config.json
        end_time = (23, 15)  # time in hours and minutes

        # calculate how many minutes are left from end_time 
        now = datetime.datetime.now()
        end = datetime.datetime(now.year, now.month, now.day, end_time[0], end_time[1])
        delta = end - now

        # convert to minutes 
        minutes = delta.seconds // 60

        # save in cache
        cache_module_obj.save_timer_cache(timer_cache={'duration': minutes})

        # start timer 
        self.logger.info(f"end of work-day timer initiated - minutes: {minutes//60:02d}:{minutes%60:02d}")
        os.system(f"./timer_window_run.sh")

    def clean_cache(self):

        cache_module_obj.delete_timer_cache()


""" WINDOWS """


class ActivityWindow(Screen):

    def __init__(self, **kwargs):
        super(ActivityWindow, self).__init__(**kwargs)

        self.clock = 0
        self.app = ""

        # logger
        self.logger = logging.getLogger("ActivityWindow")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

    def on_enter(self):

        self.logger.info("ActivityWindow entered")
        Window.size = (700, 500)

        self.app = App.get_running_app()
        self.clock = Clock.schedule_interval(self.ticking, 1)

    def on_leave(self):

        # cancel
        try:
            self.clock.cancel()
        except AttributeError:
            pass

        self.logger.info("ActivityWindow left")

    def button_pressed(self, name: str):

        if name == "close":
            self.main_image.source = "media/main_screen/main_screen_close.png"
            self.logger.info("close button pressed")

        elif name == "focus":
            self.main_image.source = "media/main_screen/main_screen_focus.png"
            self.logger.info("focus button pressed")

        elif name == "schedule":
            self.main_image.source = "media/main_screen/main_screen_schedule.png"
            self.logger.info("schedule button pressed")

        elif name == "settings":
            self.main_image.source = "media/main_screen/main_screen_settings.png"
            self.logger.info("settings button pressed")

        elif name == "timer":
            self.main_image.source = "media/main_screen/main_screen_timer.png"
            self.logger.info("timer button pressed")

        elif name == "star":
            self.main_image.source = "media/main_screen/main_screen_star.png"
            self.logger.info("star button pressed")

    def button_released(self, name=""):

        self.main_image.source = r"media/Activity window/activity_window.png"

        #if name == "timer":
        #    Window.size = (250, 200)
        pass

    def ticking(self, *args):

        """
        the clock ticks

        Returns
        -------
        None
        """

        now = time.localtime()
        self.clock_display.text = f"{now.tm_hour:02d}:{now.tm_min:02d}"

    def timer_button_pressed(self):

        """
        timer button pressed, open timer window

        Returns
        -------
        None
        """

        os.system(f"./timer_window_run.sh")


class ScheduleWindow(Screen):

    """
    main application window, where the tasks are displayed and the buttons available
    """

    def __init__(self, **kwargs):
        super(ScheduleWindow, self).__init__(**kwargs)

        ### tasks ###
        self.current_tasks = []
        self.current_popup = ""
        self.app = ""
        self.clock = 0

        self.entered_count = 0

        # logger
        self.logger = logging.getLogger("ScheduleWindow")
        self.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(stream=sys.stdout)

        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

        stdout.setFormatter(fmt)
        self.logger.addHandler(stdout)

    def on_enter(self):

        self.logger.info("ScheduleWindow entered")

        self.entered_count += 1
        self.app = App.get_running_app()

        # load pending tasks
        if self.entered_count <= 1:
            self.app.root.current_screen.jobs_manager.app = self.app
            self.app.root.current_screen.jobs_manager.load_pending()
        
        self.clock = Clock.schedule_interval(self.ticking, 1)

    def on_leave(self):

        self.logger.info("ScheduleWindow left")

    def save_task(self):

        self.jobs_manager.save_task()

    def change_image(self, flag=" "):

        if flag == " ":
            self.schedule_window_image.source = (
                r"media/Schedule window/schedule_window.png"
            )

        elif flag == "add":
            self.schedule_window_image.source = (
                r"media/Schedule window/schedule_window_add.png"
            )

        elif flag == "save":
            self.schedule_window_image.source = (
                r"media/Schedule window/schedule_window:save.png"
            )

        elif flag == "return":
            self.schedule_window_image.source = (
                r"media/Schedule window/schedule_window_return.png"
            )

        else:
            warnings.warn(f"flag <{flag}> does not correspond to any schedule button")

    def ticking(self, *args):

        """
        the clock ticks

        Returns
        -------
        None
        """

        now = time.localtime()
        self.clock_display.text = f"{now.tm_hour:02d}:{now.tm_min:02d}"


class WindowManager(ScreenManager):
    def on_resize(self):

        pass


kv1 = Builder.load_file("planner.kv")

Window.size = (700, 500)


class PlannerApp(App):
    def build(self):
        return kv1


if __name__ == "__main__":
    PlannerApp().run()
