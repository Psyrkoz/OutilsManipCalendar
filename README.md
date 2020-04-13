# OutilsManipCalendar

## Cadre de développement

Ce projet est développer dans le cadre du projet de fin d'année de M1 Miage et est à destination de l'université de Haute-Alsace de Mulhouse.\
L'objectif est de pouvoir manipuler un calendrier Google depuis l'application (Ajout / Export de fichier .ics)
Le logiciel est programmé en Python 3 sous Ubuntu 18.04 LTS

## Installation

Pour installer ce logiciel il suffit d'entrée les commandes suivantes:
```bash
git clone https://github.com/Psyrkoz/OutilsManipCalendar
pip install icalendar oauth2client
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Utilisation

Pour lancer le logiciel, il suffit de se rendre dans le répertoire cloné et de lancer main.py:
```bash
cd OutilsManipCalendar
python3 main.py
```
