#!/bin/bash
# Setup script for running Odoo natively on Ubuntu

set -e

echo "Installing Python 3.12 and dependencies..."
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip \
    postgresql postgresql-contrib libpq-dev \
    wkhtmltopdf libsasl2-dev libldap2-dev libssl-dev \
    node-less npm git

echo "Creating PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE odoo;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD 'odoo';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE odoo TO odoo;"
sudo -u postgres psql -c "ALTER DATABASE odoo OWNER TO odoo;"

echo "Creating Python virtual environment..."
python3.12 -m venv ~/apps/asset-management-mis/venv
source ~/apps/asset-management-mis/venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r ~/apps/asset-management-mis/requirements.txt

echo "Creating Odoo configuration..."
cat > ~/apps/asset-management-mis/odoo-native.conf << 'EOF'
[options]
addons_path = /home/amms-sys1/apps/asset-management-mis/addons,/home/amms-sys1/apps/asset-management-mis/custom_addons
data_dir = /home/amms-sys1/.local/share/Odoo
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
http_interface = 0.0.0.0
http_port = 8069
logfile = /var/log/odoo/odoo.log
EOF

echo "Creating log directory..."
sudo mkdir -p /var/log/odoo
sudo chown $USER:$USER /var/log/odoo

echo "Setup complete! To start Odoo, run:"
echo "source ~/apps/asset-management-mis/venv/bin/activate"
echo "./odoo-bin -c odoo-native.conf"
