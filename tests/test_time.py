import datetime
import time


def test_time():
    assert (int(datetime.datetime.now().timestamp()) - int(time.time())) < 5
