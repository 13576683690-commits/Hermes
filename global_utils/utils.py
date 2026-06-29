from loguru import logger
import multiprocessing as mp


def trace(func):
    @logger.catch()
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info(
            f"Called function {func.__name__} with args {args} and kwargs {kwargs}."
        )
        logger.info(f"Returned {result}.")
        return result

    return wrapper

import concurrent.futures as cf

def timeout_handler(fn, args=(), kwargs=None, timeout_duration=None, default=None):
    """
    Soft timeout using a thread. No multiprocessing.
    Returns `default` if the timeout is hit.
    """
    with cf.ThreadPoolExecutor(max_workers=1, thread_name_prefix="timeout") as ex:
        fut = ex.submit(fn, *(args or ()), **(kwargs or {}))
        try:
            return fut.result(timeout=timeout_duration)
        except cf.TimeoutError:
            return default


def call_scheduler(scheduler_input, scheduler):
    request_id_list = scheduler.submit_all_request(scheduler_input)
    outputs_list = scheduler.get_all_request_outputs(request_id_list)

    return outputs_list


def call_scheduler_with_timeout(scheduler_input, scheduler):
    return timeout_handler(
        call_scheduler, args=(scheduler_input, scheduler), timeout_duration=600, default=[]
    )
