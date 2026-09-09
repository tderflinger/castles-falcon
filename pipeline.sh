wget https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2
bzcat latest-all.json.bz2 | wd2sql - wikidata-new.db
