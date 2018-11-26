# zumaq-partners
## Sistema de revendas parceiras da Zumaq

[![Build Status](https://travis-ci.org/tiagocordeiro/zumaq-partners.svg?branch=master)](https://travis-ci.org/tiagocordeiro/zumaq-partners)
[![Updates](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/shield.svg)](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/)
[![Python 3](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/python-3-shield.svg)](https://pyup.io/repos/github/tiagocordeiro/zumaq-partners/)


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

### Testes

Rode os testes
```
python manage.py test -v 2
```

Code style
```
pycodestyle partners/ core/
pyflakes partners/ core/
```
