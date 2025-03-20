# Transformar sheet em tabela do bigquery


---
## Pré-requisito:
Sheet: No sheet, será necessário dar permissão view para a service account especifico. 

### Fazer build do pacote: 
```
# python setup.py sdist && gsutil cp dist/transforma_sheet_em_tabelabq-*.tar.gz gs://isd-data-business-repo-teste/python/lib/
```


### Fazer o import do pacote no código:
```
! gsutil cp gs://isd-data-business-repo-teste/python/lib/transforma_sheet_em_tabelabq-0.1.tar.gz .

! pip install ./transforma_sheet_em_tabelabq-0.1.tar.gz

from  transforma_sheet_em_tabelabq import operator_sheet2bq
```
#### Variaveis configuraveis: 
```
PATH_SECRET_MANAGER = "" # Caminho do secret manager que tem a SA de acesso ao sheet.
SHEET_ID = ""   # Id da sheet que será passado para a tabela do bigquery
SHEET_ABA = "" # Nome da aba da sheet.
SHEET_RANGE = "" # Se for pegar o dados da aba todao, usar 'A1', caso seja um range especifico, usar o seguinte exemplo : 'B3:Q23'
BUCKET_NAME = "" # Nome do bucket que será salvo os dados temporario.
BUCKET_PATH = "" # Endeço do bucket para salvar os arquivos temporario.
TABELA_SCHEMA = None # Usar None se não tiver schema da tabela, ou especificar como list a tabela do bigquery.
TABELA_NAME = "" # Nome da tabela que será salva.
```
exemplo:
```
PATH_SECRET_MANAGER = "projects/661498714774/secrets/sa_json_rd-isd-stg-01/versions/1" 
SHEET_ID = "1sN0R5VLqEEDfvJ8n5tR4wHrShJUoRyU6XyOywZ8cNkA"   
SHEET_ABA = "localidades"
SHEET_RANGE = "a1"
BUCKET_NAME = "isd-data-business-repo-teste"
BUCKET_PATH = "teste/modelo/"
TABELA_SCHEMA = None
TABELA_NAME = "local_campeoes"
```

#### Usar o modulo completo:
```
PATH_BQ_PROJECT = "rd-isdpoctmp-stg-01"
PATH_BQ_DATASET = "google_sheets_raw"

PATH_DA_TABELA_BQ = operator_sheet2bq.geraDadosParaGCS(
                    PATH_SECRET_MANAGER,
                    SHEET_ID,SHEET_ABA,SHEET_RANGE,
                    BUCKET_NAME,BUCKET_PATH,
                    TABELA_NAME,TABELA_SCHEMA,
                    PATH_BQ_PROJECT,PATH_BQ_DATASET)

print(PATH_DA_TABELA_BQ)
```


#### Usar o modulo passo a passso:
```
credential = operator_sheet2bq.getCredenciais(
    PATH_SECRET_MANAGER)

dados = operator_sheet2bq.pegar_dados_sheets(
    credential,
    SHEET_ID,SHEET_ABA,
    SHEET_RANGE)

PATH_DADOS_BUCKET = operator_sheet2bq.passar_dados_para_json_gs(
    dados, 
    BUCKET_NAME,
    SHEET_ID,
    BUCKET_PATH,
    TABELA_SCHEMA,
    SHEET_ABA)

PATH_TABELA = operator_sheet2bq.criarTabelaBigQuery(
    PATH_DADOS_BUCKET,
    TABELA_NAME,
    TABELA_SCHEMA, 
    PATH_BQ_PROJECT, 
    PATH_BQ_DATASET)

print(PATH_TABELA)
```


## Videos 
### Fazer o build do projeto
https://drive.google.com/file/d/1cfZ1hniv4rLdzQfXhQQrvKO-YcPmGyId/view?usp=drive_link

### Fazer a integração com o notebook. 
https://drive.google.com/file/d/1vxMNX3tXMJOWiYTnCz2XDq3GmTtIPyXP/view?usp=drive_link