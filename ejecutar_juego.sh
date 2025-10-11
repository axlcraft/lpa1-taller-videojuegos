#!/bin/bash
# Script para crear entorno virtual, instalar dependencias y ejecutar el juego
set -e

# Crear entorno virtual si no existe
test -d .venv || python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt || pip install pygame numpy

# Configurar DISPLAY para WSL (Windows Subsystem for Linux)
if grep -qiE 'microsoft|wsl' /proc/version; then
	export DISPLAY=:0
	echo "DISPLAY configurado para WSL: $DISPLAY"
fi

# Ejecutar el juego en modo interactivo con audio dummy
echo "Ejecutando el juego en modo interactivo (audio dummy)..."
SDL_AUDIODRIVER=dummy python3 main.py
