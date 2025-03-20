from setuptools import setup, find_packages

setup(
    name='transforma_sheet_em_tabelabq', 
    version='0.1.0', 
    description='Biblioteca que faz a transformação do sheet para tabela do bigquery.',
    author='Paulo Pires', 
    author_email='paulo.pires@rdstation.com',
    url='https://github.com/ppires-rd/transforma-sheet-em-tabelabq',
    packages=find_packages(),
    install_requires=[  
        'gspread','google-cloud-storage','google-cloud-secret-manager','google-cloud-bigquery'
    ],
    classifiers=[  
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',
)


