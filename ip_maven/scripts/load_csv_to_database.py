import argparse
import os
import pandas as pd
import sqlite3

def import_csv_to_sql_table(db_path, csv_path, table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Read CSV into a DataFrame
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Insert the DataFrame into the specified table in the database
        df.to_sql(table_name, conn, if_exists='append', index=False)
        
        print(f"CSV data imported into '{table_name}' table successfully.")
        
        # Execute SQL to move data to the main table
        cursor = conn.cursor()

        cursor.execute(f"update {table_name} set name = '' where name is null;")
        conn.commit()

        cursor.execute(f"""
        INSERT INTO ipmaven_www_whois (
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
            parent_org_handle,
            updated
        )
        SELECT
            endAddress,
            handle,
            name,
            orgHandle,
            startAddress,
            ref,
            city,
            code2,
            code3,
            customerName,
            e164,
            customer,
            postalCode,
            registrationDate,
            state,
            streetAddress,
            updateDate,
            comment,
            referralServer,
            parentOrgHandle,
            datetime('now')
        FROM {table_name};
        """)
        
        # Commit the insertion
        conn.commit()

        # Drop the import table
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()

        print("Data moved to 'ipmaven_www_whois' table and temporary table dropped.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import CSV into SQLite and migrate data.')
    parser.add_argument('--db', required=True, help='Path to the SQLite database file.')
    parser.add_argument('--csv', required=True, help='Path to the CSV file to import.')
    args = parser.parse_args()
    
    # Validate file paths
    if not os.path.isfile(args.db):
        print(f"Database file '{args.db}' not found.")
        exit(1)
    if not os.path.isfile(args.csv):
        print(f"CSV file '{args.csv}' not found.")
        exit(1)
    
    import_csv_to_sql_table(args.db, args.csv, "import2")
    