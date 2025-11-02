#!/bin/bash

echo "Iniciando indexación en batch..."
# uv run python -m pipelines.pdf_indexing_pipeline &> logs/pdf_indexing_pipeline.log
uv run python -m pipelines.pdf_indexing_pipeline &> /dev/null
echo "Indexación en batch completada"