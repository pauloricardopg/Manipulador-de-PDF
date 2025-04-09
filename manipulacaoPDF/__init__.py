import os
from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = '46ca2defb01cc7f0b122f36e6ca22e7p'


enviados = os.path.join(app.root_path, 'static/pdfs_enviados')
convertidos = os.path.join(app.root_path, 'static/pdfs_convertidos')

os.makedirs(enviados, exist_ok=True)
os.makedirs(convertidos, exist_ok=True)


from manipulacaoPDF import routes