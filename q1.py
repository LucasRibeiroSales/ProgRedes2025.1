# Programa para receber o nome de um arquivo .pcap pela linha de comando

#Importa a biblioteca para verificar se o arquivo existe
import os
# Importa função para ler arquivos .pcap
from scapy.all import rdpcap, Ether, ARP, IP, ICMP, UDP, TCP

# Solicita ao usuário o nome do arquivo .pcap
nome_arquivo = input("Digite o nome do arquivo .pcap: ")

# Verifica se o arquivo existe no computador
if os.path.isfile(nome_arquivo):
    print(f"Arquivo encontrado: {nome_arquivo}")

# Lê os pacotes do arquivo .pcap
    pacotes = rdpcap(nome_arquivo)

# Percorre cada pacote capturado
    for i, pacote in enumerate(pacotes):
        print(f"Pacote {i+1}:")

        # Verifica se o pacote tem camada Ethernet (camada de enlace)
        if pacote.haslayer("Ethernet"):
            camada_ethernet = pacote[Ether]

             # Colher os MACs de origem e destino
            mac_origem = pacote.src
            mac_destino = pacote.dst
            print(f"MAC de Origem: {mac_origem}")
            print(f"MAC de Destino: {mac_destino}\n")

             # Verificando o campo 'type' da camada Ethernet
            tipo_protocolo = camada_ethernet.type

            # Análise com base no campo 'type'
            if tipo_protocolo == 0x0806:  # ARP ou RARP
                print("Protocolo no Enlace: ARP ou RARP")

                # Verificar se o pacote tem camada ARP
                if pacote.haslayer(ARP):
                    operacao = pacote[ARP].op

                    # Identificar se é ARP ou RARP pela operação
                    if operacao == 1:
                        tipo_operacao = "ARP Request"
                    elif operacao == 2:
                        tipo_operacao = "ARP Reply"
                    elif operacao == 3:
                        tipo_operacao = "RARP Request"
                    elif operacao == 4:
                        tipo_operacao = "RARP Reply"
                    else:
                        tipo_operacao = f"Operação desconhecida (código {operacao})"
                        
                        print(f"Tipo de Operação: {tipo_operacao}")

                        # Exibir MACs e IPs do remetente e destinatário
                    mac_remetente = pacote[ARP].hwsrc
                    mac_destinatario = pacote[ARP].hwdst
                    ip_remetente = pacote[ARP].psrc
                    ip_destinatario = pacote[ARP].pdst

                    print(f"MAC Remetente: {mac_remetente}")
                    print(f"MAC Destinatário: {mac_destinatario}")
                    print(f"IPv4 Remetente: {ip_remetente}")
                    print(f"IPv4 Destinatário: {ip_destinatario}")

            elif tipo_protocolo == 0x0800:  # IPv4
                print("Protocolo no Enlace: IPv4")

                    # Verifica se o pacote tem camada IP
                if pacote.haslayer(IP):
                    camada_ip = pacote[IP]
                    ip_origem = pacote[IP].src
                    ip_destino = pacote[IP].dst
                    versao_ip = camada_ip.version
                    tamanho_total = camada_ip.len
                    ttl = camada_ip.ttl
                    checksum = camada_ip.chksum

                    print(f"IPv4 de Origem: {ip_origem}")
                    print(f"IPv4 de Destino: {ip_destino}")
                    print(f"Versão IP: {versao_ip}")
                    print(f"Tamanho Total (Total Length): {tamanho_total}")
                    print(f"Time To Live (TTL): {ttl}")
                    print(f"Header Checksum: {checksum}")

                    # Verificando se tem ICMP
                    if camada_ip.proto == 1:  # Protocolo ICMP tem número 1
                        if pacote.haslayer(ICMP):
                            camada_icmp = pacote[ICMP]
                            tipo_icmp = camada_icmp.type

                            # Nome descritivo para os 5 tipos principais

                            nomes_icmp = {
                                0: "Echo Reply",
                                3: "Destination Unreachable",
                                5: "Redirect",
                                8: "Echo Request",
                                11: "Time Exceeded"
                            }
                            nome_tipo = nomes_icmp.get(tipo_icmp, "Outro Tipo ICMP")

                            print(f"Protocolo de Transporte: ICMP")
                            print(f"Tipo ICMP: {tipo_icmp} - {nome_tipo}")

                            # Se for Echo Request (8) ou Echo Reply (0), mostrar ID e Seq

                            if tipo_icmp == 8 or tipo_icmp == 0:
                                identificador = camada_icmp.id
                                sequencia = camada_icmp.seq
                                print(f"Identificador: {identificador}")
                                print(f"Número de Sequência: {sequencia}")
                        #UDP
                        elif camada_ip.proto == 17 and pacote.haslayer(UDP):
                            camada_udp = pacote[UDP]
                            porta_origem = camada_udp.sport
                            porta_destino = camada_udp.dport

                            print("Protocolo de Transporte: UDP")
                            print(f"Porta de Origem: {porta_origem}")
                            print(f"Porta de Destino: {porta_destino}")
                        #TCP
                        elif camada_ip.proto == 6 and pacote.haslayer(TCP):
                            camada_tcp = pacote[TCP]
                            porta_origem = camada_tcp.sport
                            porta_destino = camada_tcp.dport
                            numero_sequencia = camada_tcp.seq
                            numero_ack = camada_tcp.ack
                            flags = camada_tcp.flags
                            janela = camada_tcp.window

                            print("Protocolo de Transporte: TCP")
                            print(f"Porta de Origem: {porta_origem}")
                            print(f"Porta de Destino: {porta_destino}")
                            print(f"Número de Sequência: {numero_sequencia}")
                            print(f"Número de Reconhecimento (ACK): {numero_ack}")
                            print(f"Flags: {flags}")
                            print(f"Tamanho da Janela: {janela}")
                else:
                    print("Aviso: O pacote tem type IPv4 na camada Ethernet, mas não tem camada IP no Scapy.")

            else:
                print(f"Outro tipo de protocolo no enlace (type = {hex(tipo_protocolo)})")
        
        else:
            print("Pacote sem camada Ethernet.")

        print("-" * 40)  # Linha separadora

else:
    print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado no diretório atual.")
