from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect,reverse
import subprocess,docker
from math import ceil
import pandas as pd
import os
import base64
from io import BytesIO
import re
from django.http import JsonResponse
from datetime import datetime


def gerer_docker(request, container_id=''):
    try:
        images_result = subprocess.run(['docker', 'images'], capture_output=True, text=True)
        image_lines = images_result.stdout.splitlines()[1:]
        image_details = [
            {
                "name": columns[0],
                "tag": columns[1],
                "image_id": columns[2],
                "size": columns[6],
                "created": f"{columns[3]} {columns[4]} {columns[5]}"
            }
            for line in image_lines
            for columns in [line.split()]
        ]

        ps_result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}'], capture_output=True, text=True)
        ps_output = ps_result.stdout.strip()
        container_lines = ps_output.split('\n')
        containers = [
            {
                'id': columns[0],
                'name': columns[1],
                'image': columns[2],
                'status': columns[3]
            }
            for line in container_lines
            for columns in [line.split('\t')]
        ]

        conteneur = next((c for c in containers if c['id'] == container_id), None)

        context = {'containers': containers, 'conteneur': conteneur, 'image_details': image_details}
        if containers:
            return render(request, "Modele_admin/gerer_docker.html", context)
        else:
            return render(request, "Modele_admin/gerer_docker.html", {'containers': [], 'conteneur': None, 'image_details': image_details})

    except Exception as e:
        return render(request, "Modele_admin/gerer_docker.html", {'error': str(e)})


def create_containers(request):
    if request.method == 'POST':
        name = request.POST['name']
        image = request.POST['image']
        port=request.POST['ports']
        if port and name:
          command = f"docker run -it -d --name {name} -p {port} {image}"
	 
        elif name:
          command =  f"docker run -it -d --name {name} {image}"
        elif port:
          command = f"docker run -it -d -p {port}:80 {image}"
        else:
          command =  f"docker run -it -d {image}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            messages.success(request, "Ajout avec succès")
            with open('containers.txt', 'a') as file:
                file.write(f'Name: {name}, Image: {image}\n')
            return redirect('gerer_docker')
        else:
            messages.error(request, "Erreur lors de la création du conteneur")
            return redirect('gerer_docker')
    
    else:
        return render(request, "Modele_admin/gerer_docker.html")


def delete_containers(request):
    cmd=f'docker stop $(docker ps -aq)'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    command = f'docker rm -f $(docker ps -aq)'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return redirect('gerer_docker')
    else:
        return redirect('gerer_docker')


def delete_container(request, container_id):
    cmd=f'docker stop {container_id}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    command = f'docker rm {container_id}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return redirect('gerer_docker')
    else:
        return redirect('gerer_docker')



def edit_container(request):
    if request.method == 'POST':
        container_id = request.POST.get('container_id')
        name = request.POST.get('container_name')
        image = request.POST.get('container_image')
        command = f'docker rename {container_id} {name}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        commit_command = ['docker', 'commit', container_id]
       
        
    return redirect('gerer_docker')
#---------------------------

def gerer_images(request):
    command = ['docker', 'images']
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    lines = output.splitlines()
    image_details = []
    for line in lines[1:]:
        columns = line.split()
        image_info = {
             "name": columns[0],
            "tag": columns[1],
            "image_id": columns[2],
            "size": columns[6],  
            "created": (columns[3] + ' ' +columns[4] + ' ' + columns[5])
        }
        image_details.append(image_info)

    return render(request, "Modele_admin/gerer_images.html", {'image_details': image_details})




#-------------------------
#predictiion des performances
import matplotlib
matplotlib.use('Agg')  # Utilisation de Matplotlib en mode "non interactif"

import matplotlib.pyplot as plt
def generate_cpu_chart(csv_file):
    data = pd.read_csv(csv_file)
    timestamp = data['Timestamp']
    cpu_percentages = data['CPUsage'].astype(str)
    cpu_values = cpu_percentages.str.extract(r'([\d.]+)').astype(float)
    fig, ax = plt.subplots(figsize=(7, 5))  
    ax.plot(timestamp, cpu_percentages)
    ax.set_title('CPU Usage of Docker Containers')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('CPU Usage (%)')
    ax.set_xticklabels(timestamp, rotation=60)
    ax.set_yticks(range(0, 201, 20))
    ax.set_yticklabels(['{}%'.format(i) for i in range(0, 201, 20)])
    ax.grid(True)
    fig.set_size_inches(fig.get_size_inches()[0], fig.get_size_inches()[1]*1.25) 
    image_path = 'static/dist/img/cpu_chart.png' 
    plt.savefig(image_path, format='png')
    plt.close(fig)

    return image_path


