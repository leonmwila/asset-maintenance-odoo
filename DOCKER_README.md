# Asset Maintenance MIS - Docker Setup

This project can be run using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Build and start the containers:**
   ```bash
   docker-compose up -d
   ```

2. **Access Odoo:**
   - Open your browser and go to `http://localhost:8069`
   - Create a new database or use existing one
   - Install the custom modules: `company_extension`, `equipment_serial_link`, `custom_login`

3. **Stop the containers:**
   ```bash
   docker-compose down
   ```

4. **Stop and remove all data (including database):**
   ```bash
   docker-compose down -v
   ```

## Configuration

The Docker setup includes:
- **PostgreSQL 15** database container
- **Odoo 19.0** application container with custom addons
- **Persistent volumes** for database and filestore

### Custom Configuration

To modify Odoo configuration, edit `odoo-docker.conf` and restart:
```bash
docker-compose restart odoo
```

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Only Odoo
docker-compose logs -f odoo

# Only Database
docker-compose logs -f db
```

### Access Odoo shell
```bash
docker-compose exec odoo odoo shell
```

### Backup database
```bash
# Using Odoo web interface: Settings > Database Manager > Backup
# Or via command line:
docker-compose exec db pg_dump -U odoo <database_name> > backup.sql
```

### Restore database
```bash
docker-compose exec -T db psql -U odoo <database_name> < backup.sql
```

### Update modules
```bash
docker-compose exec odoo odoo -u company_extension,equipment_serial_link,custom_login --stop-after-init
docker-compose restart odoo
```

## Production Deployment

For production use:

1. **Update `docker-compose.yml`:**
   - Change database password
   - Update admin password in `odoo-docker.conf`
   - Configure proper volumes for backups

2. **Use environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Enable SSL/HTTPS:**
   - Use a reverse proxy (nginx, traefik)
   - Configure SSL certificates

## Troubleshooting

### Port already in use
If port 8069 is already in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "8070:8069"  # Use port 8070 instead
```

### Permission issues
```bash
sudo chown -R 101:101 custom_addons
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## Volumes

- `odoo-db-data`: PostgreSQL database files
- `odoo-web-data`: Odoo filestore (attachments, sessions)
- `./custom_addons`: Mounted as `/mnt/extra-addons` in container
