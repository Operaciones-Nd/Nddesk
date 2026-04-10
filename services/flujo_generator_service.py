from models import Flujo, Transicion, db
import json

class FlujoGeneratorService:
    
    PLANTILLAS = {
        'simple': {
            'estados': ['Pendiente', 'Solucionado', 'Cerrado'],
            'transiciones': [
                {'origen': 'Pendiente', 'destino': 'Solucionado', 'nombre': 'Resolver', 'comentario': True, 'adjunto': False, 'roles': 'resolutor,coordinador,admin'},
                {'origen': 'Solucionado', 'destino': 'Cerrado', 'nombre': 'Cerrar', 'comentario': True, 'adjunto': False, 'roles': 'coordinador,admin'}
            ]
        },
        'completo': {
            'estados': ['Pendiente', 'Planificado', 'En Progreso', 'Solucionado', 'Cerrado'],
            'transiciones': [
                {'origen': 'Pendiente', 'destino': 'Planificado', 'nombre': 'Planificar', 'comentario': True, 'adjunto': False, 'roles': 'resolutor,coordinador,admin'},
                {'origen': 'Planificado', 'destino': 'En Progreso', 'nombre': 'Iniciar', 'comentario': True, 'adjunto': False, 'roles': 'resolutor,coordinador,admin'},
                {'origen': 'En Progreso', 'destino': 'Solucionado', 'nombre': 'Resolver', 'comentario': True, 'adjunto': True, 'roles': 'resolutor,coordinador,admin'},
                {'origen': 'Solucionado', 'destino': 'Cerrado', 'nombre': 'Cerrar', 'comentario': True, 'adjunto': False, 'roles': 'coordinador,admin'}
            ]
        },
        'aprobacion': {
            'estados': ['Pendiente', 'En Revisión', 'Aprobado', 'Rechazado', 'En Ejecución', 'Cerrado'],
            'transiciones': [
                {'origen': 'Pendiente', 'destino': 'En Revisión', 'nombre': 'Enviar a revisión', 'comentario': True, 'adjunto': True, 'roles': 'resolutor,coordinador,admin'},
                {'origen': 'En Revisión', 'destino': 'Aprobado', 'nombre': 'Aprobar', 'comentario': True, 'adjunto': False, 'roles': 'coordinador,admin'},
                {'origen': 'En Revisión', 'destino': 'Rechazado', 'nombre': 'Rechazar', 'comentario': True, 'adjunto': False, 'roles': 'coordinador,admin'},
                {'origen': 'Aprobado', 'destino': 'En Ejecución', 'nombre': 'Ejecutar', 'comentario': True, 'adjunto': False, 'roles': 'resolutor,coordinador,admin'},
                {'origen': 'En Ejecución', 'destino': 'Cerrado', 'nombre': 'Finalizar', 'comentario': True, 'adjunto': True, 'roles': 'resolutor,coordinador,admin'}
            ]
        }
    }
    
    @staticmethod
    def generar_desde_texto(instruccion, tipo_ticket):
        """Genera flujo desde instrucción en lenguaje natural"""
        instruccion_lower = instruccion.lower()
        
        # Detectar plantilla
        if 'simple' in instruccion_lower or 'básico' in instruccion_lower or 'rapido' in instruccion_lower:
            plantilla = 'simple'
            nombre = f'Flujo Simple - {tipo_ticket}'
            descripcion = 'Flujo rápido con estados mínimos'
        elif 'aprobación' in instruccion_lower or 'aprobar' in instruccion_lower or 'revisar' in instruccion_lower:
            plantilla = 'aprobacion'
            nombre = f'Flujo con Aprobación - {tipo_ticket}'
            descripcion = 'Flujo que requiere aprobación antes de ejecutar'
        else:
            plantilla = 'completo'
            nombre = f'Flujo Completo - {tipo_ticket}'
            descripcion = 'Flujo estándar con todos los estados'
        
        return FlujoGeneratorService.crear_flujo(nombre, tipo_ticket, descripcion, plantilla)
    
    @staticmethod
    def crear_flujo(nombre, tipo_ticket, descripcion, plantilla_key):
        """Crea flujo desde plantilla"""
        plantilla = FlujoGeneratorService.PLANTILLAS.get(plantilla_key, FlujoGeneratorService.PLANTILLAS['completo'])
        
        flujo = Flujo(
            nombre=nombre,
            tipo_ticket=tipo_ticket,
            descripcion=descripcion,
            activo=True
        )
        db.session.add(flujo)
        db.session.flush()
        
        for trans_data in plantilla['transiciones']:
            trans = Transicion(
                flujo_id=flujo.id,
                estado_origen=trans_data['origen'],
                estado_destino=trans_data['destino'],
                nombre=trans_data['nombre'],
                requiere_comentario=trans_data['comentario'],
                requiere_adjunto=trans_data['adjunto'],
                roles_permitidos=trans_data['roles']
            )
            db.session.add(trans)
        
        db.session.commit()
        return flujo
