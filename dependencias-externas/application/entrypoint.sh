#!/bin/bash

echo "Iniciando entrypoint.sh..."
# Inicialização do serviço SSH
mkdir /run/sshd
service ssh start

echo "Executando comando principal..."

# Alternando para usuário menos privilegiado
su -p host_user -c "python -m uvicorn main:app --proxy-headers --host=0.0.0.0 --port=$APP_PORT --forwarded-allow-ips='*'"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "ENTRYPOINT ERROR: O comando principal falhou com código de saída $EXIT_CODE!"
    echo "ENTRYPOINT INFO: O container continua em execução para depuração."
fi

exec tail -f /dev/null
