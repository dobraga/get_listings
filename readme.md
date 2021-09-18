# Get Listings

Esse app tem como objetivo capturar dados do ZapImoveis e Vivareal, adicionando a possibilidade da visualização em mapa, um modelo de precificação para identificar os imóveis com melhor custo/benefício e a distância da estação de metro/trem mais próxima.

## Configuração

Criar o arquivo `production.env` no seguinte padrão:

```
FLASK_ENV=production
FLASK_APP=listings
PORT=5000

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=listing
```

Para configurar a extração, basta modificar o arquivo `settings.toml`, a única alteração obrigatória neste arquivo é no caso de alteração das configurações do Postgres(usuário, senha ou database). Neste caso, altere a linha [production.SQLALCHEMY_DATABASE_URI] para o padrão `postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}`

## Execução

```sh
git clone https://github.com/dobraga/get_listings
cd get_listings
```

```sh
docker-compose -f "docker-compose.yml" up -d --build
```

## Dashboard

```sh
python dashboard
```

## Desenvolvimento

### Migrações

```sh
export FLASK_APP=dashboard:create_server
flask db init
flask db migrate 
flask db upgrade
```
