from sqlalchemy import Engine, Table, create_engine
from sqlalchemy.orm import Session, registry


class Castle:
    """ORM entity mapped to the castlemap-castles table."""


mapper_registry = registry()
CASTLES_SQLITE: str = "sqlite:///castles.gpkg"


def setup_mappings(engine: Engine) -> None:
    castles_table = Table(
        "castlemap-castles",
        mapper_registry.metadata,
        autoload_with=engine,
    )
    mapper_registry.map_imperatively(Castle, castles_table)


def connect_castles_db():
    castles_engine = create_engine(CASTLES_SQLITE)
    setup_mappings(castles_engine)
    with Session(castles_engine) as session:
        rows = session.query(Castle).all()
    return rows
