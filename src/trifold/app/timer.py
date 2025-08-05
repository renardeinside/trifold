from trifold.app.config import rt
from typing import Callable
import time
import functools

def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        # Calculate duration in milliseconds
        duration_ms = (end_time - start_time) * 1000
        
        # Format nicely based on duration
        if duration_ms < 1:
            duration_str = f"{duration_ms:.3f}ms"
        elif duration_ms < 100:
            duration_str = f"{duration_ms:.2f}ms"
        elif duration_ms < 1000:
            duration_str = f"{duration_ms:.1f}ms"
        else:
            # For longer durations, also show seconds
            duration_str = f"{duration_ms:.0f}ms ({duration_ms/1000:.2f}s)"
        
        rt.logger.info(f"{func.__name__} completed in {duration_str}")
        return result
    return wrapper