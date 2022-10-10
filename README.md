# zumaq-partners
## Sistema de revendas parceiras da Zumaq

![Deploy workflow](https://github.com/tiagocordeiro/zumaq-partners/actions/workflows/python-app.yml/badge.svg)
[![Build Status](https://travis-ci.org/tiagocordeiro/zumaq-partners.svg?branch=master)](https://travis-ci.org/tiagocordeiro/zumaq-partners)
[![Updates](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/shield.svg)](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/)
[![Python 3](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/python-3-shield.svg)](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/)
[![codecov](https://codecov.io/gh/tiagocordeiro/zumaq-partners/branch/master/graph/badge.svg)](https://codecov.io/gh/tiagocordeiro/zumaq-partners)
[![Python 3.10.7](https://img.shields.io/badge/python-3.10.7-blue.svg)](https://www.python.org/downloads/release/python-3107/)
[![Django 4.1.2](https://img.shields.io/badge/django-4.1.2-blue.svg)](https://www.djangoproject.com/download/)
[![PyBling](https://img.shields.io/badge/bling-API-green.svg)](https://github.com/tiagocordeiro/pybling)


### Como rodar o projeto?

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Rode as migrações.

```
git clone https://github.com/tiagocordeiro/zumaq-partners.git partners
cd partners
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
```


### Populando o banco de dados

Cria grupos de usuários ['Parceiro', 'Gerente']
```
python manage.py loaddata core/fixtures/groups.json
```

Cria usuário
```
python manage.py createsuperuser --username dev --email dev@foo.bar
```

Atualiza cotações de moedas
```
python manage.py atualiza_cotacoes
```

### Testes

##### Rode os testes
```
python manage.py test -v 2
```
ou
```
coverage run manage.py test -v 2
coverage hmtl
```
para relatório de cobertura de testes.

Code style
```
pycodestyle .
flake8 .
```
