from logging import Logger


def get_exceptions(f, *args, **kwargs):
    def wrapper(f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as ex:
            if "logger" in kwargs.keys():
                kwargs.get("logger").exception(ex)
                ex = f"{ex}\nNo logger loaded"
            raise Exception(ex)
    return wrapper
