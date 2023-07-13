#!/bin/bash

printf "\n"
printf "%s\n" "------------------------------------------"
printf "Script para extraer los datos para el TFM\n"
printf "%s\n" "------------------------------------------"
printf "\n"

# Creando directorios
declare -a types=("nano" "micro" "macro" "mega")
for type in "${types[@]}"; do
    if [ ! -d "$type" ]; then
        mkdir "$type"
        printf "Creando el directorio $type\n"
        printf "\n"
    fi
done

# Llama al script de Python
python3 instaloader_script.py

