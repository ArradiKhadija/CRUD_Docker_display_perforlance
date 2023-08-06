
    def get_total_cpu_usage_all_containers():
        client = docker.from_env()
        containers = client.containers.list()
        total_cpu_usage = 0

        # Retrieve Docker host information
        docker_info = client.info()
        cpu_count = docker_info['NCPU']  # Number of CPUs available on the host

        for container in containers:
            stats = container.stats(stream=False)
            cpu_stats = stats['cpu_stats']
            cpu_usage = cpu_stats['cpu_usage']
            system_cpu_usage = stats['precpu_stats']['cpu_usage']['total_usage']
            cpu_delta = cpu_usage['total_usage'] - system_cpu_usage
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percentage = (cpu_delta / system_delta) * 100

            total_cpu_usage += cpu_percentage

        return total_cpu_usage, cpu_count


        # Creating a bar plot
        labels = ['Total CPU Usage', 'CPU Count']
        values = [total_cpu_usage, cpu_count]
        colors = ['blue', 'green']
        plt.barh(labels, values, color=colors)
        plt.xlabel('Percentage')
        plt.title('CPU Cores Usage')
        plt.imshow()



