# PostgreSQL

## How to install PostgreSQL in Debian/Ubuntu

Run these commands as root or with `sudo`.

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

After installation, the service starts automatically. Check status:

```bash
sudo systemctl status postgresql
```

Switch to the default PostgreSQL administrative user:

```bash
sudo -i -u postgres
```

Start the PostgreSQL shell:

```bash
psql
```

To exit:

```sql
\q
```

To enable the service at boot:

```bash
sudo systemctl enable postgresql
```

Configuration files: `/etc/postgresql/<version>/main/`
Data directory: `/var/lib/postgresql/<version>/main/`

## Create root user

From the terminal as the `postgres` system user:

```bash
sudo -i -u postgres
psql
```

Inside the `psql` prompt, create a new superuser:

```sql
CREATE ROLE admin WITH LOGIN PASSWORD 'your_password' SUPERUSER CREATEDB CREATEROLE;
```

Then exit:

```sql
\q
```

Allow local connections using password authentication. Edit:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Find the line:

```
local   all             all                                     peer
```

Replace it with:

```
local   all             all                                     md5
```

Save and restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

Now you can connect with:

```bash
psql -U admin -d postgres
```

It will prompt for the password you set.
