# IP Maven Quick Start

Due to licensing restrictions on some of the data used by IP Maven, the application does not include netblock information by default. To load the necessary data and start using IP Maven, follow these steps:

## Step 1: Prepare the Environment

- Ensure that you have installed Python 3.8+ and the required dependencies.
- Clone the IP Maven repository from GitHub:

```bash
git clone https://github.com/cmu-sei/Valkyrie_Framework
cd valkyrie_framework/ip_maven
```

## Step 2: Acquire Licensing Data

- Obtain the necessary netblock data files from approved providers.
- Licensing agreements may require you to download and update these files periodically.
- Save the netblock data files to the data/ directory within the IP Maven project.

## Step 3: Install Dependencies

- Use the following command to install all required dependencies:

```bash
pip install -r requirements.txt

# If python manage.py results in ModuleNotFoundError: No module named 'pkg_resources'
# https://stackoverflow.com/questions/7446187/no-module-named-pkg-resources
pip install setuptools

python manage.py makemigrations ipmaven_www
python manage.py migrate
```

## Step 4: Load Netblock Information

- Load the netblock data into IP Maven using the provided script:

```bash
python ../scripts/load_csv_to_database.py --db ../src/ipmaven_www/db.sqlite3 --csv ../_data/import/out/arin_db.csv
```

Verify the data load by checking the application logs for success messages.

The output should be similar to:

```bash
CSV data imported into 'import2' table successfully.
Data moved to 'ipmaven_www_whois' table and temporary table dropped.
```

## Step 5: Start the Application

- Launch IP Maven:

```bash
python manage.py runserver 127.0.0.1:8000
```

By default, the service runs on [http://localhost:8000](http://localhost:8000). You can modify the port and configuration settings in the config.yaml file.

## Step 6: Integration with Zeek

- Configure Zeek to export DNS logs to a directory accessible by IP Maven.

The app is now ready to use.
