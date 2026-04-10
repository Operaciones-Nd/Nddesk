from models.base import BaseModel, db
import json

class Flujo(BaseModel):
    __tablename__ = 'flujos'
    
    nombre = db.Column(db.String(100), nullable=False)
    tipo_ticket = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    @classmethod
    def get_by_tipo(cls, tipo_ticket):
        return cls.query.filter_by(tipo_ticket=tipo_ticket, activo=True).first()

class Transicion(BaseModel):
    __tablename__ = 'transiciones'
    
    flujo_id = db.Column(db.Integer, db.ForeignKey('flujos.id'), nullable=False)
    estado_origen = db.Column(db.String(50), nullable=False)
    estado_destino = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    condiciones = db.Column(db.Text)
    requiere_comentario = db.Column(db.Boolean, default=False)
    requiere_adjunto = db.Column(db.Boolean, default=False)
    roles_permitidos = db.Column(db.String(200))
    
    flujo = db.relationship('Flujo', backref='transiciones')
    
    def puede_ejecutar(self, usuario, ticket):
        if self.roles_permitidos:
            roles = self.roles_permitidos.split(',')
            if usuario.rol not in roles:
                return False
        
        if self.condiciones:
            try:
                cond = json.loads(self.condiciones)
                for campo, valor in cond.items():
                    if getattr(ticket, campo, None) != valor:
                        return False
            except:
                pass
        
        return True

class ReglaAutomatizacion(BaseModel):
    __tablename__ = 'reglas_automatizacion'
    
    nombre = db.Column(db.String(100), nullable=False)
    tipo_ticket = db.Column(db.String(50))
    condiciones = db.Column(db.Text, nullable=False)
    acciones = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    @classmethod
    def evaluar(cls, ticket):
        reglas = cls.query.filter_by(activo=True).all()
        for regla in reglas:
            if regla.tipo_ticket and regla.tipo_ticket != ticket.tipo_ticket:
                continue
            
            try:
                cond = json.loads(regla.condiciones)
                if cls._evaluar_condiciones(cond, ticket):
                    cls._ejecutar_acciones(json.loads(regla.acciones), ticket)
            except:
                pass
    
    @staticmethod
    def _evaluar_condiciones(cond, ticket):
        campo = cond.get('campo')
        operador = cond.get('operador')
        valor = cond.get('valor')
        
        valor_ticket = getattr(ticket, campo, None)
        
        if operador == '==':
            return valor_ticket == valor
        elif operador == '!=':
            return valor_ticket != valor
        elif operador == 'in':
            return valor_ticket in valor
        
        return False
    
    @staticmethod
    def _ejecutar_acciones(acciones, ticket):
        from models.base import db
        
        for accion in acciones:
            tipo = accion.get('tipo')
            
            if tipo == 'cambiar_campo':
                setattr(ticket, accion['campo'], accion['valor'])
            elif tipo == 'escalar':
                from services import EscalamientoService
                EscalamientoService.escalar_ticket(
                    ticket.id, accion['nivel'], accion['grupo'], 
                    'Escalamiento automático', 'automatico'
                )
        
        db.session.commit()
