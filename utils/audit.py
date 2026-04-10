"""
Sistema de auditoría automática
"""
from functools import wraps
from flask import session, request
from models import AuditoriaTicket, db
from datetime import datetime
import json

def audit_action(action_type, resource_type='ticket'):
    """Decorator para auditoría automática de acciones"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Ejecutar función
            result = f(*args, **kwargs)
            
            # Registrar auditoría
            try:
                if session.get('user_id'):
                    audit = AuditoriaTicket(
                        ticket_id=kwargs.get('id'),
                        usuario_id=session['user_id'],
                        accion=action_type,
                        ip_address=request.remote_addr,
                        campo_modificado=resource_type,
                        valor_nuevo=json.dumps(request.form.to_dict(), default=str)[:500]
                    )
                    db.session.add(audit)
                    db.session.commit()
            except Exception as e:
                # No fallar si auditoría falla
                pass
            
            return result
        return decorated
    return decorator
