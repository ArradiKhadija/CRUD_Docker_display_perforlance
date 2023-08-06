#!/bin/bash

# Démarrer le conteneur avec l'image Ubuntu
docker run -it -d ubuntu

# Attendre quelques secondes pour permettre au premier conteneur de démarrer complètement
sleep 20

# Démarrer le conteneur avec l'image Kali Linux
docker run -it -d kalilinux/kali-rolling
