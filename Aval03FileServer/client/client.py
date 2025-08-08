import socket
import os

HOST = '127.0.0.1'
PORT = 12345

# Diretório de destino para os arquivos baixados
CAMINHO_DESTINO = r"C:\Users\usuario\Downloads\ProgRedes2025.1\Aval03FileServer\client\arquivos"

# Garante que a pasta de destino exista
os.makedirs(CAMINHO_DESTINO, exist_ok=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        comando = input("Digite o comando:\n DIR\n DOW <arquivo>\n MD5 <arquivo> <pos>\n DRA <arquivo> <pos> <hash>\n DMA\n SAIR\n -----\n:")
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
                    try:
                        primeira_linha, conteudo = resposta.split(b"\n", 1)
                        nome_arquivo = primeira_linha.decode().split()[1]
                        caminho_arquivo = os.path.join(CAMINHO_DESTINO, nome_arquivo)
                        
                        modo = "wb"

                        if os.path.exists(caminho_arquivo):
                            opcao = input(f"O arquivo '{nome_arquivo}' já existe. Deseja sobrescrever? (s/n): ").strip().lower()
                            if opcao != 's':
                                print(f"Pulando '{nome_arquivo}'")
                                continue

                        with open(caminho_arquivo, modo) as f:
                            f.write(conteudo)
                        print(f"Arquivo '{nome_arquivo}' salvo com sucesso.")
                    except ValueError:
                        print("Erro ao processar o cabeçalho do arquivo. Recebeu dados inesperados.")
                else:
                    try:
                        print("Resposta do servidor:", resposta.decode('utf-8'))
                    except UnicodeDecodeError:
                        print("Erro: Recebeu dados binários inesperados que não puderam ser decodificados.")
                    break
        else:
            # Outros comandos: DIR, DOW, MD5, DRA
            resposta = s.recv(4096)
            if resposta.startswith(b"ARQUIVO\n") or resposta.startswith(b"CONTINUAR\n"):
                nome = comando.split()[1]
                modo = "ab" if resposta.startswith(b"CONTINUAR\n") else "wb"
                dados = resposta.split(b"\n", 1)[1]
                
                caminho_completo = os.path.join(CAMINHO_DESTINO, nome)
                
                with open(caminho_completo, modo) as f:
                    f.write(dados)
                print(f"Arquivo {nome} salvo em {CAMINHO_DESTINO}")
            else:
                try:
                    print("Resposta do servidor:\n", resposta.decode('utf-8'))
                except UnicodeDecodeError:
                    print("Erro: Recebeu dados binários inesperados que não puderam ser decodificados.")
