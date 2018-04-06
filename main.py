# -*- coding: utf-8 -*-
from requests_html import HTMLSession
import os
import csv
import datetime
from bs4 import BeautifulSoup


def get_ultima_pagina(ultima_data_base):
    url = 'http://www.seagri.ba.gov.br/cotacao'
    session = HTMLSession()
    today = datetime.date.today()
    params = {
        'page': '1',
        'produto' : '',
        'praca': '',
        'tipo': '',
        'data_inicio': ultima_data_base.strftime('%d/%m/%Y'),
        'data_final': today.strftime('%d/%m/%Y'),
        'sort':'asc',
        'order':'Data'
    }

    response = session.get(url, params=params)
    if (response.status_code != 200):
        print('erro no acesso a página: ', url, params)
        get_ultima_pagina(ultima_data_base)
    
    last_page_link = response.html.find('.pager-last > a:nth-child(1)', first=True)
    element = last_page_link.html.split('=')
    return int(element[3].split('&')[0])


def get_data_from_site(paginas, ultima_data_base, ultima_pagina):
    url = 'http://www.seagri.ba.gov.br/cotacao'
    session = HTMLSession()
    today = datetime.date.today()

    for page in paginas:
        print('extraindo dados - ', 'página', str(page).zfill(4), 'de', str(ultima_pagina).zfill(4))

        params = {
            'page': str(page),
            'produto' : '',
            'praca': '',
            'tipo': '',
            'data_inicio': ultima_data_base.strftime('%d/%m/%Y'),
            'data_final': today.strftime('%d/%m/%Y'),
            'sort':'asc',
            'order':'Data'
        }
        
        response = session.get(url, params=params)
        if (response.status_code != 200):
            print('erro no acesso a página: ', url, params)
            get_data_from_site([page], ultima_data_base, ultima_pagina)
            continue

        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.select_one("table.cotacoes")
        
        rows = []
        for row in table.find_all("tr")[1:]:
            td1, td2, td3, td4, td5, td6 = row.find_all("td")
            preco = td6.text.replace('R$ ', '').replace('.', '').replace(',', '.').replace('sem cotação', '')
            data_referencia = datetime.datetime.strptime(td1.text, '%d/%m/%Y').date()
            
            # pula valores em dólar, visto que não será importado
            if 'US$' in preco:
                continue

            if preco is '':
                preco = None

            # só insere datas que ainda não estão na base
            if ultima_data_base > data_referencia:
                continue

            row = {
                'dt_referencia': data_referencia,
                'no_produto': td2.text,
                'no_praca': td3.text,
                'no_tipo': td4.text,
                'no_unidade': td5.text,
                'vr_real': preco
            }
            rows.append(row)
    
        # agora que tem os dados da tabela completa, inclui no arquivo csv
        path_file_base = os.path.join('bases', 'precos_seagri_base.csv')
        for row in rows:
            # faz o append no csv da base
            with open(path_file_base, 'a', newline='', encoding='utf8') as baseFile:
                fieldnames = ['dt_referencia', 'no_produto', 'no_praca', 'no_tipo', 'no_unidade', 'vr_real']
                writer = csv.DictWriter(baseFile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(row)
    return True


def get_ultima_data_disponivel_base(path_file_base):
    with open(path_file_base, 'r', encoding='utf8') as f:
        for row in reversed(list(csv.reader(f))):
            data = row[0].split(';')[0]
            if data in ['Data', 'dt_referencia']:
                return None
            return datetime.datetime.strptime(data[0:10], '%Y-%m-%d').date()


def main():
    name_base_file = 'precos_seagri_base.csv'
    path_file_base = os.path.join('bases', name_base_file)
    ultima_data_base = get_ultima_data_disponivel_base(path_file_base)
    print('última data base:', ultima_data_base)

    start_date = ultima_data_base + datetime.timedelta(days=1)
    ultima_pagina = get_ultima_pagina(start_date)
    paginas = list(range(1, ultima_pagina, 1))
    get_data_from_site(paginas, start_date, ultima_pagina)


if __name__ == '__main__':
    main()