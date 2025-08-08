# Servidor TCP Multi-threaded
# Importa as bibliotecas necessárias
import socket #--------------------------------------------------------------------- Para comunicação via rede (TCP)
import threading #------------------------------------------------------------------ Para lidar com múltiplas conexões ao mesmo tempo
import os #------------------------------------------------------------------------- Para listar arquivos e obter tamanhos
import hashlib #-------------------------------------------------------------------- Biblioteca para calcular hash MD5
import glob 

# Define o IP e a porta que o servidor vai escutar
HOST = '127.0.0.1' #-------------------------------------------------------------- IP do servidor
PORT = 12345 #---------------------------------------------------------------------- Porta TCP para escutar conexões

# Diretório base para arquivos permitidos
PASTA_ARQUIVOS = r"C:\Users\usuario\Downloads\ProgRedes2025.1\Aval03FileServer\server\arquivos"
PASTA_ARQUIVOS_ABSOLUTA = PASTA_ARQUIVOS

# Função que será executada em uma nova thread para cada cliente
def handle_client(con, cliente):
    print("Conectado por:", cliente)

    while True:
        try:
            # Recebe até 1024 bytes de dados do cliente
            msg = con.recv(1024)
            # Se não receber nada, o cliente desconectou
            if not msg:
            # Em caso de erro, sai do loop
                break
            # Converte os bytes recebidos em string e remove espaços extras
            comando = msg.decode('utf-8').strip()
        
