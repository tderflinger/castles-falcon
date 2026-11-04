wget https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2
bzcat latest-all.json.bz2 | wd2sql - wikidata-new.db
source ./copy-wikidata-attributes ./wikidata-new.db

# Convert table wikidata to Parquet file; ensure Parquet driver installed, for example with conda version
ogr2ogr -f Parquet castles-falcon-wikidata.parquet ./castles-falcon.gpkg wikidata
ogr2ogr -f Parquet castles-falcon.parquet ./castles-falcon.gpkg castlemap-castles
# Combine to one unified Parquet file
duckdb -c "COPY (SELECT fid,qid,name,category,country,iso,year,year_approx,century,wikipedia,image,image_by,image_licence,sitelinks,pageviews,fame_rank,url,geom,geom_bbox,osm_node_id,osm_relation_id,osm_way_id,website,threed_model,youtube_id,commons_category,design_plans FROM 'castles-falcon.parquet' JOIN 'castles-falcon-wikidata.parquet' USING (qid)) TO 'castles-falcon-combined.parquet' (FORMAT PARQUET);"
