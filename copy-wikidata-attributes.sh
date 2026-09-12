rm ./castles-falcon.gpkg
cp ./castles.gpkg ./castles-falcon.gpkg
source ./.venv/bin/activate
python3 src/main.py $1
