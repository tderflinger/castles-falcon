import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extend castles data with Wikidata attributes."
    )
    parser.add_argument(
        "wikidata_db_path",
        help="Absolute or relative path to wikidata.db SQLite file",
    )
    return parser.parse_args()
