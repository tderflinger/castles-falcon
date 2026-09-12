# Castles Falcon

<p align="center">
  <img src="./assets/castles-falcon-logo.png" alt="Castles Falcon logo image" />
</p>

The goal of this project is to extend the [castlemap-dataset](https://github.com/Flightmussy/castlemap-dataset) from Flightmussy with more attributes from [Wikidata](https://www.wikidata.org/).

This distribution is called `castles-falcon`.

## Prerequisites

In order to reproduce the data pipeline, install the following applications:

- Python 3
- uv
- wget
- bzip2
- wd2sql: https://github.com/p-e-w/wd2sql

This pipeline has only been tested on Ubuntu Linux.

## Data Pipeline

- Download the compressed Wikidata dump from https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2
- Convert the dump file into a SQLite database using wd2sql (https://github.com/p-e-w/wd2sql)
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

## Added Attributes

The following attributes from Wikidata are added to the `wikidata` table in the `castles-falcon.gpkg` database:

- qid: The Wikidata entity ID
- osm_node_id: The OpenStreetMap node id of the castle, if available
- osm_relation_id: The OpenStreetMap relation id of the castle, if available
- osm_way_id: The OpenStreetMap way id of the castle, if available
- website: The website entry from Wikidta, if available
- threed_model: The link to a 3D model of the castle, if available

## Provenance

The data in `castles-falcon.gpkg` is based on the [castlemap-dataset](https://github.com/Flightmussy/castlemap-dataset) v2.2.0 of Flightmussy, licensed as CC0.

The relevant Wikidata attributes copied into `castles-falcon.gpkg` are from
https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2 from 8 September 2026 and licensed as CC0.

The logo image was generated with GenAI. The Python source code was partially created with the help of GenAI.

## License

The code in this repository is licensed as MIT. The data in the database
is license as CC-BY.
