#!/bin/bash
echo "==================================="
echo "  PandaRey Bot - Instalacion"
echo "==================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no esta instalado. Instalalo desde https://python.org"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "🚀 Iniciando el bot..."
python3 bot.py
