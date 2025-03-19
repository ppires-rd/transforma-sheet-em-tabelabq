# pip install gspread google-auth google-cloud-bigquery

import gspread
import json
import os
import logging
import uuid

from google.cloud                       import storage,secretmanager,bigquery
from google.oauth2.service_account      import Credentials


PATH_BQ_PROJECT = os.getenv("PATH_BQ_PROJECT")
PATH_BQ_DATASET = os.getenv("PATH_BQ_DATASET")


def echo(texto:str):
    logging.info(texto)
    print(texto)

def getCredenciais(secret_name:str) -> Credentials:
    # Definir os escopos necessários
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",  # Para acessar os Google Sheets
        "https://www.googleapis.com/auth/cloud-platform",  # Para acessar o BigQuery
    ]

    # Criado a conexão do cliente do Secret Manager
    client = secretmanager.SecretManagerServiceClient()

    # Acesse o segredo
    secret_response = client.access_secret_version(name=secret_name)
    secret_data = secret_response.payload.data.decode("UTF-8")

    # O segredo está em formato JSON, então foi passado para um dicionário
    credentials_info = json.loads(secret_data)

    # Return da credencial do JSON.
    return Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

def pegar_dados_sheets(credenciais:Credentials, sheet_id:str, sheet_name_aba:str, intervalo_celulas:str) -> list :
    # Autentificacao para abrir a planilha
    gc = gspread.authorize(credenciais)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/'
    spreadsheet = gc.open_by_url(sheet_url)
    
    if intervalo_celulas.lower() == 'a1':
        worksheet = spreadsheet.worksheet(str(sheet_name_aba))  
        return worksheet.get_all_values()
    else:
        worksheet = spreadsheet.worksheet(sheet_name_aba).get(intervalo_celulas)  
        return worksheet
    
def definicao_schema_table(schema_table:list,valor:list) -> list:
    if schema_table is None:
        return [
            {valor[0][i]: valor[j][i] for i in range(len(valor[0]))}
            for j in range(1, len(valor))
        ]
    else:
        colunas = [item['name'] for item in schema_table]
        return [
            {colunas[i]: valor[j][i] for i in range(len(valor[0]))}
            for j in range(1, len(valor))
        ]

def passar_dados_para_json_gs(valor:list, bucket_name:str,sheet_id:str,json_filename:str,schema_table:list,sheet_name_aba:str):
    TMP_ARQUIVO = f'/tmp/dados-{str(uuid.uuid4())}.json'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)


    # Converte os dados para ter coluna: valor
    resultados = definicao_schema_table(schema_table,valor) 

    num_rows = len(resultados)  # Conta o número de linhas
    echo(f"Total de linhas encontradas: {num_rows}")

    with open(TMP_ARQUIVO, 'w') as f:
        for item in resultados:
            json.dump(item, f)
            f.write('\n')  # Escreve uma nova linha após cada objeto JSON

    PATH_DADOS = f"{json_filename}{sheet_id}/{sheet_name_aba}/dados.json"

    blob = bucket.blob(PATH_DADOS)

    # Fazendo o upload do arquivo local para o bucket
    blob.upload_from_filename(TMP_ARQUIVO)

    # Após o upload, excluir o arquivo local
    os.remove(TMP_ARQUIVO)

    echo(f'Arquivo JSON gerado e salvo em gs://{bucket_name}/{PATH_DADOS}')
    return f"{bucket_name}/{PATH_DADOS}"

def criarTabelaBigQuery(PATH_DADOS_GCS,table_id,schema_table):
    print(f"PATH_BQ_PROJECT : {PATH_BQ_PROJECT}")
    print(f"PATH_BQ_DATASET : {PATH_BQ_DATASET}")
    print(f"PATH_DADOS_GCS : {PATH_DADOS_GCS}")
    print(f"table_id : {table_id}")
    print(f"schema_table : {schema_table}")

    # Criar o cliente do BigQuery
    client = bigquery.Client(project=PATH_BQ_PROJECT)

    # Definir a URI do arquivo no GCP Storage (formato: gs://<bucket>/<file>)
    uri = f'gs://{PATH_DADOS_GCS}'


    # Configurar o job de carregamento
    if isinstance(schema_table, list):
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,  # Tipo de arquivo JSON
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Sobrescrever a tabela existente
            schema=schema_table
        )
    else:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,  # Tipo de arquivo JSON
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Sobrescrever a tabela existente
            autodetect=True
        )

    # Carregar os dados do arquivo JSON no BigQuery
    load_job = client.load_table_from_uri(
        uri, f'{PATH_BQ_DATASET}.{table_id}', job_config=job_config
    )

    # Esperar até que o job seja concluído
    load_job.result()

    # Verificar se a tabela foi criada com sucesso
    table = client.get_table(f'{PATH_BQ_DATASET}.{table_id}')
    return f"{PATH_BQ_PROJECT}.{PATH_BQ_DATASET}.{table_id}"

def geraDadosParaGCS(secretManagerSheet:str,sheet_id:str,sheet_name_aba:str,intervalo_celulas:str,
                    bucket_name:str,json_filename:str,schema_table:list,
                    table_name:str):
    credential = getCredenciais(secretManagerSheet)
    valor = pegar_dados_sheets(credential,sheet_id,sheet_name_aba,intervalo_celulas)

    if isinstance(schema_table, list):
        print("A schema_table é uma lista.")
    else:
        print("Schema definido como none.")
        schema_table = None

    PATH_DADOS_BUCKET = passar_dados_para_json_gs(valor, bucket_name,sheet_id,json_filename,schema_table,sheet_name_aba)
    return criarTabelaBigQuery(PATH_DADOS_BUCKET,table_name,schema_table)
