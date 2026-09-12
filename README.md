# Castles Falcon

The goal of this project is to extend the [castlemap-dataset](https://github.com/Flightmussy/castlemap-dataset) from Flightmussy with more attributes from Wikidata.

This extension distribution is called `castles-falcon`.

## Prerequisites

In order to reproduce the data pipeline, install the following applications:

- wget
- bzip2
- wd2sql: https://github.com/p-e-w/wd2sql

This pipeline has only been tested on Ubuntu Linux.

## Data Pipeline

- Download the compressed Wikidata dump from https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2
- Convert the dump file into a SQLite database using wd2sql
- Use the Python script in `src/main.py` to write the missing data from Wikidata into a new
`castles-ext.gpkg` GeoPackage (SQLite) database file.

Run like this:
```bash
uv xxxxx
source ./.venv/bin/activate
python3 src/main.py wikidata.db
```

Note that you need at a minimum twice the harddisk space of the Wikidata dump (currently about 96G), probably more because of the index creation.

First, the link to OSM relation or way is added. Via OSM entry, the official website
information could be retrieved (and added to Wikidata if missing).

It can also be used for the purpose of quality control of Wikidata. If
OSM data is missing, it should be added, if available on OSM.

Note: Do not forget to create an index on wikidata db, else it is very slow. Normally `wd2sql` 
automatically creates indexes. If not, create the relevant index manually, like:

``sql
CREATE INDEX IF NOT EXISTS idx_string_id
ON "string" ("id");
``

Ideas:
- Grab videos about castle from YouTube API
- Grab literature info from Wikipedia article

