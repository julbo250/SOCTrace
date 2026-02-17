#!/bin/bash

echo "=========================================="
echo "🚀 SOC Inventory - Docker"
echo "=========================================="
echo ""

# Vérifications basiques
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non installé!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non installé!"
    exit 1
fi

echo "✅ Docker détecté"
echo ""

# Nettoyage
echo "🧹 Nettoyage..."
docker-compose down 2>/dev/null || true

echo ""
echo "🔨 Construction..."
docker-compose build --no-cache

echo ""
echo "🚀 Démarrage..."
docker-compose up -d

echo ""
echo "⏳ Attente (10s)..."
sleep 10

if docker-compose ps | grep -q "soc-inventory-app"; then
    echo ""
    echo "=========================================="
    echo "✅ APPLICATION DÉMARRÉE!"
    echo "=========================================="
    echo ""
    echo "🌐 http://localhost:5000"
    echo "🔐 -> LOGIN ET MOT DE PASSE DANS LE FICHIER .env"
    echo ""
else
    echo "❌ Erreur!"
    docker-compose logs
    exit 1
fi
