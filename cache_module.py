import os
import json
import sys 



# adjust path to the operating system
if sys.platform == 'win32':
    split = '\\'
else:
    split = '/'

# define the path to the cache folder
PATH = os.getcwd()
PENDING_PATH = PATH + f"{split}Workflow" * ("workflow" not in PATH and "Workflow" not in PATH) + f"{split}routines{split}PlannerApp" * ("PlannerApp" not in PATH) + f"{split}cache"


class CacheInterface:

    def __init__(self):

        self.pending_filename = "pending_jobs.json"

    def retrieve_objects(self):

        """ retrieve eventual pending tasks / projects """

        # check if the file of pending objects is there
        if self.pending_filename in os.listdir(path=PENDING_PATH):

            # load
            with open(f'{PENDING_PATH}{split}{self.pending_filename}', 'rb') as f:

                pending_list = json.loads(f.read())

            print(f'\n<{len(list(pending_list.keys()))} job objects found>\n', pending_list)
            return True, pending_list

        # no file found
        print('\n!oh no, no file found in cache!')
        return False, {}

    def save_pending_objects(self, objects: list, settings: dict):

        """ save a list of pending objects """

        pending_list = {'settings': settings}

        for obj in objects:

            pending_list[obj['name']] = obj

        # save
        with open(f"{PENDING_PATH}{split}{self.pending_filename}", 'w') as f:
            f.write(json.dumps(pending_list))

        print(f'\n<{len(objects)} job objects successfully saved>')


