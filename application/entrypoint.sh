#!/bin/bash

# Inicialização do serviço SSH
mkdir /run/sshd
service ssh start

# Alternando para usuário menos privilegiado
su -p host_user
python -m uvicorn main:app --proxy-headers --host=0.0.0.0 --port=$APP_PORT --forwarded-allow-ips='*'