[voltar](../README.md)

## Shipay - Segundo Desafio

### Code Review

1) Podemos melhorar a separação de contexto dentro da função main.
   Podemos por exemplo ter uma função separada para lidar com leitura do arquivo de configuração, enquanto setamos o path para o arquivo de configurção no topo do script pois assim fica mais clara a declarção da variável e caso seja necessário modificá-la no futuro isso pode ser feito modificando apenas uma linha em vez de ter que buscar a string no arquivo para modificá-la:

    ```
    CONFIGURATION_FILE = "/tmp/bot/settings/config.ini"

    def get_script_configuration():
        configuration = configparser.ConfigParser()
        configuration.read(CONFIGURATION_FILE)

        return configuration
    ```

2) Algumas configurações que estão "hard coded" no script também podem ser melhoradas. Elas podem se    tornar configurações no arquivo de configurações (config.ini) ou serem configuradas no topo do script. Alguns exemplos são os parâmetros de configuração do logging handler e as configurações para acesso ao banco de dados e, nesse caso, isso ainda ajudaria a ocultar as configurações para acesso ao banco que seriam removidas do script. Dessa forma, ficaria algo como:

    ```
    def get_logging_handler(configuration):
        log_filename = configuration.get("logger", "Filename", fallback="bot.log")
        file_max_bytes = configuration.getint("logger", "MaxBytes", fallback=10000)
        backup_count = configuration.getint("logger", "BackupCount", fallback=1)

        handler = RotatingFileHandler(log_filename, max_bytes=file_max_bytes, backupCount=backup_count)
        handler.setLevel(logging.INFO)

        return handler

    def get_database_connection_string(configuration):
        database_user = configuration.get("database", "User")
        database_password = configuration.get("database", "Password")
        database_host = configuration.get("database", "Host")
        database_port = configuration.get("database", "Port")
        database_name = configuration.get("database", "Name")

        return (
            f"postgresql+psycopg2://{database_user}:{database_password}"
            f"@{database_host}:{database_port}/{database_name}"
        )
    ```

3) É possível melhorar os nomes de algumas variáveis para tornar mais explícito seu significado, por exemplo:
    ```
    var1 (interval_in_minutes), task1_instance (export_job_instance), task1_job (export_job)
    ```

4) O print `print('Press Crtl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))` pode ser movido para dentro da função `greetings`

5) Reorganização da função main utilizando as melhorias sugeridas nos tópicos anteriores.

6) A função `task_1` também pode ser melhorada, a começar pelo nome que poderia ser mais descritivo, talvez `export_users_to_spreadsheet`.

    As linhas iniciais da função podem se tornar uma outra função:

    ```
    def get_output_file_path():
        file_name = 'data_export_{0}.xlsx'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
        file_path = os.path.join(os.path.curdir, file_name)
        return file_path
    ```

    A instanciação do workbook também poderia ser modificada para utilizar um context manager:

    ```
    with xlsxwriter.Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()
        orders = db.session.execute('SELECT * FROM users;')

        index = 1
        for order in orders:
            index = index + 1
            write_spreadsheet_header(worksheet)
            write_spreadsheet_content(worksheet, index, order)

        print('Job executed!')
    ```

    A parte responsável por escrever o cabeçalho da planilha também pode ser refatorada para uma função  separada, algo como:

    ```
    def write_spreadsheet_header(worksheet):
        worksheet.write('A1','Id')
        worksheet.write('B1','Name')
        worksheet.write('C1','Email')
        worksheet.write('D1','Password')
        worksheet.write('E1','Role Id')
        worksheet.write('F1','Created At')
        worksheet.write('G1','Updated At')
    ```

    Bem como a parte responsável por escrever o conteúdo da planilha, também pode se tornar uma função separada, algo como:

    ```
    def write_spreadsheet_content(worksheet, index, order):

        write_spreadsheet_row(worksheet, f"A{index}", "Id", order[0])
        write_spreadsheet_row(worksheet, f"B{index}", "Name", order[1])
        write_spreadsheet_row(worksheet, f"C{index}", "Email", order[2])
        write_spreadsheet_row(worksheet, f"D{index}", "Password", order[3])
        write_spreadsheet_row(worksheet, f"E{index}", "Role Id", order[4])
        write_spreadsheet_row(worksheet, f"F{index}", "Created At", order[5])
        write_spreadsheet_row(worksheet, f"G{index}", "Updated At", order[6])


    def write_spreadsheet_row(worksheet, column, name, value):
        print('{0}: {1}'.format(column, value)
        worksheet.write(column, value)
    ```

    Na função acima poderia também utilizar-se de f-strings no lugar dos .format. Além disso poderia se verificar se é possível obter cada
    order como um dicionário para que na função acima sejam utilizados os nomes das colunas/atributos do usuário e seus valores no lugar de índices de uma tupla.

    Uma outra sugestão geral seria adicionar docstrings com descrições sucintas.

Todas as sugestões anteriores visam simplificar as implementações de maneira que cada função tenha objetivos específicos, evitando repetições e facilitando a leitura do código. Essa abordagem de ter o código refatorado em várias funções separadas que realizam trabalhos específicos também facilita o desenvolvimento de testes unitários e torna o código mais "future-proofed", facilitando refatorações, ajustes e melhorias em partes específicas e auto contidas do código.
