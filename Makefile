LOCAL_NAME = get_listings
HEROKU_NAME = get-listings

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

init_db: ## Inicializa o banco de dados
	rm -rf migrations/
	export FLASK_APP=dashboard:create_server && flask db init
	export FLASK_APP=dashboard:create_server && flask db migrate 
	export FLASK_APP=dashboard:create_server && flask db upgrade

local_deploy: ## Sobe APP completo
	docker-compose up --build

db: ## Sobe banco de dados
	docker-compose up --build db

dash: ## Executa dashboard
	poetry run python dashboard.py

clear-mlflow: ## Limpa diretórios do MLFlow
	rm -rf mlruns
	rm -rf artifacts
	rm -f mlflow_data.db
	rm -rf utils/model/opt

mlflow: ## Sobe MLFlow na porta 5050
	poetry run mlflow server --backend-store-uri sqlite:///mlflow_data.db --default-artifact-root artifacts -p 5050 --gunicorn-opts "--timeout 0"

export_req: ## Exporta dependências para requirements.txt
	poetry export -o requirements.txt

export_req_dev: ## Exporta dependências de desenvolvimento para requirements-dev.txt
	poetry export -o requirements-dev.txt --dev

clear: ## Limpa notebooks e python
	find . | grep ipynb$ | grep -v .ipynb_checkpoints | xargs jupyter nbconvert --ClearOutputPreprocessor.enabled=True --clear-output
	find . | grep -E "__pycache__" | xargs rm -rf

test: ## Executa os testes
	poetry run pytest -v -x

heroku-deploy: ## Deploy no heroku
	# heroku addons:create heroku-postgresql:hobby-dev -a $(HEROKU_NAME) # Adiciona o postgresql
	# heroku pg:credentials:url -a $(HEROKU_NAME) # Busca informações de conexão com o postgresql

	heroku container:push web -a $(HEROKU_NAME)
	heroku container:release web -a $(HEROKU_NAME)

heroku-log: ## Log da aplicação 
	heroku logs --tail -a $(HEROKU_NAME)
