import datetime
import re
import subprocess
import time
import pandas as pd

csv_file = '/home/khadija/DockerApplicationpython/DockerApplication/static/csv_files/memory_usage.csv'  # Chemin du fichier CSV à générer

def convert(value_str):
    value_match = re.match(r'^([\d.]+)([A-Za-z]+)$', value_str)
    if value_match:
        value = float(value_match.group(1))
        unit = value_match.group(2).lower()
        if 'k' in unit:
            value *= 1024
        elif 'm' in unit:
            value *= 1024 * 1024
        elif 'g' in unit:
            value *= 1024 * 1024 * 1024
        elif 't' in unit:
            value *= 1024 * 1024 * 1024 * 1024
        return value
    else:
        return 0.0

def convert_size(size):
    if size < 1024:
        return f"{size:.2f}B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.2f}KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f}MB"
    else:
        return f"{size / (1024 ** 3):.2f}GB"

total_cpu_usage = 0.0
total_ram_usage = 0.0

result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.ID}}'], capture_output=True, text=True)
containers = []
if result.returncode == 0:
    output = result.stdout.strip()
    lines = output.split('\n')

    for line in lines:
        columns = line.split('\t')
        container_data = {
            'id': columns[0],
        }
        containers.append(container_data)

for container in containers:
    result = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}', container['id']], capture_output=True, text=True)

    if result.returncode == 0:
        output = result.stdout.strip()
        lines = output.split('\n')

        for line in lines:  # Skip the first line (header)
            stats = line.split(',')
            cpu_percentage = float(stats[0].strip('%'))
            total_cpu_usage += cpu_percentage
            ram_usage_str = stats[1].split('/')[0].strip()
            ram_usages = convert(ram_usage_str)
            total_ram_usage += ram_usages

timestamp = datetime.datetime.now().strftime("%H:%M:%S")
new_row = [timestamp, total_cpu_usage, convert_size(total_ram_usage)]

# Charger le fichier CSV existant
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=['Timestamp', 'CPUsage', 'Ram_usage'])

# Ajouter la nouvelle ligne au DataFrame
df = df._append(pd.Series(new_row, index=df.columns), ignore_index=True)

# Conserver uniquement les deux dernières lignes
df = df.tail(11)

# Écrire le DataFrame dans le fichier CSV
df.to_csv(csv_file, index=False)

print("CSV file '{csv_file}' updated.")
print(f"Total CPU Usage: {total_cpu_usage:.2f}%")
print(f"Total RAM Usage: {convert_size(total_ram_usage)}")
