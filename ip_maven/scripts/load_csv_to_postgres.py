import argparse
import os
import pandas as pd
import psycopg2
import sys
import logging

def DBConnect(db_host, db_port, db_name, db_user, db_pass):
    try:
        if str(db_pass).lower() == "pgpass":
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                dbname=db_name,
                user=db_user
            )
        else:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_pass
            )
    except Exception as err:
        logging.exception(err)
        sys.exit(1)
    return conn

def import_csv_to_sql_table(conn, csv_path, table_name="ipmaven_www_whois"):
    try:
        # Read CSV into a DataFrame
        df = pd.read_csv(csv_path, low_memory=False)

        # Create a cursor to execute PostgreSQL commands
        with conn.cursor() as cursor:
            print(f"Starting data insertion into '{table_name}'...")

            # Insert data from DataFrame to table row by row
            for i, row in df.iterrows():
                cursor.execute(f"""
                    INSERT INTO {table_name} (
                        end_address,
                        handle,
                        name,
                        org_handle,
                        start_address,
                        ref,
                        city,
                        code2,
                        code3,
                        customer_name,
                        e164,
                        customer,
                        postal_code,
                        registration_date,
                        state,
                        street_address,
                        update_date,
                        comment,
                        referral_server,
                        parent_org_handle, updated
                    ) VALUES (
                        %(endAddress)s, %(handle)s, %(name)s, %(orgHandle)s, %(startAddress)s,
                        %(ref)s, %(city)s, %(code2)s, %(code3)s, %(customerName)s,
                        %(e164)s, %(customer)s, %(postalCode)s, %(registrationDate)s, %(state)s,
                        %(streetAddress)s, %(updateDate)s, %(comment)s, %(referralServer)s, %(parentOrgHandle)s, now()
                    );
                """, row.to_dict())
                
                # Print insertion progress on the same line
                print(f"Inserted row {i + 1}/{len(df)}", end='\r')

            # Commit all inserts after the loop
            conn.commit()

        print("\nData moved to 'ipmaven_www_whois' table successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import CSV into PostgreSQL and migrate data.')
    parser.add_argument('--dbname', required=True, help='PostgreSQL database name.')
    parser.add_argument('--user', required=True, help='PostgreSQL user.')
    parser.add_argument('--password', required=True, help='PostgreSQL password.')
    parser.add_argument('--host', required=True, help='PostgreSQL host.')
    parser.add_argument('--port', required=True, help='PostgreSQL port.')
    parser.add_argument('--csv', required=True, help='Path to the CSV file to import.')
    args = parser.parse_args()
    
    # Validate file path for the CSV file
    if not os.path.isfile(args.csv):
        print(f"CSV file '{args.csv}' not found.")
        exit(1)
    
    # Database configuration
    conn = DBConnect(args.host, args.port, args.dbname, args.user, args.password)
    
    # Set autocommit to true to handle temporary table creation properly
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    import_csv_to_sql_table(conn, args.csv)

    conn.close()


# python load_csv_to_postgres.py --dbname ipmaven --user ipmaven --password scotty@1 --host localhost --port 5432 --csv ../_data/import/arin_db.csv