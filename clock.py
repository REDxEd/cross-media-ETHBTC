from datetime import datetime
from multiprocessing.dummy import current_process
from operator import contains
import sched
from unicodedata import name

from aiohttp import client
# import confg
import os
from binance.client import Client
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import schedule
import time
from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every minute....')

sched.start()