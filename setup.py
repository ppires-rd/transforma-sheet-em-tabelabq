from setuptools import setup, find_packages

setup(
    name='transforma_sheet_em_tabelabq',  # Nome do seu pacote
    version='0.1',  # Versão do seu pacote
    description='Biblioteca que faz a transformação do sheet para tabela do bigquery.',
    author='Paulo Pires',  # Seu nome ou nome da organização
    author_email='paulo.pires@rdstation.com',  # Seu e-mail de contato
    url='https://github.com/ppires-rd/transforma-sheet-em-tabelabq',  # URL do repositório (opcional)
    packages=find_packages(),  # Encontrar pacotes automaticamente (ex: mylib/)
    install_requires=[  # Dependências externas, se houver
        # 'numpy', 'requests', etc.
        'gspread','google-cloud-storage','google-cloud-secret-manager','google-cloud-bigquery'
    ],
    classifiers=[  # Classificadores para descrever a biblioteca
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',  # Requisitos de versão do Python
    package_data={
        '': ['./main.py', './operator_gssheet.py'],
    },
)

# build package: python setup.py sdist
