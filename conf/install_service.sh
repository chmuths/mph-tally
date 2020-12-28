#!/bin/bash
echo "Arrêt du service tally"
sudo systemctl stop tally.service

echo "Copie du fichier de config"
cp config-dual-screen.json ../config.json
cp config-tally_only.json ../config.json

echo "Création du service"
sudo cp tally.service /etc/systemd/system
sudo systemctl enable tally.service

echo "Démarrage du service"
sudo systemctl start tally.service

sleep 5
