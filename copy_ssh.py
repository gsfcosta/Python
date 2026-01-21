#!/usr/bin/env python3

import paramiko
import getpass

# Configurações
SSH_USER = "root"
SSH_PASSWORD = "#"  # Coloque a senha aqui
DEST_USER = "#"
DEST_GROUP = "#"
IP_LIST = "ips.txt"

def obter_chave_publica():
    """Obtém a chave pública local"""
    try:
        with open('/root/.ssh/id_rsa.pub', 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Erro ao ler chave pública: {e}")
        return None

def configurar_servidor(ip, chave_publica):
    """Configura um servidor em UMA única conexão"""
    try:
        # Conectar
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=SSH_USER, password=SSH_PASSWORD)

        print(f"🔧 Configurando {ip}...")

        # Executar TODOS os comandos na mesma sessão
        comandos = [
            # 1. Criar usuário
            f"sudo useradd {DEST_USER} -G {DEST_GROUP} -m -d /home/{DEST_USER} -s /bin/bash",

            # 2. Configurar SSH
            f"sudo -u {DEST_USER} ssh-keygen -t rsa -f /home/{DEST_USER}/.ssh/id_rsa -N '' -q",

            # 3. Adicionar chave pública
            f"echo '{chave_publica}' | sudo -u {DEST_USER} tee /home/{DEST_USER}/.ssh/authorized_keys > /dev/null",

            # 4. Ajustar permissões
            f"sudo chmod 644 /home/{DEST_USER}/.ssh/authorized_keys"
        ]

        for cmd in comandos:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # Esperar comando terminar
            stdout.channel.recv_exit_status()

        ssh.close()
        return True

    except Exception as e:
        print(f"❌ Erro em {ip}: {e}")
        return False

def main():
    print("🚀 Iniciando configuração automática...")

    # Obter chave pública
    chave_publica = obter_chave_publica()
    if not chave_publica:
        return

    # Ler IPs
    try:
        with open(IP_LIST, 'r') as f:
            ips = [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        print(f"❌ Arquivo {IP_LIST} não encontrado")
        return

    # Processar cada servidor
    for ip in ips:
        print(f"📡 Processando: {ip}")

        if configurar_servidor(ip, chave_publica):
            print(f"✅ {ip} - Configurado com sucesso")
        else:
            print(f"❌ {ip} - Falha na configuração")

        print("----------------------------------------")

    print("🎉 Configuração concluída!")

if __name__ == "__main__":
    main()
