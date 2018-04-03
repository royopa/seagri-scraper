# -*- coding: utf-8 -*-
from requests_html import HTMLSession
import os
import csv
import datetime
from bs4 import BeautifulSoup


def get_data_from_site(paginas = []):
    url = 'http://www.seagri.ba.gov.br/cotacao'
    session = HTMLSession()
    today = datetime.date.today()

    for page in paginas:
        print('pagina:', page)

        params = {
            'page': str(page),
            'produto' : '',
            'praca': '',
            'tipo': '',
            'data_inicio': '01/01/2010',
            'data_final': today.strftime('%d/%m/%Y')
        }
        
        response = session.get(url, params=params)
        if (response.status_code != 200):
            print('erro no acesso a página: ', url, params)
            get_data_from_site([page])
            continue

        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.select_one("table.cotacoes")
        
        rows = []
        for row in table.find_all("tr")[1:]:
            td1, td2, td3, td4, td5, td6 = row.find_all("td")

            preco = td6.text.replace('R$ ', '').replace(',', '.').replace('sem cotação', '')
            data_referencia = datetime.datetime.strptime(td1.text, '%d/%m/%Y')
            
            if preco is '':
                preco = None

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
            with open(path_file_base, 'a', newline='') as baseFile:
                fieldnames = ['dt_referencia', 'no_produto', 'no_praca', 'no_tipo', 'no_unidade', 'vr_real']
                writer = csv.DictWriter(baseFile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(row)
                print(row)
    return True


def main():
    pagina_inicial = 3661
    paginas = list(range(pagina_inicial, 6173, 1))
    get_data_from_site(paginas)


if __name__ == '__main__':
    main()