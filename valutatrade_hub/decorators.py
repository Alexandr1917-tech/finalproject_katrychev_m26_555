from functools import wraps

from valutatrade_hub.logging_config import logger


def log_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.info(f"{action_name} result=OK")
                return result
            except Exception as e:
                logger.error(f"{action_name} result=ERROR error_type={type(e).__name__} error_message={e}") # noqa: E501
                raise 
        return wrapper
    return decorator