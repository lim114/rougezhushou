"""Thread-local physical coordinates for native Windows geometry reads."""
import ctypes
from contextlib import contextmanager
from functools import lru_cache


@lru_cache(maxsize=1)
def thread_dpi_api():
    switch = ctypes.WinDLL('user32', use_last_error=True).SetThreadDpiAwarenessContext
    switch.argtypes = [ctypes.c_void_p]
    switch.restype = ctypes.c_void_p
    return switch


@contextmanager
def physical_pixels():
    switch = thread_dpi_api()
    prior = switch(ctypes.c_void_p(-4))
    try:
        yield
    finally:
        if prior:
            switch(prior)
