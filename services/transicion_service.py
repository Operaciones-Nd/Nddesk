"""
Servicio de validación de transiciones de estado
"""
from utils.validators import ValidationError

class TransicionService:
    """Valida transiciones de estado de tickets"""
    
    TRANSICIONES_VALIDAS = {
        'Pendiente': ['Planificado', 'Escalado', 'Solucionado', 'Cerrado'],
        'Planificado': ['Solucionado', 'Escalado', 'Pendiente'],
        'Escalado': ['Planificado', 'Solucionado'],
        'Solucionado': ['Cerrado', 'Pendiente'],
        'Cerrado': []  # No se puede cambiar desde cerrado
    }
    
    @staticmethod
    def validar_transicion(estado_actual, estado_nuevo):
        """
        Valida si una transición de estado es válida
        
        Args:
            estado_actual: Estado actual del ticket
            estado_nuevo: Estado al que se quiere cambiar
            
        Raises:
            ValidationError: Si la transición no es válida
        """
        if estado_actual == estado_nuevo:
            return True
        
        estados_permitidos = TransicionService.TRANSICIONES_VALIDAS.get(estado_actual, [])
        
        if estado_nuevo not in estados_permitidos:
            raise ValidationError(
                f'Transición inválida: {estado_actual} → {estado_nuevo}. '
                f'Estados permitidos: {", ".join(estados_permitidos) if estados_permitidos else "ninguno"}'
            )
        
        return True
    
    @staticmethod
    def puede_reabrir(estado_actual):
        """Verifica si un ticket puede ser reabierto"""
        return estado_actual == 'Cerrado'
