# castles-extension

The goal of this project is to extend the castles.gpkg database with attributes
from Wikidata.

First, the link to OSM relation or way is added. Via OSM entry, the official website
information could be retrieved (and added to Wikidata if missing).

It can also be used for the purpose of quality control of Wikidata. If
OSM data is missing, it should be added, if available on OSM.

Note: Do not forget to create an index on wikidata db, else it is very slow:

CREATE INDEX IF NOT EXISTS idx_string_id
ON "string" ("id");


Ideas:
- Grab videos about castle from YouTube API
- Grab literature info from Wikipedia article

