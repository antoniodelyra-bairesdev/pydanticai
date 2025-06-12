# back-sistema-v2

API interna do sistema Vanguarda

## Setup

O setup assume que você está na pasta raiz do projeto e que os containers "db-postgresql-dev" e "back-fastapi-dev" estão sendo executados.

Execute o script abaixo:

```bash
./back-sistema-v2/setup.sh
```

## Gerar Migration

Para gerar uma migration, basta conectar-se ao container, por meio do comando:

```bash
docker exec -it back-fastapi-dev bash
```

No container, execute o comando abaixo:

```bash
python -m alembic revision -m '[mensagem explicativa soobre o objetivo da migration]'
```
