Para configurar a extração, basta modificar o arquivo `aluguel/config/config.toml`.

Para instalar e ativar o environment anaconda, execute:

```sh
conda env create -f env.yml
```

É possível executar de duas formas:

```sh
conda activate aluguel
python ./run.py
```

Ou

```sh
~/anaconda3/envs/aluguel/bin/python ./run.py
```
