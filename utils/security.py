from datetime import datetime, timedelta
from models import IntentoLogin, db

class SecurityHelper:
    @staticmethod
    def check_login_attempts(username, max_attempts, block_time):
        try:
            intentos = IntentoLogin.query.filter_by(
                username=username,
                exitoso=False
            ).filter(
                IntentoLogin.created_at >= datetime.now() - block_time
            ).count()
            
            if intentos >= max_attempts:
                ultimo = IntentoLogin.query.filter_by(username=username).order_by(
                    IntentoLogin.created_at.desc()
                ).first()
                if ultimo and ultimo.bloqueado_hasta and ultimo.bloqueado_hasta > datetime.now():
                    return False, ultimo.bloqueado_hasta
            return True, None
        except Exception:
            # Si hay error en BD, permitir login
            return True, None
    
    @staticmethod
    def register_login_attempt(username, exitoso, ip_address, block_time=None):
        try:
            intento = IntentoLogin(
                username=username,
                exitoso=exitoso,
                ip_address=ip_address,
                bloqueado_hasta=datetime.now() + block_time if not exitoso and block_time else None
            )
            db.session.add(intento)
            db.session.commit()
        except Exception:
            # Si falla el registro, no bloquear el login
            db.session.rollback()
            pass
