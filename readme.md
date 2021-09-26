# 1. Get Listings

Esse app tem como objetivo capturar dados do ZapImoveis e Vivareal, adicionando a possibilidade da visualização em mapa, um modelo de precificação para identificar os imóveis com melhor custo/benefício e a distância da estação de metro/trem mais próxima.


!["Tabela"](img/table.png)
!["Mapa"](img/mapa.png)

## 1.1. Configuração

Criar o arquivo `production.env` no seguinte padrão:

``` sh
FLASK_ENV=production
FLASK_APP=listings
PORT=5000

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=listing
```

Para configurar a extração, basta modificar o arquivo `settings.toml`.

## 1.2. Execução

```sh
git clone https://github.com/dobraga/get_listings
cd get_listings
```

```sh
docker-compose -f "docker-compose.yml" up -d --build
```


## 1.3. Desenvolvimento

Criar o arquivo `.env` no seguinte padrão:

``` sh
FLASK_ENV=development
FLASK_APP=dashboard
PORT=5000

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=listing
```

### 1.3.1. Migrações

```sh
export FLASK_APP=dashboard:create_server
flask db init
flask db migrate 
flask db upgrade
```

### 1.3.2. Dashboard

Para execução apenas do Dashboard:

``` sh
python dashboard
```
