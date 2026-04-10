"""
Script para poblar la base de conocimiento con artículos iniciales
"""
from app import create_app, db
from models import ArticuloKB, Usuario

app = create_app()

articulos_iniciales = [
    {
        'titulo': '¿Cómo crear un ticket?',
        'contenido': '''
# Crear un Ticket en NDDesk

## Pasos para crear un ticket:

1. **Accede al sistema** con tu usuario y contraseña
2. Click en **"Nuevo Ticket"** o el botón **"+"**
3. Completa los campos requeridos:
   - **Fecha de publicación**: Cuándo se publicará el contenido
   - **Prioridad**: Baja, Media, Alta o Urgente
   - **Medio**: Nuestro Diario o Soy502
   - **Sección**: Área que manejará el ticket
   - **Familia de Servicios**: Digital o Impreso
   - **Subcategoría**: Tipo específico de contenido
   - **Descripción**: Detalla tu solicitud

4. El **email de notificación** se llena automáticamente según la sección
5. Click en **"Crear Ticket"**

## Importante:
- Proporciona todos los detalles necesarios en la descripción
- El ticket se asigna automáticamente al equipo correspondiente
- Recibirás notificaciones por email sobre el progreso
        ''',
        'categoria': 'Tickets',
        'tags': 'crear,ticket,nuevo,solicitud',
        'estado': 'publicado'
    },
    {
        'titulo': '¿Cómo gestionar usuarios y roles?',
        'contenido': '''
# Gestión de Usuarios en NDDesk

## Roles disponibles:
- **Admin**: Acceso total al sistema
- **Coordinador**: Gestiona tickets y usuarios
- **Resolutor**: Atiende tickets de su sección
- **Solicitante**: Crea y consulta sus tickets

## Crear un usuario (Solo Admin):
1. Ve a **Usuarios** → **+ Nuevo Usuario**
2. Completa:
   - Username (email corporativo)
   - Nombre completo
   - Rol
   - Departamento
   - Secciones asignadas
3. Guarda

## Editar usuario:
1. Ve a **Usuarios**
2. Click en el botón de editar (lápiz)
3. Modifica los datos necesarios
4. Guarda cambios

## Eliminar/Reactivar:
- Al eliminar un usuario, se hace "soft delete"
- Si intentas crear un usuario con el mismo username, se reactiva automáticamente
        ''',
        'categoria': 'Administración',
        'tags': 'usuarios,roles,permisos,admin',
        'estado': 'publicado'
    },
    {
        'titulo': '¿Cómo configurar secciones y emails?',
        'contenido': '''
# Configuración de Secciones

## Crear una sección:
1. Ve a **Secciones** → **+ Nueva**
2. Completa:
   - **Nombre**: Nombre de la sección
   - **Medio**: Nuestro Diario o Soy502
   - **Email**: Correo del grupo (ej: digital.tickets@nuestrodiario.com.gt)
3. Guarda

## Funcionamiento automático:
- Cuando se crea un ticket de esa sección, el email se llena automáticamente
- Las notificaciones se envían al email del grupo configurado
- El grupo de Zoho Mail distribuye a todos los miembros

## Emails de grupo recomendados:
- digital.tickets@nuestrodiario.com.gt
- deportes.tickets@nuestrodiario.com.gt
- softnews.tickets@nuestrodiario.com.gt
- marketing.tickets@nuestrodiario.com.gt
- regionales.tickets@nuestrodiario.com.gt
- metro.tickets@nuestrodiario.com.gt
- s502.tickets@soy502.com
        ''',
        'categoria': 'Configuración',
        'tags': 'secciones,email,notificaciones,configurar',
        'estado': 'publicado'
    },
    {
        'titulo': 'Estados de tickets',
        'contenido': '''
# Estados de Tickets en NDDesk

## Estados disponibles:

### Pendiente
- Ticket recién creado
- Esperando asignación o inicio de trabajo

### Planificado
- Ticket asignado y programado
- En cola para ser trabajado

### En Proceso
- Resolutor trabajando activamente en el ticket

### Solucionado
- Trabajo completado
- Esperando validación del solicitante

### Cerrado
- Ticket finalizado y validado
- No requiere más acciones

### Escalado
- Requiere atención de nivel superior
- Problemas complejos o urgentes

## Transiciones permitidas:
- Pendiente → Planificado, En Proceso
- Planificado → En Proceso, Pendiente
- En Proceso → Solucionado, Pendiente
- Solucionado → Cerrado
- Cerrado → Pendiente (reapertura)
        ''',
        'categoria': 'Tickets',
        'tags': 'estados,workflow,proceso',
        'estado': 'publicado'
    },
    {
        'titulo': '¿Cómo cambiar mi contraseña?',
        'contenido': '''
# Cambiar Contraseña

## Primera vez (contraseña temporal):
1. Inicia sesión con la contraseña temporal
2. El sistema te redirigirá automáticamente
3. Ingresa:
   - Contraseña actual (temporal)
   - Nueva contraseña
   - Confirma nueva contraseña
4. Guarda

## Cambio posterior:
1. Click en tu nombre (esquina superior derecha)
2. Selecciona **"Cambiar Contraseña"**
3. Completa el formulario
4. Guarda

## Requisitos de contraseña:
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Al menos un carácter especial
        ''',
        'categoria': 'Cuenta',
        'tags': 'contraseña,password,seguridad,cambiar',
        'estado': 'publicado'
    }
]

with app.app_context():
    # Obtener admin
    admin = Usuario.query.filter_by(username='admin').first()
    
    if not admin:
        print("Error: Usuario admin no encontrado")
        exit(1)
    
    # Verificar si ya existen artículos
    if ArticuloKB.query.count() > 0:
        print("Ya existen artículos en la base de conocimiento")
        respuesta = input("¿Deseas agregar más artículos? (s/n): ")
        if respuesta.lower() != 's':
            exit(0)
    
    # Crear artículos
    for art_data in articulos_iniciales:
        # Verificar si ya existe
        existe = ArticuloKB.query.filter_by(titulo=art_data['titulo']).first()
        if existe:
            print(f"✓ Ya existe: {art_data['titulo']}")
            continue
        
        articulo = ArticuloKB(
            titulo=art_data['titulo'],
            contenido=art_data['contenido'],
            categoria=art_data['categoria'],
            tags=art_data['tags'],
            autor_id=admin.id,
            estado=art_data['estado']
        )
        db.session.add(articulo)
        print(f"✓ Creado: {art_data['titulo']}")
    
    db.session.commit()
    print(f"\n✅ Base de conocimiento poblada con {len(articulos_iniciales)} artículos")
