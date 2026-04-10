#!/bin/bash

echo "=== Instalando PostgreSQL ==="
brew install postgresql@14

echo "=== Iniciando PostgreSQL ==="
brew services start postgresql@14

echo "=== Esperando que PostgreSQL inicie ==="
sleep 5

echo "=== Creando base de datos ==="
/usr/local/opt/postgresql@14/bin/createdb nddesk_db

echo "=== Creando usuario ==="
/usr/local/opt/postgresql@14/bin/psql -d nddesk_db -c "CREATE USER nddesk_user WITH PASSWORD 'nddesk_pass';"
/usr/local/opt/postgresql@14/bin/psql -d nddesk_db -c "GRANT ALL PRIVILEGES ON DATABASE nddesk_db TO nddesk_user;"
/usr/local/opt/postgresql@14/bin/psql -d nddesk_db -c "ALTER DATABASE nddesk_db OWNER TO nddesk_user;"

echo "=== PostgreSQL configurado ==="
