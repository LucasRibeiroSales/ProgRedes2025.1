import socket
import os

HOST = '127.0.0.1'
PORT = 12345

# Garante que a pasta de destino exista
os.makedirs("arquivos", exist_ok=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        comando = input("Digite o comando (DIR, DOW <arquivo>, MD5 <arquivo> <pos>, DRA <arquivo> <pos> <hash>, SAIR): ")
        if comando.strip().upper() == "SAIR":
            break
        s.sendall(comando.encode('utf-8'))
        if comando.upper().startswith("DMA "):
            # Comando DMA: baixar múltiplos arquivos por máscara
            while True:
                resposta = s.recv(4096)

                if resposta.startswith(b"FIMDMA"):
                    print("Todos os arquivos foram recebidos.")
                    break
                elif resposta.startswith(b"ARQUIVO "):
                    # Extrai nome do arquivo
                    primeira_linha, conteudo = resposta.split(b"\n", 1)
                    nome_arquivo = primeira_linha.decode().split()[1]
                    caminho_arquivo = os.path.join("arquivos", nome_arquivo)

                    # Verifica se o arquivo já existe
                    if os.path.exists(caminho_arquivo):
                        opcao = input(f"O arquivo '{nome_arquivo}' já existe. Deseja sobrescrever? (s/n): ").strip().lower()
                        if opcao != 's':
                            print(f"Pulando '{nome_arquivo}'")
                            continue

                    # Salva o arquivo
                    with open(caminho_arquivo, "wb") as f:
                        f.write(conteudo)

                    print(f"Arquivo '{nome_arquivo}' salvo com sucesso.")
                else:
                    print("Erro recebido:", resposta.decode('utf-8'))
                    break

        else:
            # Outros comandos: DIR, DOW, MD5, DRA
            resposta = s.recv(4096)
            if resposta.startswith(b"ARQUIVO\n") or resposta.startswith(b"CONTINUAR\n"):
                nome = comando.split()[1]
                modo = "ab" if resposta.startswith(b"CONTINUAR\n") else "wb"
                dados = resposta.split(b"\n", 1)[1]
                with open(f"arquivos/{nome}", modo) as f:
                    f.write(dados)
                print(f"Arquivo {nome} salvo em arquivos/")
            else:
                print("Resposta do servidor:\n", resposta.decode('utf-8'))