def generate_mem_chart(csv_file):
    data = pd.read_csv(csv_file)
    timestamp = data['Timestamp']
    mem_percentages = data['Ram_usage']
    mem_values = mem_percentages.str.extract(r'([\d.]+)').astype(float)

   
    fig, ax = plt.subplots(figsize=(7, 5))  
    ax.plot(timestamp, mem_values)
    ax.set_title('Memory Usage of Docker Containers')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Memory Usage (MB)')

   
    ax.set_xticklabels(timestamp, rotation=60)  
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels(['{}MB'.format(i) for i in range(0, 101, 10)])
    ax.grid(True)

    
    fig.set_size_inches(fig.get_size_inches()[0], fig.get_size_inches()[1]*1.25)  # Adjust the vertical size multiplier as needed
    

    # Save the chart as an image file
    image_path = os.path.join("static", "dist/img/mem_chart.png") 
    plt.savefig(image_path, format='png')
    plt.close(fig)

    return image_path

def mem_chart_view(request):
    csv_file = os.path.join("static", "csv_files", "memory_usage.csv")
    mem_chart = generate_mem_chart(csv_file)

    return  mem_chart

def cpu_chart_view(request):
    csv_file = os.path.join("static", "csv_files", "memory_usage.csv")
    cpu_chart = generate_cpu_chart(csv_file)

    return  cpu_chart

def convert_size(size):
                    if size < 1024:
                        return f"{size:.2f}B"
                    elif size < 1024 ** 2:
                        return f"{size / 1024:.2f}KB"
                    elif size < 1024 ** 3:
                        return f"{size / (1024 ** 2):.2f}MB"
                    else:
                        return f"{size / (1024 ** 3):.2f}GB"
                          
#performances ressouces---------------------------
def PerformancesDetails(request):
    result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}'], capture_output=True, text=True)
    performances = []
    containers = []
    if result.returncode == 0:
        output = result.stdout.strip()
        lines = output.split('\n')

        for line in lines:
            columns = line.split('\t')
            container_data = {
                'id': columns[0],
                'name': columns[1],
                'image': columns[2],
                'status': columns[3]
            }
            containers.append(container_data)
    else:
        return render(request, 'Modele_admin/PerformancesDetails.html', {'containers': containers})

    total_cpu_usage = 0
    total_ram_usage = 0

    client = docker.from_env()
    docker_info = client.info()
    cpu_count = docker_info['NCPU'] * 100  
    ram_total = docker_info['MemTotal']
    num_containers = docker_info['Containers']
    containerRun = docker_info['ContainersRunning']
    containerStop = docker_info['ContainersStopped']
    ram_limit_str = convert_size(ram_total)

    for container in containers:
        result = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.Container}},{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}', container['id']],
                                capture_output=True, text=True)

        if result.returncode == 0:
            output = result.stdout.strip()
            lines = output.split('\n')

            for line in lines: 
                stats = line.split(',')
                cpu_percentage = float(stats[2].strip('%'))
                total_cpu_usage += cpu_percentage
                ram_usage_str = stats[3].split('/')[0].strip()
                
                performance_data = {
                    'container_id': stats[0],
                    'name': stats[1],
                    'status': container['status'],
                    'cpu_perc': float(stats[2].replace('%', '')),
                    'mem_usage': stats[3].split('/')[0].strip(),
                    'mem_limit': stats[3].split('/')[1].strip(),
                    'mem_perc': float(stats[4].replace('%', '')),
                    'net_io': stats[5],
                    'block_io': stats[6],
                    'pids': stats[7]
                }
                performances.append(performance_data)

                

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

                

                ram_usages = convert(ram_usage_str)
                total_ram_usage += ram_usages
                memory_usage = int((total_ram_usage / ram_total) * 100)
                cpu_usage = int((total_cpu_usage / cpu_count) * 100)
                container_usage = int((containerRun / num_containers) * 100)
                

    ram_usage = convert_size(total_ram_usage)
    chart_cpu = cpu_chart_view(request)
    chart_mem = mem_chart_view(request)
   
    return render(request, 'Modele_admin/PerformancesDetails.html', {
        'performances': performances,
        'total_cpu_usage': total_cpu_usage,
        'cpu_count': cpu_count,
        'total_ram_usage': total_ram_usage,
        'ram_total': ram_total,
        'ram_usage': ram_usage,
        'chart_cpu': chart_cpu,
        'chart_mem': chart_mem,
        'ram_limit_str': ram_limit_str,
        'num_containers': num_containers,
        'containerRun': containerRun,
        'containerStop': containerStop,
        'memory_usage': memory_usage,
        'cpu_usage': cpu_usage,
        'container_usage': container_usage
    })






