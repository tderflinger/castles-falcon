from typing import Any
from args import parse_args
from sqlalchemy import Integer, String, Table, create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column, registry

mapper_registry = registry()
output_base = declarative_base()

class Castle:
    """ORM entity mapped to the castlemap-castles table."""

    def as_dict(self) -> dict[str, Any]:
        return {
            column.key: getattr(self, column.key) for column in self.__table__.columns
        }

class WikiData:
    """ORM entity mapped to a table in wikidata.db."""

class WikiDataOutput(output_base):
    """Output table in castles-ext.gpkg with OSM id values."""

    __tablename__ = "wikidata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    qid: Mapped[str] = mapped_column(String, nullable=False)
    osm_node_id: Mapped[str | None] = mapped_column(String, nullable=True)
    osm_relation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    osm_way_id: Mapped[str | None] = mapped_column(String, nullable=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)

def setup_mappings(engine: Engine) -> None:
    castles_table = Table(
        "castlemap-castles",
        mapper_registry.metadata,
        autoload_with=engine,
    )
    mapper_registry.map_imperatively(Castle, castles_table)

def setup_wikidata_mapping(engine: Engine, table_name: str = "string") -> str:
    inspector = inspect(engine)
    table_names = [
        name for name in inspector.get_table_names() if not name.startswith("sqlite_")
    ]
    if not table_names:
        raise RuntimeError("No user tables found in wikidata database")
    if table_name not in table_names:
        raise RuntimeError(f"Table {table_name!r} not found in wikidata database")

    wikidata_table = Table(
        table_name,
        mapper_registry.metadata,
        autoload_with=engine,
    )
    pk_names = inspector.get_pk_constraint(table_name).get("constrained_columns") or []
    if pk_names:
        mapper_primary_key = [wikidata_table.c[name] for name in pk_names]
    else:
        # Some SQLite tables in wikidata.db have no declared PK.
        # For read-only ORM mapping, use all columns as a composite identity.
        mapper_primary_key = list(wikidata_table.c)

    mapper_registry.map_imperatively(
        WikiData,
        wikidata_table,
        primary_key=mapper_primary_key,
    )
    return table_name

def qid_to_wikidata_id(qid: object) -> int | None:
    text = str(qid).strip()
    if text.startswith("Q"):
        text = text[1:]
    if not text.isdigit():
        return None
    return int(text)

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
    osm_node_property_id: int = 1000011693
    osm_relation_property_id: int = 1000000402
    osm_way_property_id: int = 1000010689
    website_property_id: int = 1000000856

    castles_engine = create_engine("sqlite:///castles.gpkg")
    setup_mappings(castles_engine)
    with Session(castles_engine) as session:
        rows = session.query(Castle).all()

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
            print(f"[{i}]", castle.qid)
            wikidata_id = qid_to_wikidata_id(castle.qid)
            if wikidata_id is None:
                continue

            first_match = (
                wikidata_session.query(WikiData)
                .filter(WikiData.id == wikidata_id)
                # OSM Way Id and OSM Relation Id
                .filter(
                    WikiData.property_id.in_([osm_node_property_id, osm_relation_property_id, osm_way_property_id, website_property_id])
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

            output_rows.append(
                WikiDataOutput(
                    qid=str(castle.qid),
                    osm_node_id=osm_node_id_value,
                    osm_relation_id=osm_relation_id_value,
                    osm_way_id=osm_way_id_value,
                    website=website_value,
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
