# -*- coding: utf-8 -*-
import pandas as pd
import os


def get_pandas_dataframe_base(path_file_base):
    df = pd.read_csv(path_file_base, sep=';', encoding='utf8')
    return df


def main():
    base_file_name = 'precos_seagri_base.csv'
    path_file_base = os.path.join('bases', base_file_name)
    df = get_pandas_dataframe_base(path_file_base)
    
    df = df.loc[(df['no_produto'] == "Cacau (até 15:30h)") & (df['no_praca'] == "ILHEUS")]

    df.set_index('dt_referencia', inplace=True)
    
    new_columns = {
        'Cacau (até 15:30h)': 'Cacau Ilheus'
    }

    df = df.rename(columns=new_columns)

    drop_columns = {
        'no_praca',
        'no_tipo',
        'no_unidade',
        'no_produto'
    }

    df = df.drop(columns=drop_columns)
    
    df = df.dropna()

    # insere demais colunas
    df['MM15d'] = df['vr_real'].rolling(15).mean().round(2)
    df['MM30d'] = df['vr_real'].rolling(30).mean().round(2)
    df['MM60d'] = df['vr_real'].rolling(60).mean().round(2)

    df['MM15d/MM15d(-1)'] = ((df['MM15d'] / df['MM15d'].shift(-1))-1)*100
    df['MM15d/MM15d(-1)'] = df['MM15d/MM15d(-1)'].round(2)
    
    df['MM30d/MM30d(-1)'] = ((df['MM30d'] / df['MM30d'].shift(-1))-1)*100
    df['MM30d/MM30d(-1)'] = df['MM30d/MM30d(-1)'].round(2)
   
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    path_saida = os.path.join('bases', 'precos_cacau_ilheus.xlsx')
    writer = pd.ExcelWriter(path_saida, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print("Arquivo de saída (precos_cacau_ilheus.xlsx) gravado com sucesso.")


if __name__ == '__main__':
    main()