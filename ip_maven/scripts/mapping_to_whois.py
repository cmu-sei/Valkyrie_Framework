import argparse
import os
import pandas as pd
import psycopg2
import sys
import logging
import ipaddress

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

def map(conn):
    try:
        # Create a cursor to execute PostgreSQL commands
        with conn.cursor() as cursor:
            logging.info("Starting data mapping...")

            # Fetch rows that need processing
            cursor.execute("""
                SELECT query, answer, id FROM ipmaven_www_mapping 
                WHERE answer_whois_id IS NULL OR query_whois_id IS NULL;
            """)

            rows = cursor.fetchall()

            for row in rows:
                query, answer, mapping_id = row

                # Convert query and answer to IP addresses if valid
                try:
                    query_ip = ipaddress.ip_address(query)
                except ValueError:
                    query_ip = None

                try:
                    answer_ip = ipaddress.ip_address(answer)
                except ValueError:
                    answer_ip = None

                # Update query_whois_id if query is a valid IP address
                if query_ip:
                    cursor.execute("""
                        SELECT id FROM ipmaven_www_whois 
                        WHERE %s >= start_address AND %s <= end_address
                        LIMIT 1;
                    """, (query, query))
                    whois_record = cursor.fetchone()
                    if whois_record:
                        cursor.execute("""
                            UPDATE ipmaven_www_mapping 
                            SET query_whois_id = %s 
                            WHERE id = %s;
                        """, (whois_record[0], mapping_id))

                # Update answer_whois_id if answer is a valid IP address
                if answer_ip:
                    cursor.execute("""
                        SELECT id FROM ipmaven_www_whois 
                        WHERE %s >= start_address AND %s <= end_address
                        LIMIT 1;
                    """, (answer, answer))
                    whois_record = cursor.fetchone()
                    if whois_record:
                        cursor.execute("""
                            UPDATE ipmaven_www_mapping 
                            SET answer_whois_id = %s 
                            WHERE id = %s;
                        """, (whois_record[0], mapping_id))

            # Commit all updates after the loop
            conn.commit()

        logging.info("Data mapping completed successfully.")
    
    except Exception as e:
        logging.error(f"An error occurred during data mapping: {e}")
        conn.rollback()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import CSV into PostgreSQL and migrate data.')
    parser.add_argument('--dbname', required=True, help='PostgreSQL database name.')
    parser.add_argument('--user', required=True, help='PostgreSQL user.')
    parser.add_argument('--password', required=True, help='PostgreSQL password.')
    parser.add_argument('--host', required=True, help='PostgreSQL host.')
    parser.add_argument('--port', required=True, help='PostgreSQL port.')
    args = parser.parse_args()
    
    conn = DBConnect(args.host, args.port, args.dbname, args.user, args.password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    map(conn)
    conn.close()

# python mapping_to_whois.py --dbname ipmaven --user ipmaven --password scotty@1 --host localhost --port 5432
