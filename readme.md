# Get Listings

Esse app tem como objetivo capturar dados do ZapImoveis e Vivareal em um único lugar, adicionando a possibilidade da visualização em mapa e um modelo de precificação.

## Configuração

Para configurar a extração, basta modificar o arquivo `./config.toml`.


## Execução

Para instalar os pacotes nescessários, execute:

```sh
pip install -f requirements.txt
```

Para executar o app, basta:

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

## Utilização

A utilização básica é por meio da rotas: `/table` e `/map`.

Um parâmetro obrigatório é o `local`, também é possível utilizar o parâmetro `query` que é opcional.

Por exemplo, para listar todos os imoveis da tijuca, pode acessar: http://127.0.0.1:5000/table?local=tijuca

Para acessar o mapa, podemos usar: http://127.0.0.1:5000/map?local=tijuca

Podemos também realizar alguns filtros como por exemplo: http://127.0.0.1:5000/map?local=tijuca&query=total_fee<=2500+and+bedrooms==2