def start_container(request, container_id):
    cmd = f'docker start {container_id}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        refresh_url = reverse('PerformancesDetails') + '?refresh=true'
        return redirect(refresh_url)
    else:
        return  redirect('PerformancesDetails')







def stop_container(request, container_id):
    cmd=f'docker stop {container_id}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        refresh_url = reverse('PerformancesDetails') + '?refresh=true'
        return redirect(refresh_url)
    else:
        return  redirect('PerformancesDetails')

# search


def get_related_images(request, image_name):
    commande = ['docker', 'search', image_name]
    resultat = subprocess.run(commande, capture_output=True, text=True)

    lignes_resultat = resultat.stdout.split('\n')
    related_images = []

    for ligne in lignes_resultat[1:]:
        if ligne:
            elements = ligne.split()
            name = elements[0]
            description = ''

            if len(elements) >= 4:
                description = ' '.join(elements[1:8])

            related_images.append({
                'name': name,
                'description': description,
            })

    return JsonResponse({"related_images": related_images})

    
# puller l'image docker

def pull_image(request, args):
    try:
        image_name = args  
        result = subprocess.run(["docker", "pull", image_name], capture_output=True, text=True)
        if result.returncode == 0:
            return redirect("gerer_images")
        else:
            print(f"Erreur lors de la suppression de l'image {image_name}: {result.stderr}")
            # Gérer l'erreur selon vos besoins
    
    except FileNotFoundError:
        print("Commande 'docker' introuvable.") 


def run_container(request):
    if request.method == 'POST':
        name = request.POST['name']
        image = request.POST['image']
        port=request.POST['ports']
        if port and name:
          command = f"docker run -it -d --name {name} -p {port} {image}"
        elif port:
          command = f"docker run -it -d -p {port} {image}"
        elif name:
          command =  f"docker run -it -d --name {name} {image}"


        else:
          command =  f"docker run -it -d {image}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            messages.success(request, "Ajout avec succès")
            with open('containers.txt', 'a') as file:
                file.write(f'Name: {name}, Image: {image}\n')
            return redirect('gerer_images')
        else:
            messages.error(request, "Erreur lors de la création du conteneur")
            return redirect('gerer_images')
    
    else:
        return render(request, "Modele_admin/gerer_images.html")
#supprimer images

def delete_image(request, args):
    try:
        # List all container IDs associated with the given image
        image_name = args  # Utiliser directement la valeur de `args` comme nom de l'image
        cmd = f'docker ps -aq --filter "ancestor={image_name}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            container_ids = result.stdout.strip().split()
            if container_ids:
                # Stop and remove all containers associated with the image at once
                stop_all_cmd = f'docker stop {" ".join(container_ids)}'
                subprocess.run(stop_all_cmd, shell=True)

                remove_all_cmd = f'docker rm -f {" ".join(container_ids)}'
                subprocess.run(remove_all_cmd, shell=True)

        remove_image_cmd = f'docker rmi -f {image_name}'
        subprocess.run(remove_image_cmd, shell=True)

        return redirect("gerer_images")

    except FileNotFoundError:
        print("Commande 'docker' introuvable.")
       
    return redirect("gerer_images")




def delete_all_ubuntu_images(request):
    try:
       
        cmd=f'docker stop $(docker ps -aq)'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        command = f'docker rm -f $(docker ps -aq)'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        cmd=f'docker images -a'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        command = f'docker rmi $(docker images -a -q)'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            return redirect('gerer_images')
        else:
            print("Erreur lors de la suppression des images Ubuntu")
            return redirect('gerer_images')  

    except Exception as e:
        print(f"Erreur lors de la suppression des images Ubuntu : {str(e)}")
        return redirect('gerer_images')  # Rediriger vers la vue 'gerer_images' en cas d'erreur
