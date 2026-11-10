import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extend castles data with Wikidata attributes."
    )
    parser.add_argument(
        "wikidata_db_path",
        help="Absolute or relative path to wikidata.db SQLite file",
    )
    parser.add_argument(
        "wikipedia_parquet_path",
        help="Absolute or relative path to Wikipedia Parquet file",
    )
    return parser.parse_args()
