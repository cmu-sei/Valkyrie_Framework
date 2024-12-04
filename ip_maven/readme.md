# IP Maven

IP Maven is a DNS service that provides detailed information about IP addresses and their associated netblock records, both online and offline.

The thinking is that by combining normal zeek dns logs with the netblock information, we can provide a more detailed view of the network traffic.

## Quick Start

Due to licensing restrictions on some of the data that IP Maven relies on, the application does not include netblock information by default. To load the data and start the application, follow these steps:

```bash
pip install -r requirements.txt

# If python manage.py results in ModuleNotFoundError: No module named 'pkg_resources'
# https://stackoverflow.com/questions/7446187/no-module-named-pkg-resources
pip install setuptools

python manage.py makemigrations ipmaven_www
python manage.py migrate

python ../scripts/load_csv_to_database.py --db ../src/ipmaven_www/db.sqlite3 --csv ../_data/import/out/arin_db.csv

python manage.py runserver 127.0.0.1:8000
```

The output then, should be similar to:

```
CSV data imported into 'import2' table successfully.
Data moved to 'ipmaven_www_whois' table and temporary table dropped.
```

The app is now ready to use.
