# -CLI-Dispatcher


This project implements a small command-line dispatcher that maps fixed natural-language intents to SPARQL queries over the publications dataset.

## How to run

Start Fuseki and load the dataset:

```bash
docker compose up -d
python load_dataset.py