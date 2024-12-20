#!/usr/bin/env python3

import argparse
import os
import pprint
import sys
from dreampylib import DreampyLib

ZONE_OUTPUT_TEMPLATE = "{record:<30} IN {type:<6} {value:<30} ; {comment}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Export a DNS Zone File for one or more Dreamhost domains"
    )

    parser.add_argument(
        "-d",
        "--domain",
        action="append",
        help="Domain(s) for which to retrieve DNS entries (can specify multiple times)"
    )

    parser.add_argument(
        "-k",
        "--api-key",
        type=str,
        help="Dreamhost API Key (if unspecified, will fall back to DREAMHOST_APIKEY environment variable, then a command line prompt)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    if args.api_key:
        password = args.api_key
    else:
        password = os.environ.get("DREAMHOST_APIKEY") or input("API key: ")

    if args.debug:
        DEBUG = True
    else:
        DEBUG = False

    # Specify the default returntype.
    # Can be either 'dict' or 'list'
    defaultReturnType = 'dict'

    # Initialize the library and open a connection
    connection = DreampyLib(password, debug=DEBUG)

    # If the connection is up, do some tests.
    if not connection.IsConnected():
        print("Error connecting!")
        print(connection.Status())
        sys.exit(1)

    response = connection.dns.list_records()
    if DEBUG:
        pprint.pprint(response)

    # If domain(s) specified, filter down to just those records.
    if args.domain:
        response = [item for item in response if item["zone"] in args.domain]

    dns_data = {}
    for d in response:
        account_entries = dns_data.setdefault(d["account_id"], {})
        zone_entries = account_entries.setdefault(d["zone"], [])
        zone_entries.append(d)
    if DEBUG:
        pprint.pprint(dns_data)

    for a in dns_data:
        print("# ", "-" * 50, "Account: %s" % a, "-" * 50)
        zones = dns_data[a]
        for z in zones:
            print("# ", "." * 50, "Zone: %s" % z, "." * 50)
            zone = zones[z]
            print("$ORIGIN %s" % z)
            print("$TTL 600s")
            for e in zone:
                e["record"] += "."
                print(ZONE_OUTPUT_TEMPLATE.format(**e))
