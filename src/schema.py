from sqlalchemy import Engine, inspect

from wikidata import output_base


def ensure_output_schema(engine: Engine) -> None:
    output_base.metadata.create_all(engine)
    inspector = inspect(engine)
    wikipedia_columns = {
        column["name"] for column in inspector.get_columns("wikipedia")
    }
    with engine.begin() as conn:
        for column_name in ("abstract", "article_body_wikitext"):
            if column_name not in wikipedia_columns:
                conn.exec_driver_sql(
                    f"ALTER TABLE wikipedia ADD COLUMN {column_name} TEXT"
                )

    column_names = {column["name"] for column in inspector.get_columns("wikidata")}

    required_columns = {
        "qid": "TEXT",
        "osm_node_id": "TEXT",
        "osm_relation_id": "TEXT",
        "osm_way_id": "TEXT",
        "website": "TEXT",
        "threed_model": "TEXT",
        "youtube_id": "TEXT",
        "commons_category": "TEXT",
        "design_plans": "TEXT"
    }

    # Legacy schema includes a required osm_id column; recreate table for new layout.
    if "osm_id" in column_names:
        with engine.begin() as conn:
            conn.exec_driver_sql("DROP TABLE wikidata")
        output_base.metadata.create_all(engine)
        return

    with engine.begin() as conn:
        for column_name, column_type in required_columns.items():
            if column_name not in column_names:
                conn.exec_driver_sql(
                    f"ALTER TABLE wikidata ADD COLUMN {column_name} {column_type}"
                )
