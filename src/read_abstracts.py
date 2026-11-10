"""Read all Wikipedia abstracts from the castles-falcon GeoPackage."""

from pathlib import Path

from openai import OpenAI
from sqlalchemy import create_engine, text

GPKG_PATH = Path(__file__).resolve().parent.parent / "castles-falcon.gpkg"
AUDIO_PATH = GPKG_PATH.parent / "audio"


def read_abstracts(db_path: Path = GPKG_PATH) -> list[tuple[str, str | None]]:
    """Return Wikipedia QIDs and abstracts as a list."""
    engine = create_engine(f"sqlite:///{db_path}")
    abstracts: list[tuple[str, str | None]] = []
    with engine.connect() as conn:
        result = conn.execute(text('SELECT "qid", "abstract" FROM "wikipedia"'))
        for row in result:
            abstracts.append((row[0], row[1]))
    return abstracts


def generate_audio(
    abstracts: list[tuple[str, str | None]], output_dir: Path = AUDIO_PATH
) -> None:
    """Generate QID-named MP3 files for nonempty abstracts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAI(base_url="http://hayek:8880/v1", api_key="not-needed")
    for qid, abstract in abstracts:
        if not abstract or not abstract.strip():
            continue
        output_file = output_dir / f"{qid}.mp3"
        if output_file.exists():
            continue
        with client.audio.speech.with_streaming_response.create(
            model="kokoro", voice="af_heart", input=abstract
        ) as response:
            response.stream_to_file(output_file)


if __name__ == "__main__":
    data = read_abstracts()
    print(f"Read {len(data)} abstracts")
    generate_audio(data)
