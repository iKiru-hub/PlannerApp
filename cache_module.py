import os
import json
import sys 
import logging


# adjust path to the operating system
if sys.platform == 'win32':
    split = '\\'
    OS = 0
else:
    split = '/'
    OS = 1

# general logger
logger = logging.getLogger(f"CacheLogs")
logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")
stdout.setFormatter(fmt)
logger.addHandler(stdout)


# get the path of the app
PATH = os.getcwd()
APP_PATH = PATH + f"{split}Workflow" * ("workflow" not in PATH and "Workflow" not in PATH) + f"{split}routines{split}PlannerApp" * ("PlannerApp" not in PATH) 

# define the path of the cache
CACHE_PATH = APP_PATH + f"{split}cache"


class CacheInterface:

    def __init__(self):

        self.pending_filename = "pending_jobs.json"
        self.timer_filename = "timer.json"

    def retrieve_objects(self):

        """ retrieve eventual pending tasks / projects 

        Parameters
        ----------
        None

        Returns
        -------
        bool : True if there are pending objects, False otherwise
        dict : the list of pending objects
        """

        # check if the file of pending objects is there
        if self.pending_filename in os.listdir(path=CACHE_PATH):

            # load
            with open(f'{CACHE_PATH}{split}{self.pending_filename}', 'rb') as f:

                pending_list = json.loads(f.read())

            logger.info(f'{len(list(pending_list.keys()))} job objects found')
            return True, pending_list

        # no file found
        logger.warning(f'no file found in cache')
        return False, {}

    def save_pending_objects(self, objects: list, settings: dict):

        """ save a list of pending objects

        Parameters
        ----------
        objects : list
            the list of objects to save
        settings : dict
            the settings of the app 

        Returns
        -------
        None
        """

        pending_list = {'settings': settings}

        for obj in objects:

            pending_list[obj['name']] = obj

        # save
        with open(f"{CACHE_PATH}{split}{self.pending_filename}", 'w') as f:
            f.write(json.dumps(pending_list))

        logger.info(f'{len(objects)} job objects successfully saved')

    def save_timer_cache(self, timer_cache: dict):

        """ save the timer 

        Parameters
        ----------
        timer_cache : dict
            the timer settings 

        Returns
        -------
        None
        """

        # save
        with open(f"{CACHE_PATH}{split}{self.timer_filename}", 'w') as f:
            f.write(json.dumps(timer_cache))

        logger.info(f'timer cache successfully saved')

    def get_timer_cache(self):

        """ retrieve the timer cache

        Parameters
        ----------
        None

        Returns
        -------
        bool : True if there is a timer cache, False otherwise
        dict : the timer cache
        """

        # check if timer cache is there
        if self.timer_filename not in os.listdir(path=CACHE_PATH):
            logger.warning(f'no timer cache found')
            return False, {}

        # load
        with open(f'{CACHE_PATH}{split}{self.timer_filename}', 'rb') as f:

            timer_cache = json.loads(f.read())

        logger.info(f'timer cache found')
        return True, timer_cache

    def delete_timer_cache(self):

        """ delete the timer cache 

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # check if timer cache is there
        if self.timer_filename not in os.listdir(path=CACHE_PATH):
            print(f'\n<!no timer cache found>')
            return

        # delete
        os.remove(f"{CACHE_PATH}{split}{self.timer_filename}")

        logger.info(f'timer cache successfully deleted')