# Verifica se o cliente solicitou a listagem de arquivos
            if comando.upper() == "DIR": #------------------------------------------ Se o comando for 'DIR', listar arquivos e seus tamanhos
                resposta = ""
                arquivos = os.listdir(PASTA_ARQUIVOS) #---------------------------------------- Lista arquivos no diretório atual
            # Para cada item, verifica se é um arquivo e obtém seu tamanho
                for arquivo in arquivos:
                    caminho_completo = os.path.join(PASTA_ARQUIVOS, arquivo)
                    if os.path.isfile(caminho_completo):
                        tamanho = os.path.getsize(caminho_completo)
                        resposta += f"{arquivo} - {tamanho} bytes\n"
            # Se não houver arquivos
                if not resposta:
                    resposta = "Nenhum arquivo encontrado.\n"
            # Envia a resposta de volta para o cliente
                con.sendall(resposta.encode('utf-8'))
            
            # Tratamento do comando DOW para download de arquivos
            elif comando.upper().startswith("DOW "):
                nome_arquivo = comando[4:].strip()  # Extrai o nome do arquivo após 'DOW '
                caminho = os.path.join(PASTA_ARQUIVOS, nome_arquivo)  # Define o caminho para a pasta 'arquivos'

                # Verifica se o arquivo existe e é um arquivo regular
                if os.path.isfile(caminho):
                    with open(caminho, "rb") as f:
                        conteudo = f.read()
                    # Envia uma tag inicial para o cliente saber que é um arquivo
                    con.sendall(b"ARQUIVO\n")
                    con.sendall(conteudo)
                else:
                    msg_erro = "ERRO: Arquivo não encontrado ou acesso negado.\n"
                    con.sendall(msg_erro.encode('utf-8'))
            # Comando MD5 - calcular hash MD5 de parte do arquivo
            elif comando.upper().startswith("MD5 "): # Identifica o comando
                # Verifica se a sintaxe está correta: MD5 nome posição
                partes = comando.split()
                if len(partes) != 3:
                    con.sendall(b"ERRO: Formato invalido. Use: MD5 nome_arquivo posicao\n")
                else:
                    nome_arquivo = partes[1]
                    try:
                        posicao = int(partes[2]) # Converte a posição para inteiro, valida se está dentro do tamanho do arquivo.
                        caminho = os.path.join("arquivos", nome_arquivo)

                        # Verifica se o arquivo existe
                        if not os.path.isfile(caminho):
                            con.sendall(b"ERRO: Arquivo nao encontrado.\n")
                        else:
                            tamanho_arquivo = os.path.getsize(caminho)

                            # Limita a posição ao tamanho do arquivo
                            if posicao < 0 or posicao > tamanho_arquivo:
                                con.sendall(b"ERRO: Posicao invalida.\n")
                            else:
                                with open(caminho, "rb") as f:
                                # Lê os bytes até a posição e calcula o hash com hashlib.md5()
                                    conteudo = f.read(posicao)
                                # Calcula o hash MD5 dos bytes lidos
                                hash_md5 = hashlib.md5(conteudo).hexdigest()
                                con.sendall(f"MD5: {hash_md5}\n".encode('utf-8'))
                    except ValueError:
                        con.sendall(b"ERRO: Posicao deve ser um numero inteiro.\n")
            # Comando DRA - Continuação de download com verificação de hash
            elif comando.upper().startswith("DRA "): # Detecta comando de continuação de download.
                partes = comando.split()
                if len(partes) != 4:
                    con.sendall(b"ERRO: Formato invalido. Use: DRA nome_arquivo posicao hash_md5\n")
                else:
                    nome_arquivo = partes[1] # Extrai os três argumentos: nome, posição e hash MD5.
                    caminho = os.path.join("arquivos", nome_arquivo)
                    try:
                        posicao = int(partes[2]) # Extrai os três argumentos: nome, posição e hash MD5.
                        hash_cliente = partes[3] # Extrai os três argumentos: nome, posição e hash MD5.

                        # Verifica se o arquivo existe
                        if not os.path.isfile(caminho):
                            con.sendall(b"ERRO: Arquivo nao encontrado.\n")
                        else:
                            tamanho = os.path.getsize(caminho)
                            if posicao < 0 or posicao > tamanho:
                                con.sendall(b"ERRO: Posicao invalida.\n")
                            else:
                                with open(caminho, "rb") as f:
                                    parte_inicial = f.read(posicao)  # Lê os primeiros bytes
                                    hash_servidor = hashlib.md5(parte_inicial).hexdigest() # Calcula o hash dos primeiros bytes do arquivo no servidor

                                    # Compara o hash recebido com o hash do servidor
                                    # Se o hash bater, envia o restante do arquivo a partir da posição solicitada.
                                    if hash_cliente == hash_servidor:
                                        restante = f.read()  # Lê o restante do arquivo
                                        con.sendall(b"CONTINUAR\n")
                                        con.sendall(restante)
                                    else:
                                        con.sendall(b"ERRO: Hash MD5 nao confere. Transferencia abortada.\n")
                    except ValueError:
                        con.sendall(b"ERRO: Posicao deve ser um numero inteiro.\n")

            # Comando DMA - download múltiplo por máscara (*.ext)
            elif comando.upper().startswith("DMA "):
                padrao = comando[4:].strip()
                base_dir = os.path.realpath("arquivos")
                arquivos_encontrados = glob.glob(os.path.join("arquivos", padrao))

                if not arquivos_encontrados:
                    con.sendall(b"ERRO: Nenhum arquivo corresponde a mascara fornecida.\n")
                else:
                    for caminho_absoluto in arquivos_encontrados:
                        caminho_real = os.path.realpath(caminho_absoluto)
                        # Verifica se está dentro da pasta permitida
                        if not caminho_real.startswith(base_dir):
                            continue

                        nome_arquivo = os.path.basename(caminho_real)
                        if os.path.isfile(caminho_real):
                            with open(caminho_real, "rb") as f:
                                conteudo = f.read()
                            con.sendall(f"ARQUIVO {nome_arquivo}\n".encode('utf-8'))
                            con.sendall(conteudo)
                    # Sinaliza o fim da transferência
                    con.sendall(b"FIMDMA\n")

            else:
            # Se não for o comando DIR, apenas imprime a mensagem recebida
                print(f"Mensagem de {cliente}: {comando}")
        except:
            # Em caso de erro na comunicação, encerra a conexão
            break
    print("Finalizando conexão do cliente:", cliente)
    con.close() # Fecha o socket de conexão com o cliente

            # Cria o socket TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #------------------- Cria o socket TCP (IPv4 + TCP)
tcp_socket.bind((HOST, PORT))#----------------------------------------------------- Associa o socket ao IP e porta definidos
# Coloca o socket no modo "escuta" 
tcp_socket.listen(5)#-------------------------------------------------------------- Permite até 5 conexões pendentes na fila de espera

print("Servidor TCP Multi-threaded aguardando conexões...\n")


# Loop principal do servidor: aguarda conexões indefinidamente
while True:
    con, cliente = tcp_socket.accept()#-------------------------------------------- Aceita uma nova conexão de cliente
    client_thread = threading.Thread(target=handle_client, args=(con, cliente))#--- Cria uma nova thread para lidar com esse cliente
    client_thread.start() #-------------------------------------------------------- Inicia a thread (executa handle_client)
