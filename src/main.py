from typing import Any
from args import parse_args
from castles import Castle, connect_castles_db
from sqlalchemy import create_engine, inspect
from wikidata import output_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from wikidata import WikiData, WikiDataOutput, setup_wikidata_mapping, qid_to_wikidata_id

osm_node_property_id: int = 1000011693
osm_relation_property_id: int = 1000000402
osm_way_property_id: int = 1000010689
website_property_id: int = 1000000856
threed_model_property_id: int = 1000004896  

def ensure_output_schema(engine: Engine) -> None:
    output_base.metadata.create_all(engine)
    inspector = inspect(engine)
    column_names = {column["name"] for column in inspector.get_columns("wikidata")}

    required_columns = {
        "qid": "TEXT",
        "osm_node_id": "TEXT",
        "osm_relation_id": "TEXT",
        "osm_way_id": "TEXT",
        "website": "TEXT",
        "threed_model": "TEXT",
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


def main(wikidata_db: str) -> None:
    rows = connect_castles_db()
    cols = [column.key for column in Castle.__table__.columns]

    print("Columns:", ", ".join(cols))
    print("Row count:", len(rows))

    wikidata_engine = create_engine(f"sqlite:///{wikidata_db}")
    wikidata_table_name = setup_wikidata_mapping(wikidata_engine)
    wikidata_columns = [column.key for column in WikiData.__table__.columns]

    print("WikiData table:", wikidata_table_name)
    print("WikiData columns:", ", ".join(wikidata_columns))

    castles_ext_engine = create_engine("sqlite:///castles-falcon.gpkg")
    ensure_output_schema(castles_ext_engine)

    output_rows: list[WikiDataOutput] = []
    with Session(wikidata_engine) as wikidata_session:
        for i, castle in enumerate(rows, 1):
            wikidata_id = qid_to_wikidata_id(castle.qid)
            if wikidata_id is None:
                continue

            first_match = (
                wikidata_session.query(WikiData)
                .filter(WikiData.id == wikidata_id)
                # OSM Way Id and OSM Relation Id
                .filter(
                    WikiData.property_id.in_([osm_node_property_id, osm_relation_property_id, osm_way_property_id, website_property_id, threed_model_property_id])
                )
                .all()
            )
            if not first_match:
                continue

            osm_node_id_value = next(
                (
                    getattr(item, "string", None)
                    for item in first_match
                    if item.property_id == osm_node_property_id
                    and getattr(item, "string", None)
                ),
                None,
            )

            osm_relation_id_value = next(
                (
                    getattr(item, "string", None)
                    for item in first_match
                    if item.property_id == osm_relation_property_id
                    and getattr(item, "string", None)
                ),
                None,
            )

            osm_way_id_value = next(
                (
                    getattr(item, "string", None)
                    for item in first_match
                    if item.property_id == osm_way_property_id
                    and getattr(item, "string", None)
                ),
                None,
            )

            website_value = next(
                (
                    getattr(item, "string", None)
                    for item in first_match
                    if item.property_id == website_property_id
                    and getattr(item, "string", None)
                ),
                None,
            )

            threed_model_value = next(
                (
                    getattr(item, "string", None)
                    for item in first_match
                    if item.property_id == threed_model_property_id
                    and getattr(item, "string", None)
                ),
                None,
            )

            if threed_model_value:
                print("Found 3D model for castle:", castle.qid, "Value:", threed_model_value)

            output_rows.append(
                WikiDataOutput(
                    qid=str(castle.qid),
                    osm_node_id=osm_node_id_value,
                    osm_relation_id=osm_relation_id_value,
                    osm_way_id=osm_way_id_value,
                    website=website_value,
                    threed_model=threed_model_value,
                )
            )

    with Session(castles_ext_engine) as output_session:
        output_session.query(WikiDataOutput).delete()
        output_session.add_all(output_rows)
        output_session.commit()

    print("Written to castles-falcon.gpkg table wikidata:", len(output_rows))

if __name__ == "__main__":
    args = parse_args()
    main(args.wikidata_db_path)
