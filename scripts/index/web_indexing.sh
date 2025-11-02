#!/bin/bash

echo "Iniciando indexación en batch..."
uv run python -m pipelines.web_indexing_pipeline &> logs/web_indexing_pipeline.log
echo "Indexación en batch completada"