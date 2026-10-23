from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from args import parse_args
from castles import Castle, connect_castles_db
from schema import ensure_output_schema
from wikidata import (
    WikiData,
    WikiDataOutput,
    qid_to_wikidata_id,
    setup_wikidata_mapping,
)

osm_node_property_id: int = 1000011693
osm_relation_property_id: int = 1000000402
osm_way_property_id: int = 1000010689
website_property_id: int = 1000000856
threed_model_property_id: int = 1000004896
youtube_property_id: int = 1000001651
commons_category_id: int = 1000000373
design_plans__property_id: int = 1000003311

def _get_property_string(items: list[WikiData], property_id: int) -> str | None:
    for item in items:
        if item.property_id == property_id:
            value: str | None = getattr(item, "string", None)
            if value:
                return value
    return None


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
        for _i, castle in enumerate(rows, 1):
            wikidata_id = qid_to_wikidata_id(castle.qid)
            if wikidata_id is None:
                continue

            # filters the entries to find the first match with the specified property IDs.
            # If not one of those properties found, the castle will be skipped.
            first_match = (
                wikidata_session.query(WikiData)
                .filter(WikiData.id == wikidata_id)
                # OSM Way Id and OSM Relation Id
                .filter(
                    WikiData.property_id.in_(
                        [
                            osm_node_property_id,
                            osm_relation_property_id,
                            osm_way_property_id,
                            website_property_id,
                            threed_model_property_id,
                            youtube_property_id,
                            commons_category_id,
                            design_plans__property_id,
                        ]
                    )
                )
                .all()
            )
            #if not first_match:
            #    continue

            osm_node_id_value = _get_property_string(
                first_match, osm_node_property_id
            )
            osm_relation_id_value = _get_property_string(
                first_match, osm_relation_property_id
            )
            osm_way_id_value = _get_property_string(first_match, osm_way_property_id)
            website_value = _get_property_string(first_match, website_property_id)
            threed_model_value = _get_property_string(
                first_match, threed_model_property_id
            )
            youtube_value = _get_property_string(first_match, youtube_property_id)
            commons_category_value = _get_property_string(first_match, commons_category_id)
            design_plans_value = _get_property_string(first_match, design_plans__property_id)

            if youtube_value:
                print(
                    "Found YouTube link for castle:",
                    castle.qid,
                    "Value:",
                    youtube_value,
                )

            output_rows.append(
                WikiDataOutput(
                    qid=str(castle.qid),
                    osm_node_id=osm_node_id_value,
                    osm_relation_id=osm_relation_id_value,
                    osm_way_id=osm_way_id_value,
                    website=website_value,
                    threed_model=threed_model_value,
                    youtube_id=youtube_value,
                    design_plans=design_plans_value,
                    commons_category=commons_category_value,
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
