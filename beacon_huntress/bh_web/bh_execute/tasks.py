from __future__ import absolute_import, unicode_literals

from celery import shared_task

from beacon_huntress.src.bin.web import exe_bh

@shared_task
def example_task(x,y):
    return x * y
    
@shared_task
def run_algo(request,algo):

    print("Running algorithm {}".format(algo))
    ret_val = exe_bh(dict(request),algo)
    return ret_val

@shared_task
def test_task():
    return "Task executed successfully"