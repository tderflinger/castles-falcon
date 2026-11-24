rm data/landing/castles-falcon.gpkg
rm data/output/castles-falcon.gpkg
cp data/landing/castles.gpkg data/output/castles-falcon.gpkg
source ./.venv/bin/activate
uv sync --frozen
python3 src/main.py $1 $2
