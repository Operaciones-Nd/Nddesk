"""
Middleware para manejar reintentos de base de datos
"""
from sqlalchemy.exc import OperationalError
from functools import wraps
import time

def retry_on_db_lock(max_retries=3, delay=0.5):
    """Decorator para reintentar operaciones cuando la BD está bloqueada"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return f(*args, **kwargs)
                except OperationalError as e:
                    if 'database is locked' in str(e).lower():
                        retries += 1
                        if retries >= max_retries:
                            raise
                        time.sleep(delay * retries)
                    else:
                        raise
            return f(*args, **kwargs)
        return wrapper
    return decorator
