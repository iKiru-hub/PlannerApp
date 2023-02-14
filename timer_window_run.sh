#! /bin/bash

# This script is used to run the timer window. It is called by planner_app

# open a new tmux tab 
tmux split-window -h "python timer_window.py"
