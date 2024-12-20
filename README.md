# README

This simple program allows you to export all your DNS entries in your
dreamhost account to a zonefile. Then you can import that zonefile in
BIND or Route 53, etc.

## How to run this

First, you’ll need to [create an API key for the Dreamhost API](https://help.dreamhost.com/hc/en-us/articles/4407354972692-Connecting-to-the-DreamHost-API) with access to the `dns-list_records` function.

Then, you can run the script:

    ./dreamhost_zone_exporter.py

You can provide your API Key as a command line argument:

    ./dreamhost_zone_exporter.py -k 6SHU5P2HLDAYECUM

Or as an environment variable:

    DREAMHOST_APIKEY=6SHU5P2HLDAYECUM ./dreamhost_zone_exporter.py

By default, the script will print a Zone File for all "zones" (domains) your API Key has access to. If you want to filter down to a subset of domains in your account, you can use one or more `-d` arguments:

    ./dreamhost_zone_exporter.py -d example.com -d example.net
