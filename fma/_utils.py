from contextlib import contextmanager

import httpx


@contextmanager
def httpx_error_handling():
    """Context manager to handle httpx errors"""
    try:
        yield
    except httpx.HTTPStatusError as errh:
        status = errh.response.status_code
        if status == 403:
            print("ERROR: You need to authenticated first! Run `fma login`")
        elif status == 400:
            print("ERROR: Some of the provided arguments were incorrect!")
        else:
            print("ERROR: We encountered an HTTP error: ", errh)
        exit()
    except httpx.ConnectError as errc:
        print("ERROR: We are having trouble connecting:", errc)
        exit()
    except httpx.ReadTimeout as errt:
        print("ERROR: The request to the model has timed out:", errt)
        exit()
    except httpx.RequestError as err:
        print("ERROR: Something went wrong, please try again:", err)
        exit()


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
