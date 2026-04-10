"""
Script para poblar la Base de Conocimientos con artículos de ayuda
"""
from app import create_app
from models import db, ArticuloKB, Usuario

app = create_app()

ARTICULOS = [
    {
        "titulo": "Cómo cambiar mi contraseña",
        "categoria": "Usuario",
        "tags": "contraseña, password, seguridad, cambiar",
        "contenido": """# Cómo cambiar mi contraseña

Para cambiar tu contraseña en el sistema, sigue estos pasos:

1️⃣ Haz clic en tu perfil (icono de usuario) en la esquina superior derecha
2️⃣ Selecciona "Cambiar Contraseña" del menú desplegable
3️⃣ Ingresa tu contraseña actual
4️⃣ Ingresa tu nueva contraseña (debe cumplir con los requisitos de seguridad)
5️⃣ Confirma tu nueva contraseña
6️⃣ Haz clic en "Guardar cambios"

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 minúscula
- Al menos 1 número
- Al menos 1 carácter especial

**Nota:** Por seguridad, se te pedirá cambiar tu contraseña periódicamente.
"""
    },
    {
        "titulo": "Cómo crear un ticket",
        "categoria": "Tickets",
        "tags": "ticket, solicitud, crear, nuevo, requerimiento",
        "contenido": """# Cómo crear un ticket

Para crear una nueva solicitud o ticket:

1️⃣ Ve al menú lateral y haz clic en "Nueva Solicitud"
2️⃣ Completa el formulario con la información requerida:
   - Fecha de publicación
   - Medio (Impreso, Digital, Redes Sociales)
   - Departamento
   - Sección
   - Tipo de contenido
   - Descripción detallada

3️⃣ Selecciona la prioridad:
   - **Alta**: Urgente, requiere atención inmediata
   - **Media**: Prioridad normal
   - **Baja**: No urgente

4️⃣ Haz clic en "Crear Solicitud"

El sistema asignará automáticamente el ticket al grupo correspondiente según la sección seleccionada.

**Tip:** Sé lo más específico posible en la descripción para que el equipo pueda atender tu solicitud rápidamente.
"""
    },
    {
        "titulo": "Estados de tickets explicados",
        "categoria": "Tickets",
        "tags": "estados, status, pendiente, planificado, solucionado, cerrado",
        "contenido": """# Estados de tickets explicados

Los tickets en el sistema pueden tener los siguientes estados:

## 🟡 Pendiente
El ticket ha sido creado y está esperando ser asignado o revisado por el equipo.

## 🔵 Planificado
El equipo ha revisado el ticket y está trabajando en él. Ya tiene un plan de acción.

## 🟢 Solucionado
El ticket ha sido resuelto. El solicitante puede revisar la solución y dar feedback.

## ⚫ Cerrado
El ticket está completamente finalizado y archivado. No se pueden hacer más cambios.

## 🟣 Escalado
El ticket requiere atención de un nivel superior o de otro departamento.

**Nota:** Solo los coordinadores y administradores pueden cerrar tickets definitivamente.
"""
    },
    {
        "titulo": "Roles y permisos del sistema",
        "categoria": "Seguridad",
        "tags": "roles, permisos, admin, coordinador, resolutor, solicitante",
        "contenido": """# Roles y permisos

El sistema tiene 4 roles principales:

## 👤 Solicitante
- Puede crear tickets
- Puede ver sus propios tickets
- Puede comentar en sus tickets
- **No puede** editar ni cerrar tickets

## 🔧 Resolutor
- Puede ver tickets de su sección
- Puede editar tickets asignados
- Puede cambiar estados
- Puede cerrar tickets
- Puede ver bitácoras internas

## 👨💼 Coordinador
- Puede ver todos los tickets
- Puede editar cualquier ticket
- Puede asignar y reasignar tickets
- Puede gestionar usuarios
- Puede generar reportes
- Puede gestionar turnos

## ⚙️ Administrador
- Acceso completo al sistema
- Puede gestionar usuarios y roles
- Puede configurar el sistema
- Puede ver auditorías
- Puede gestionar secciones y departamentos

**Nota:** Si necesitas cambiar tu rol, contacta al administrador.
"""
    },
    {
        "titulo": "Cómo usar los filtros del dashboard",
        "categoria": "Tickets",
        "tags": "filtros, buscar, dashboard, busqueda",
        "contenido": """# Cómo usar los filtros del dashboard

El dashboard tiene filtros avanzados para encontrar tickets rápidamente:

## Filtros disponibles

### Por Estado
Filtra tickets por: Pendiente, Planificado, Solucionado, Cerrado, Escalado

### Por Prioridad
Filtra por: Alta, Media, Baja

### Por Sección
Filtra por la sección que creó el ticket

### Por Fecha
Selecciona un rango de fechas (Desde/Hasta)

### Búsqueda rápida
- Escribe `#123` para buscar el ticket con ID 123
- Escribe texto libre para buscar en descripción, sección y solicitante

## Tabs organizados
- **Activos**: Tickets pendientes, planificados y escalados de últimos 30 días
- **Solucionados**: Tickets resueltos
- **Cerrados**: Tickets finalizados
- **Histórico**: Todos los tickets sin restricción

**Tip:** Puedes combinar múltiples filtros para búsquedas más específicas.
"""
    },
    {
        "titulo": "Cómo crear un usuario (Admin)",
        "categoria": "Administración",
        "tags": "usuario, crear, admin, administrador, nuevo",
        "contenido": """# Cómo crear un usuario

**Rol requerido:** Administrador o Coordinador

Para crear un nuevo usuario en el sistema:

1️⃣ Ve al menú lateral y haz clic en "Usuarios"
2️⃣ Haz clic en el botón "Nuevo Usuario"
3️⃣ Completa el formulario:
   - **Nombre completo**: Nombre del usuario
   - **Username**: Nombre de usuario para login (sin espacios)
   - **Rol**: Selecciona el rol apropiado
     - Solicitante: Solo crea tickets
     - Resolutor: Atiende tickets de su sección
     - Coordinador: Gestiona tickets y usuarios
     - Administrador: Acceso completo
   - **Departamento**: Departamento al que pertenece
   - **Sección**: Sección(es) que puede atender (solo para resolutores)

4️⃣ Haz clic en "Crear Usuario"

**Nota importante:**
- El sistema generará una contraseña temporal
- El usuario deberá cambiarla en su primer inicio de sesión
- Comunica las credenciales al usuario de forma segura

**Tip:** Asigna el rol más restrictivo necesario para las funciones del usuario.
"""
    },
    {
        "titulo": "Cómo gestionar turnos (Coordinador)",
        "categoria": "Administración",
        "tags": "turnos, coordinador, gestionar, asignar",
        "contenido": """# Cómo gestionar turnos

**Rol requerido:** Coordinador o Administrador

Para gestionar los turnos de trabajo:

## Crear un turno

1️⃣ Ve al menú lateral y haz clic en "Turnos"
2️⃣ Haz clic en "Nuevo Turno"
3️⃣ Completa la información:
   - **Sección**: Selecciona la sección
   - **Usuario**: Selecciona el resolutor
   - **Fecha inicio**: Fecha de inicio del turno
   - **Fecha fin**: Fecha de finalización del turno
   - **Activo**: Marca si el turno está activo

4️⃣ Haz clic en "Guardar"

## Ver turnos activos

- En la página de Turnos verás todos los turnos programados
- Los turnos activos se muestran destacados
- Puedes filtrar por sección o usuario

## Editar un turno

1️⃣ En la lista de turnos, haz clic en "Editar"
2️⃣ Modifica la información necesaria
3️⃣ Haz clic en "Guardar cambios"

## Desactivar un turno

1️⃣ Edita el turno
2️⃣ Desmarca la opción "Activo"
3️⃣ Guarda los cambios

**Nota:** Los turnos ayudan a organizar la asignación automática de tickets según el personal disponible.
"""
    },
    {
        "titulo": "Cómo editar un ticket",
        "categoria": "Tickets",
        "tags": "editar, ticket, modificar, actualizar",
        "contenido": """# Cómo editar un ticket

**Rol requerido:** Resolutor, Coordinador o Administrador

Para editar un ticket existente:

1️⃣ Abre el ticket que deseas editar
2️⃣ Haz clic en el botón "Editar"
3️⃣ Modifica los campos necesarios:
   - **Estado**: Cambia el estado del ticket
   - **Prioridad**: Ajusta la prioridad
   - **Solución**: Describe la solución implementada
   - **Bitácora pública**: Información visible para el solicitante
   - **Bitácora interna**: Notas internas del equipo

4️⃣ Haz clic en "Guardar cambios"

## Cambiar estado

Puedes cambiar el estado directamente:
- **Pendiente → Planificado**: Cuando empiezas a trabajar en él
- **Planificado → Solucionado**: Cuando lo resuelves
- **Solucionado → Cerrado**: Solo coordinadores/admin

## Reasignar ticket

Solo coordinadores y administradores pueden reasignar:
1️⃣ En la vista del ticket, busca "Reasignar"
2️⃣ Selecciona el nuevo resolutor
3️⃣ Confirma la reasignación

**Nota:** Los tickets cerrados no se pueden editar.
"""
    },
    {
        "titulo": "Cómo cerrar un ticket",
        "categoria": "Tickets",
        "tags": "cerrar, ticket, finalizar, completar",
        "contenido": """# Cómo cerrar un ticket

**Rol requerido:** Resolutor, Coordinador o Administrador

Para cerrar un ticket:

1️⃣ Abre el ticket que deseas cerrar
2️⃣ Asegúrate de que el ticket esté en estado "Solucionado"
3️⃣ Haz clic en el botón "Cerrar Ticket"
4️⃣ En el modal de cierre, completa:
   - **Estado de publicación**: Selecciona si fue publicado o no
   - **Comentarios**: Agrega comentarios finales si es necesario

5️⃣ Haz clic en "Cerrar definitivamente"

## Importante

- Un ticket cerrado **NO se puede reabrir** fácilmente
- Solo cierra tickets cuando estés completamente seguro
- Asegúrate de que la solución esté documentada
- Verifica que el solicitante esté satisfecho

## Antes de cerrar

✅ Verifica que la solución esté completa
✅ Confirma que el solicitante está satisfecho
✅ Documenta la solución en la bitácora
✅ Marca el estado de publicación correcto

**Nota:** Los coordinadores y administradores pueden reabrir tickets cerrados si es necesario.
"""
    }
]

def poblar_kb():
    with app.app_context():
        # Buscar usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            print("❌ Usuario admin no encontrado")
            return
        
        print("📚 Poblando Base de Conocimientos...")
        
        for art_data in ARTICULOS:
            # Verificar si ya existe
            existe = ArticuloKB.query.filter_by(titulo=art_data['titulo']).first()
            if existe:
                print(f"⏭️  Ya existe: {art_data['titulo']}")
                continue
            
            articulo = ArticuloKB(
                titulo=art_data['titulo'],
                contenido=art_data['contenido'],
                categoria=art_data['categoria'],
                tags=art_data['tags'],
                autor_id=admin.id,
                estado='publicado'
            )
            
            db.session.add(articulo)
            print(f"✅ Creado: {art_data['titulo']}")
        
        db.session.commit()
        print(f"\n🎉 Base de Conocimientos poblada con {len(ARTICULOS)} artículos")

if __name__ == '__main__':
    poblar_kb()
