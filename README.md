# Castles Falcon

![Castles Falcon logo image](./assets/castles-falcon-logo.png)

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
`castles-falcon.gpkg` GeoPackage (SQLite) database file.

Run like this:
```bash
./pipeline.sh
uv sync --frozen
source ./.venv/bin/activate
python3 src/main.py path/to/wikidata.db
```

Note that you need at a minimum twice the harddisk space of the Wikidata dump (currently about 96G), likely some more because of the index creation.

This project can also be used for the purpose of quality control of Wikidata. For example, if the OSM data link is missing, it should be added to Wikidata.

Note: Do not forget to create an index on wikidata db, else it is very slow. Normally `wd2sql` 
automatically creates indexes. If not, create the relevant index manually, like:

``sql
CREATE INDEX IF NOT EXISTS idx_string_id
ON "string" ("id");
``

## Provenance

The data in `castles-falcon.gpkg` is based on the [castlemap-dataset](https://github.com/Flightmussy/castlemap-dataset) v2.2.0 of Flightmussy, licensed as CC0.

The relevant Wikidata attributes copied into `castles-falcon.gpkg` are from
https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2 from 8 September 2026 and licensed as CC0.

## License

The code in this repository is licensed as MIT. The data in the database
is license as CC-BY.
