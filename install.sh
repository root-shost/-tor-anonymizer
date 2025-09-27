#!/bin/bash

echo "Installing Ultimate Tor Anonymizer..."

# Aggiorna sistema
sudo apt update && sudo apt upgrade -y

# Installa dipendenze
sudo apt install -y tor curl python3 python3-pip docker.io docker-compose

# Installa dipendenze Python
pip3 install -r requirements.txt

# Configura Tor
sudo cp torrc.example /etc/tor/torrc
sudo systemctl enable tor
sudo systemctl start tor

# Configura Docker
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Permessi esecuzione
chmod +x tor-anonymizer.sh
chmod +x *.py

echo "Installation completed!"
echo "Run: ./tor-anonymizer.sh"
