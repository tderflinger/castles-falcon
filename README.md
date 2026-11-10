# Castles Falcon

<p align="center">
  <img src="./assets/castles-falcon-logo.png" alt="Castles Falcon logo image" />
</p>

The goal of this project is to extend the [castlemap-dataset](https://github.com/Flightmussy/castlemap-dataset) from Flightmussy with more attributes from [Wikidata](https://www.wikidata.org/).

This distribution is called `castles-falcon`. Note, due to the large size of the GeoPackage and Parquet data files, they are not hosted on this GitHub repository but on Hugging
Face. If you are interested in downloading the final files, please visit: https://huggingface.co/datasets/td8/castles-falcon

## Prerequisites

In order to reproduce the data pipeline, install the following applications:

- Python 3
- uv
- wget
- bzip2
- wd2sql: https://github.com/p-e-w/wd2sql
- GDAL
- DuckDB

This pipeline has only been tested on Ubuntu Linux.

## Data Pipeline

- Download the compressed Wikidata dump from https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2
- Convert the dump file into a SQLite database using wd2sql (https://github.com/p-e-w/wd2sql)
- Use the Python script in `src/main.py` to write the missing data from Wikidata into a new
`castles-falcon.gpkg` GeoPackage (SQLite) database file.

Run like this:
```bash
./pipeline.sh
```

Note that you need at a minimum twice the harddisk space of the Wikidata dump (currently about 96G), likely some more because of the index creation.

This project can also be used for the purpose of quality control of Wikidata. For example, if the OSM data link is missing, it should be added to Wikidata.

Note: Do not forget to create an index on wikidata db, else it is very slow. Normally `wd2sql` 
automatically creates indexes. If not, create the relevant index manually, like:

```sql
CREATE INDEX IF NOT EXISTS idx_string_id
ON "string" ("id");
```

## Added Attributes

The following attributes from Wikidata are added to the `wikidata` table in the `castles-falcon.gpkg` database:

- qid: The Wikidata entity ID
- osm_node_id: The OpenStreetMap node id of the castle, if available
- osm_relation_id: The OpenStreetMap relation id of the castle, if available
- osm_way_id: The OpenStreetMap way id of the castle, if available
- website: The website entry from Wikidata, if available
- threed_model: The link to a 3D model of the castle, if available
- commons_category: Wikimedia Commons category
- design_plans: Design plan files on Wikimedia Commons

The following attributes from the [Wikipedia Parquet](https://huggingface.co/datasets/wikimedia/linked-openstreetmap-wikidata-wikipedia-wikivoyage) file are added to the `wikipedia` table:

- qid: The Wikidata entity ID
- title: The title of the castle
- abstract: Abstract text, the beginning of each English Wikipedia article of the castle
- article_body_html: The HTML text of each English Wikipedia article of the castle
- article_body_wikitext: The Wikitext of each English Wikipedia article of the castle
- article_body_markdown: The Markdown generated from each HTML text of the English Wikipedia article of the castle

## Provenance

The data in `castles-falcon.gpkg` is based on the [castlemap-dataset](https://github.com/Flightmussy/castlemap-dataset) v2.2.0 of Flightmussy, licensed as CC0.

Please support Flightmussy from the "The Castle Map" (https://thecastlemap.com). He made all of this possible.

The relevant Wikidata attributes copied into `castles-falcon.gpkg` are from
https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2 from 8 September 2026 and licensed as CC0.

The relevant Wikipedia attributes copied into `castles-falcon.gpkg` are from the [Linked OpenStreetMap x Wikidata x Wikipedia x Wikivoyage dataset](https://huggingface.co/datasets/wikimedia/linked-openstreetmap-wikidata-wikipedia-wikivoyage) from September 15, 2026. The license
is CC BY-SA (https://en.wikipedia.org/wiki/Wikipedia:Copyrights).

The logo image was generated with GenAI. The Python source code was partially created with the help of GenAI.

## Data Mirrors

You can also find the dataset at the following location:

* Hugging Face: https://huggingface.co/datasets/td8/castles-falcon

## License

The code in this repository is licensed as MIT. The data in the database
is licensed as CC0. The relevant Wikipedia attributes in the database table `wikipedia` are licensed as CC BY-SA (https://en.wikipedia.org/wiki/Wikipedia:Copyrights).


