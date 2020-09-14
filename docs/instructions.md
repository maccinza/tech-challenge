[voltar](../README.md)

## Shipay - Primeiro Desafio

### Considerações iniciais

Como mencionado na página inicial de documentação, assume-se que o ambiente utilizado para a execução e teste da aplicação é compatível com as versões das ferramentas lá listadas.

É especialmente importante que a máquina possua Python 3.8.1 e que as versões de Docker e Docker Compose sejam compatíveis, além de a máquina host estar conectada à internet para baixar as imagens docker e dependências necessárias.

### Variáveis de ambiente

Para conseguir executar o projeto (localmente ou com docker) é necessário criar dois arquivos com variáveis de ambiente:
  - `.env.db`
  - `.env.app`

O conteúdo de  deve definir as variáveis contendo os valores do nome do banco de dados (`POSTGRES_DB`), o usuário do banco de dados (`POSTGRES_USER`) e a senha para o acesso ao banco de dados (`POSTGRES_PASSWORD`):
  ```
  POSTGRES_USER=<usuario_desejado>
  POSTGRES_PASSWORD=<senha_desejada>
  POSTGRES_DB=<banco_desejado>
  ```
Um exemplo seria:
  ```
  POSTGRES_USER=shipay_user
  POSTGRES_PASSWORD=shipay_password
  POSTGRES_DB=shipay_db
  ```

O conteúdo de `.env.app` deve definir as variáveis contendo os valores para conexão ao banco de dados com os mesmos valores configurados em `.env.db`. Além destes, devem ser configurados a chave secreta da aplicação, host e porta do banco de dados, e a definição de espera para que o banco de dados esteja rodando para que a aplicação suba (docker):
  ```
  SECRET_KEY=<chave_secreta>
  DB_NAME=<banco_desejado>
  DB_USER=<usuario_desejado>
  DB_PASSWORD=<senha_desejada>
  DB_HOST=postgres
  DB_PORT=5432
  WAIT_HOSTS=postgres:5432
  ```
Um exemplo compatível com o exemplo anterior (`.env.db`) seria:
  ```
  SECRET_KEY=acg-8e$#e73c4#6i6_f%ed6xnxd#l21b-aujr!^8+e_7v=$y#l
  DB_NAME=shipay_db
  DB_USER=shipay_user
  DB_PASSWORD=shipay_password
  DB_HOST=postgres
  DB_PORT=5432
  WAIT_HOSTS=postgres:5432
  ```

### Rodando a aplicação

A aplicação pode ser rodada localmente na máquina host (somente com o banco de dados rodando em um container docker) ou totalmente dockerizada (aplicação e banco).

#### Aplicação dockerizada

Para rodar a aplicação totalmente dockerizada basta rodar o seguinte comando:
  ```
  make run_dockerized_app
  ```
Se tudo ocorrer como o esperado, a imagem docker da aplicação deverá ser montada, a imagem docker para o banco de dados baixada, e ambas imagens devem ser rodadas em containeres docker orquestrados.7

Ao fim do processo deve ser possível ver na shell que a aplicação está rodando em `http://0.0.0.0:8000/`, então basta acessar algum dos endpoints utilizando o navegador:
  - http://localhost:8000/api/v1/transacao
  - http://localhost:8000/api/v1/transacoes/estabelecimento?cnpj=<cnpj_valido_existente>

#### Aplicação local

Para rodar a aplicação em modo local será necessário instalar o ambiente em sua máquina.
Pode ser necessário instalar as dependências para o `psycopg2`:
  ```
  sudo apt install libpq-dev python3-dev
  ```

Se tudo estiver correto deveria bastar executar o seguinte comando:
  ```
  make start_app_local
  ```
Obs.: Caso a aplicação não consiga rodar porque o banco não subiu a tempo, aumente o intervalo de espera através da variável `WAIT_FOR_DB` no topo do `Makefile`.

O comando instala o ambiente virtual python com as dependências da aplicação, baixa e roda a imagem do banco de dados, aplica as migrações de modelos ao banco, importa os dados de exemplo das empresas (contidos na pasta `data` na raiz do projeto) e roda a aplicação.

Ao fim desse processo deve ser possível ver na shell que a aplicação está rodando em `http://0.0.0.0:8000/`, então basta acessar algum dos endpoints utilizando o navegador:
  - http://localhost:8000/api/v1/transacao
  - http://localhost:8000/api/v1/transacoes/estabelecimento?cnpj=<cnpj_valido_existente>

### Comandos úteis

Para realizar análise estática do código:
  ```
  make lint
  ```

Para executar os testes unitários:
  ```
  # (aplicação em modo local)
  make test
  # (aplicação dockerizada)
  make test_dockerized
  ```

Para importar dados de estabelecimentos:
  ```
  # (aplicação em modo local)
  make import_companies
  # (aplicação dockerizada)
  make import_companies_dockerized
  ```

### Utilizando a aplicação

Para utilizar a aplicação é necessário inicialmente importar alguns dados de estabelecimentos, o que pode ser feito manualmente com os comandos listados anteriormente ou automaticamente com os comandos listados anteriormente para rodar a aplicação.
Caso queira incluir outros estabelecimentos basta adicionar dados válidos ao arquivo `data/companies.json`.

Antes de utilizar a aplicação garanta que ela está rodando corretamente.

#### Registro de transação

Para realizar o registro de uma transação pode-se:
  1) Acessar http://localhost:8000/api/v1/transacao utilizando um navegador
  2) Utilizar o formulário, fornecendo um cnpj (Estabelecimento) válido de um estabelecimento cujos dados tenham sido importados para o banco, um cpf válido (Cliente), o valor da transação (Valor), uma descrição (Descrição) para a transação
  3) Clicar no botão `Post`
  4) Verificar na mesma página se o registro da transação foi aceito (`{"aceito":true}`) ou não ({"aceito":false})

Ou realizar uma requisição HTTP POST utilizando `curl` por exemplo:
  ```
  curl --header "Content-Type: application/json" --request POST --data '{"estabelecimento":"<CNPJ>","cliente":"<CPF>","valor":<VALOR>,"descricao":"<DESCRICAO>"}' http://localhost:8000/api/v1/transacao
  ```

#### Relatório de transações

Para acessar o relatório de transações de um estabelecimento pode-se:
  1) Acessar http://localhost:8000/api/v1/transacoes/estabelecimento?cnpj=<CNPJ> utilizando um navegador
  2) Verificar o relatório gerado para o estabelecimento informado ou a mensagem de erro gerada

Ou realizar uma requisição HTTP GET utilizando `curl` por exemplo:
  ```
  curl --header "Content-Type: application/json" --request GET http://localhost:8000/api/v1/transacoes/estabelecimento?cnpj=<CNPJ>
  ```

### Melhorias

Algumas melhorias poderiam ser implementadas (não foram implementadas por estarem fora do escopo do desafio proposto):
  1) Implementação de endpoint para cadastro de estabelecimento
  2) Implementação de endpoint para listagem de estabelecimentos cadastrados
  3) Melhor configuração da aplicação, separando settings específicas para o ambiente de desenvolvimento e produção
  4) Inclusão da criação e hospedagem da imagem no flow de ci/cd
  5) Melhoria da documentação da API (self describing API) e geração automática de documentação (OpenAPI).
