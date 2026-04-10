"""
Rate limiting simple basado en sesión
"""
from functools import wraps
from flask import session, flash, redirect, url_for, request
from datetime import datetime, timedelta
from collections import defaultdict

# Almacenamiento en memoria (usar Redis en producción)
_rate_limits = defaultdict(list)

def rate_limit(max_requests, window_seconds):
    """
    Decorador simple de rate limiting
    
    Args:
        max_requests: Número máximo de requests
        window_seconds: Ventana de tiempo en segundos
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return f(*args, **kwargs)
            
            key = f"{f.__name__}:{user_id}"
            now = datetime.now()
            cutoff = now - timedelta(seconds=window_seconds)
            
            # Limpiar requests antiguos
            _rate_limits[key] = [ts for ts in _rate_limits[key] if ts > cutoff]
            
            # Verificar límite
            if len(_rate_limits[key]) >= max_requests:
                flash(f'Demasiadas solicitudes. Intenta en {window_seconds//60} minutos.', 'warning')
                return redirect(request.referrer or url_for('solicitudes.index'))
            
            # Registrar request
            _rate_limits[key].append(now)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
