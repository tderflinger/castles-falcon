from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, registry
from sqlalchemy import Table, inspect
from sqlalchemy.engine import Engine

mapper_registry = registry()
output_base = declarative_base()

class WikiData:
    """ORM entity mapped to a table in wikidata.db."""

class WikiDataOutput(output_base):
    """Output table in castles-falcon.gpkg with OSM id values."""

    __tablename__ = "wikidata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    qid: Mapped[str] = mapped_column(String, nullable=False)
    osm_node_id: Mapped[str | None] = mapped_column(String, nullable=True)
    osm_relation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    osm_way_id: Mapped[str | None] = mapped_column(String, nullable=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    threed_model: Mapped[str | None] = mapped_column(String, nullable=True)


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
