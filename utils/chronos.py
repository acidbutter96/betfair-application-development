import time


def chronometer(start: float) -> str:
    end = time.time()
    hours, remain = divmod(end - start, 60**2)
    minutes, seconds = divmod(remain, 60)
    if hours == 0 and minutes == 0:
        return f"{round(seconds,1)}s"
    elif hours == 0:
        return f"{int(minutes)}min {round(seconds,1)}s"
    else:
        return f"{int(hours)}h{int(minutes)}min {round(seconds,1)}s"
