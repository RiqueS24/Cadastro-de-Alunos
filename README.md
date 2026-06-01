# Cadastro-de-Alunos
Sistema de Cadastro de Alunos

## Configuracao do MySQL

Instale a dependencia:

```powershell
python -m pip install -r requirements.txt
```

Execute o sistema:

```powershell
python main.py
```

Uma tela de conexao sera exibida antes da tela principal. Informe o servidor,
a porta, o usuario, a senha e o nome do banco MySQL.

Se aparecer a mensagem "Acesso negado pelo MySQL", informe a senha configurada
para o usuario escolhido. Por padrao, o formulario abre com o usuario `root`,
mas nao preenche uma senha automaticamente.

Opcionalmente, defina valores iniciais para preencher a tela automaticamente:

```powershell
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "sua_senha"
$env:MYSQL_DATABASE = "cadastro_alunos_estacio"
python main.py
```

O sistema cria automaticamente o banco e as tabelas caso ainda nao existam.
