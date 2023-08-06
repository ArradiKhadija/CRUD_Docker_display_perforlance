import csv
import docker

# Chemin du fichier CSV de sortie
chemin_fichier_csv = 'static/csv_files/performance.csv'

# Initialise le client Docker
client = docker.from_env()

# Récupère la liste de tous les conteneurs
conteneurs = client.containers.list()

# Définit les noms des métriques à collecter
noms_metriques = ['ID', 'Nom', 'CPU','system_cpu_usage','cpu_total_usage', 'Mémoire_utilisée', 'Mémoire totale']

# Ouvre le fichier CSV en mode écriture
with open(chemin_fichier_csv, 'w', newline='') as fichier_csv:
    writer = csv.writer(fichier_csv)

    # Écrit les en-têtes des colonnes dans le fichier CSV
    writer.writerow(noms_metriques)

    # Parcourt tous les conteneurs
    for conteneur in conteneurs:
        # Obtient les informations de performance du conteneur
        stats = conteneur.stats(stream=False)

        # Extrait les valeurs des métriques
        conteneur_id = conteneur.short_id
        nom = conteneur.name
        cpu_total_usage=stats['cpu_stats']['cpu_usage']['total_usage']
        system_cpu_usage=stats['cpu_stats']['system_cpu_usage']
        cpu_perc = float(stats['cpu_stats']['cpu_usage']['total_usage']) / float(stats['cpu_stats']['system_cpu_usage']) * 100
        mem_usage = stats['memory_stats']['usage']
        mem_limit = stats['memory_stats']['limit']

        # Écrit une ligne de données dans le fichier CSV
        writer.writerow([conteneur_id, nom,cpu_perc,system_cpu_usage,cpu_total_usage, mem_usage, mem_limit])

# Affiche un message de confirmation
print("Les données ont été écrites dans le fichier CSV avec succès.")

