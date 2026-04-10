"""
Middleware de seguridad avanzada
"""
from functools import wraps
from flask import request, jsonify, current_app
import hashlib
import hmac
import time

class SecurityMiddleware:
    
    @staticmethod
    def validate_request_signature(f):
        """Valida firma de requests críticos"""
        @wraps(f)
        def decorated(*args, **kwargs):
            if current_app.config.get('REQUIRE_REQUEST_SIGNATURE'):
                signature = request.headers.get('X-Request-Signature')
                if not signature:
                    return jsonify({'error': 'Firma requerida'}), 401
                
                # Validar firma
                expected = hmac.new(
                    current_app.config['SECRET_KEY'].encode(),
                    request.get_data(),
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected):
                    current_app.logger.warning(f'Firma inválida desde {request.remote_addr}')
                    return jsonify({'error': 'Firma inválida'}), 401
            
            return f(*args, **kwargs)
        return decorated
    
    @staticmethod
    def prevent_timing_attacks(f):
        """Previene timing attacks en operaciones sensibles"""
        @wraps(f)
        def decorated(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            
            # Agregar delay aleatorio para prevenir timing attacks
            elapsed = time.time() - start
            if elapsed < 0.1:
                time.sleep(0.1 - elapsed)
            
            return result
        return decorated
    
    @staticmethod
    def sanitize_response(data):
        """Sanitiza respuestas para prevenir data leakage"""
        if isinstance(data, dict):
            # Remover campos sensibles
            sensitive_fields = ['password', 'password_hash', 'secret', 'token', 'api_key']
            return {k: v for k, v in data.items() if k not in sensitive_fields}
        return data
