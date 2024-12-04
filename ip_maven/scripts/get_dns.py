import dns.resolver
import socket
from io import StringIO
import psycopg2
import argparse
import os
import pandas as pd
import sys
import logging
import ipaddress
import time 
import random

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

# Function to test DNS entries for a single domain and return raw output as a string
def test_dns(domain):
    # Use a StringIO object to capture printed output as a string
    output_buffer = StringIO()

    # Write to buffer instead of directly printing to console
    output_buffer.write(f"Testing domain: {domain}\n")

    # Step 1: Get the authoritative name servers for the domain
    try:
        ns_answers = dns.resolver.resolve(domain, 'NS', raise_on_no_answer=False)
        authoritative_nameservers = [ns.to_text() for ns in ns_answers]
        
        if authoritative_nameservers:
            # If authoritative name servers are found
            output_buffer.write(f"  Authoritative Name Servers for {domain}: {authoritative_nameservers}\n")
            
            # Step 2: Use one of the authoritative name servers to get an authoritative answer
            authoritative_server = authoritative_nameservers[0]
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [socket.gethostbyname(authoritative_server)]
        else:
            # If no authoritative servers are found, fallback to default recursive resolver
            output_buffer.write(f"  No specific authoritative NS found for {domain}, using default recursive resolver.\n")
            resolver = dns.resolver.Resolver()

        # Step 3: Query 'A' records (IPv4 address)
        try:
            answers = resolver.resolve(domain, 'A')
            for rdata in answers:
                output_buffer.write(f"  IPv4 Address of {domain}: {rdata}\n")
        except dns.resolver.NoAnswer:
            output_buffer.write(f"  No A record found for {domain}\n")
        except Exception as e:
            output_buffer.write(f"  Error querying A record for {domain}: {e}\n")

        # Step 4: Query 'AAAA' records (IPv6 address)
        try:
            answers_aaaa = resolver.resolve(domain, 'AAAA', raise_on_no_answer=False)
            for rdata in answers_aaaa:
                output_buffer.write(f"  IPv6 Address of {domain}: {rdata}\n")
        except dns.resolver.NoAnswer:
            output_buffer.write(f"  No AAAA record found for {domain}\n")
        except Exception as e:
            output_buffer.write(f"  Error querying AAAA record for {domain}: {e}\n")

        # Step 5: Query 'CNAME' records (Canonical Names)
        try:
            answers_cname = resolver.resolve(domain, 'CNAME', raise_on_no_answer=False)
            for cname in answers_cname:
                output_buffer.write(f"  CNAME Record for {domain}: {cname.target}\n")
        except dns.resolver.NoAnswer:
            output_buffer.write(f"  No CNAME record found for {domain}\n")
        except Exception as e:
            output_buffer.write(f"  Error querying CNAME record for {domain}: {e}\n")

    except dns.resolver.NXDOMAIN:
        output_buffer.write(f"  Domain {domain} does not exist.\n")
    except dns.resolver.NoNameservers:
        output_buffer.write(f"  No nameservers available for the domain {domain}.\n")
    except dns.resolver.NoAnswer:
        output_buffer.write(f"  No authoritative name servers found for {domain}.\n")
    except Exception as e:
        output_buffer.write(f"  An error occurred while finding authoritative servers for {domain}: {e}\n")

    output_buffer.write("\n")
    
    # Store the output as a string
    result = output_buffer.getvalue()

    # Close the buffer
    output_buffer.close()

    return result

# Function to parse the IP addresses from the raw output of a single domain
def parse_dns_results(raw_output):
    ip_addresses = []
    lines = raw_output.splitlines()
    for line in lines:
        if "IPv4 Address of" in line or "IPv6 Address of" in line:
            # Extract the IP address from the line
            ip = line.split(":")[-1].strip()
            ip_addresses.append(ip)
    return ip_addresses


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find records that need answers')
    parser.add_argument('--dbname', required=True, help='PostgreSQL database name.')
    parser.add_argument('--user', required=True, help='PostgreSQL user.')
    parser.add_argument('--password', required=True, help='PostgreSQL password.')
    parser.add_argument('--host', required=True, help='PostgreSQL host.')
    parser.add_argument('--port', required=True, help='PostgreSQL port.')
    args = parser.parse_args()
    
    conn = DBConnect(args.host, args.port, args.dbname, args.user, args.password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, query FROM ipmaven_www_mapping 
                WHERE answer IS NULL or answer = '';""")
        rows = cursor.fetchall()

        for row in rows:
            id, query = row

            print(f"testing domain: {query}")
            raw = test_dns(query)
            result = parse_dns_results(raw)

            if result:
                print(f"IP addresses for {query}: {result[0]}")
                

                cursor.execute("""
                    UPDATE ipmaven_www_mapping 
                    SET answer = %s 
                    WHERE id = %s;""", (result[0], id))

                # Commit all updates after the loop
                conn.commit()

            # sleep for 30 to 60 seconds randomly
            
            time.sleep(random.randint(30, 60))


        

    conn.close()

    # python get_dns.py --dbname ipmaven --user ipmaven --password scotty@1 --host localhost --port 5432
    