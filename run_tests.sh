#!/bin/bash

# Lista de archivos de prueba
test_files=(
    "test/test_get_empty_games.py"
    "test/test_get_games.py"
    # Agrega aquí cualquier otro archivo de prueba
)

# Ejecuta cada archivo de prueba individualmente
for file in "${test_files[@]}"; do
    echo "Running tests in $file"
    pytest $file
done