# Get Listings

Esse app tem como objetivo capturar dados do ZapImoveis e Vivareal, adicionando a possibilidade da visualização em mapa e um modelo de precificação para identificar os imóveis com melhor custo/benefício.

## Configuração

Criar o arquivo `.env` no seguinte padrão:

```
FLASK_ENV=production
FLASK_APP=listings
PORT=5000

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=listing
```

Para configurar a extração, basta modificar o arquivo `settings.toml`, a única alteração obrigatória neste arquivo é no caso de alteração das configurações do Postgres(usuário, senha ou database). Neste caso, altere a linha [production.SQLALCHEMY_DATABASE_URI] para o padrão `postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:15432/{POSTGRES_DB}`

## Execução

```sh
git clone https://github.com/dobraga/get_listings
cd get_listings
```

```sh
docker-compose -f "docker-compose.yml" up -d --build
```
