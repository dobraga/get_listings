# Get Listings

Esse app tem como objetivo capturar dados do ZapImoveis e Vivareal em um único lugar, adicionando a possibilidade da visualização em mapa e um modelo de precificação.

## Configuração

Para configurar a extração, basta modificar o arquivo `./config.toml`.


## Execução

```sh
git clone https://github.com/dobraga/get_listings
cd get_listings
```

### Sem Docker

Para instalar os pacotes nescessários, execute:

```sh
pip install -r requirements.txt
```

Para executar o app, defina as seguintes variáveis:

No linux:
``` sh
export FLASK_APP=app/app.py
```

No windows:
``` sh
set FLASK_APP=app/app.py
```

E depois disso, execute:

``` sh
flask run
```

### Com docker

```sh
docker-compose -f "docker-compose.yml" up -d --build
```
