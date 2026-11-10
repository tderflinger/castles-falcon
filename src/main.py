from urllib.parse import unquote, urlsplit

import duckdb
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from args import parse_args
from castles import connect_castles_db
from schema import ensure_output_schema
from wikidata import (
    WikiData,
    WikiDataOutput,
    WikipediaOutput,
    qid_to_wikidata_id,
    setup_wikidata_mapping,
)

CASTLES_FALCON_DB: str = "castles-falcon.gpkg"

OSM_NODE_PROPERTY_ID: int = 1000011693
OSM_RELATION_PROPERTY_ID: int = 1000000402
OSM_WAY_PROPERTY_ID: int = 1000010689
WEBSITE_PROPERTY_ID: int = 1000000856
THREED_MODEL_PROPERTY_ID: int = 1000004896
YOUTUBE_PROPERTY_ID: int = 1000001651
COMMONS_CATEGORY_ID: int = 1000000373
DESIGN_PLANS_PROPERTY_ID: int = 1000003311


def _get_property_string(items: list[WikiData], property_id: int) -> str | None:
    for item in items:
        if item.property_id == property_id:
            value: str | None = getattr(item, "string", None)
            if value:
                return value
    return None


def _wikipedia_title(url: str | None) -> str | None:
    if not url:
        return None
    title = urlsplit(url).path.rsplit("/", 1)[-1]
    return unquote(title).replace("_", " ") or None


def main(wikidata_db: str, wikipedia_parquet: str) -> None:
    print("Connecting to castles database...")
    rows = connect_castles_db()

    wikidata_engine = create_engine(f"sqlite:///{wikidata_db}")
    setup_wikidata_mapping(wikidata_engine)

    castles_engine = create_engine(f"sqlite:///{CASTLES_FALCON_DB}")
    ensure_output_schema(castles_engine)

    output_rows: list[WikiDataOutput] = []
    wikipedia_rows: list[WikipediaOutput] = []
    title_to_qids: dict[str, list[str]] = {}
    for castle in rows:
        title = _wikipedia_title(getattr(castle, "wikipedia", None))
        if title:
            title_to_qids.setdefault(title, []).append(str(castle.qid))

        article_bodies: dict[str, list[tuple[str | None, ...]]] = {}
    if title_to_qids:
        with duckdb.connect() as wikipedia_connection:
            article_rows = wikipedia_connection.execute(
                """
                SELECT title, abstract, article_body_html, article_body_wikitext
                FROM read_parquet(?)
                WHERE title IN (SELECT unnest(?))
                """,
                [wikipedia_parquet, list(title_to_qids)],
            ).fetchall()
        article_bodies: dict[str, list[tuple[str | None, ...]]] = {}
        for article_row in article_rows:
            article_bodies.setdefault(article_row[0], []).append(article_row[1:])

    for title, qids in title_to_qids.items():
        for abstract, article_body_html, article_body_wikitext in article_bodies.get(
            title, []
        ):
            wikipedia_rows.extend(
                WikipediaOutput(
                    qid=qid,
                    title=title,
                    abstract=abstract,
                    article_body_html=article_body_html,
                    article_body_wikitext=article_body_wikitext,
                )
                for qid in qids
            )

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
                            OSM_NODE_PROPERTY_ID,
                            OSM_RELATION_PROPERTY_ID,
                            OSM_WAY_PROPERTY_ID,
                            WEBSITE_PROPERTY_ID,
                            THREED_MODEL_PROPERTY_ID,
                            YOUTUBE_PROPERTY_ID,
                            COMMONS_CATEGORY_ID,
                            DESIGN_PLANS_PROPERTY_ID,
                        ]
                    )
                )
                .all()
            )

            osm_node_id_value = _get_property_string(first_match, OSM_NODE_PROPERTY_ID)
            osm_relation_id_value = _get_property_string(
                first_match, OSM_RELATION_PROPERTY_ID
            )
            osm_way_id_value = _get_property_string(first_match, OSM_WAY_PROPERTY_ID)
            website_value = _get_property_string(first_match, WEBSITE_PROPERTY_ID)
            threed_model_value = _get_property_string(
                first_match, THREED_MODEL_PROPERTY_ID
            )
            youtube_value = _get_property_string(first_match, YOUTUBE_PROPERTY_ID)
            commons_category_value = _get_property_string(
                first_match, COMMONS_CATEGORY_ID
            )
            design_plans_value = _get_property_string(
                first_match, DESIGN_PLANS_PROPERTY_ID
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

    with Session(castles_engine) as output_session:
        output_session.query(WikiDataOutput).delete()
        output_session.add_all(output_rows)
        output_session.query(WikipediaOutput).delete()
        output_session.add_all(wikipedia_rows)
        output_session.commit()

    print("Written to castles-falcon.gpkg table wikidata:", len(output_rows))
    print("Written to castles-falcon.gpkg table wikipedia:", len(wikipedia_rows))


if __name__ == "__main__":
    args = parse_args()
    main(args.wikidata_db_path, args.wikipedia_parquet_path)
