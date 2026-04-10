# GUÍA DE DESPLIEGUE EN INSTANCIA

## 1. Preparar el servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib -y
```

## 2. Configurar PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER nddesk_user WITH PASSWORD 'TuPasswordSeguro123!';
CREATE DATABASE nddesk_db OWNER nddesk_user;
GRANT ALL PRIVILEGES ON DATABASE nddesk_db TO nddesk_user;
\q
EOF
```

## 3. Subir la aplicación

```bash
# Clonar o copiar archivos al servidor
cd /var/www/
sudo mkdir nddesk
sudo chown $USER:$USER nddesk
cd nddesk

# Copiar archivos (usa scp, git, etc.)
```

## 4. Configurar entorno

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

## 5. Configurar .env en el servidor

```bash
nano .env
```

Contenido:
```
SECRET_KEY=genera-clave-segura-con-openssl-rand-hex-32
DATABASE_URL=postgresql://nddesk_user:TuPasswordSeguro123!@localhost:5432/nddesk_db
FLASK_ENV=production
DEFAULT_USER_PASSWORD=Admin123!

MAIL_SERVER=smtppro.zoho.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=nddesk.ti@nuestrodiario.com.gt
MAIL_PASSWORD=009WAM5ZJRbt
MAIL_DEFAULT_SENDER=nddesk.ti@nuestrodiario.com.gt
```

## 6. Inicializar base de datos

```bash
python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Base de datos creada")
EOF
```

## 7. Configurar Gunicorn

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/nddesk.service
```

Contenido:
```ini
[Unit]
Description=NDDesk ITSM Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/nddesk
Environment="PATH=/var/www/nddesk/venv/bin"
ExecStart=/var/www/nddesk/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5005 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl start nddesk
sudo systemctl enable nddesk
```

## 8. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/nddesk
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/nddesk/static;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/nddesk /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 9. SSL (Opcional pero recomendado)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

## 10. Verificar

```bash
# Ver logs
sudo journalctl -u nddesk -f

# Estado del servicio
sudo systemctl status nddesk
```

## RESUMEN RÁPIDO

La app funciona con:
- ✅ SQLite en desarrollo (local)
- ✅ PostgreSQL en producción (instancia)
- ✅ Solo cambias DATABASE_URL en .env
- ✅ Todo lo demás es igual
