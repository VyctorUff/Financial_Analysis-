import pandas as pd
import requests
import numpy as np
import zipfile
import os
#from bcb import sgs


pd.options.display.float_format = '{:.2f}'.format

class CVM_Data:


    def __init__(self,year:int,path:str) -> None:
        
        self.year = str(year)
        self.path = path


    def download_data(self, autoclean:bool = True) -> str:

        URL = f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{self.year}.zip'

        download = requests.get(URL)
        
        full_file_name_zip = f'{self.path}dfp_cia_aberta_{self.year}.zip'

        with open(full_file_name_zip, 'wb') as file:
    
            file.write(download.content)

        path_to_item = os.path.join(full_file_name_zip)
        clean_path = path_to_item.replace('.zip', '')
                                    
        with zipfile.ZipFile(path_to_item, 'r') as zipobj:
            zipobj.extractall(path = clean_path)
            
        if autoclean:
            # Del zip file
            os.remove(path_to_item)

        self.folder_path = clean_path

        return clean_path
    

    def get_financial_info(self,suffix:str) -> pd.DataFrame:

        folder_path = self.download_data()
        zip_file_name = f'dfp_cia_aberta_{suffix}_con_{self.year}.csv'
        path_csv = os.path.join(folder_path, zip_file_name)

        with open(path_csv,'r') as file:

            df_data = pd.read_csv(file,sep=';', encoding='ISO-8859-1')

        self.df_data = df_data

        return df_data


    def get_counterparty_info(self, cnpj:list,suffix_list:list ) -> pd.DataFrame:

        columns = ['CNPJ_CIA', 'DT_REFER', 'VERSAO', 'DENOM_CIA', 'CD_CVM', 'GRUPO_DFP', 'MOEDA', 'ESCALA_MOEDA', 
                   'ORDEM_EXERC', 'DT_FIM_EXERC', 'CD_CONTA', 'DS_CONTA', 'VL_CONTA']
        
        financials_info = pd.DataFrame(columns = columns)

        for i in suffix_list:
            financials_info = pd.merge(financials_info,self.get_financial_info(i),how="outer")

        financials_info = financials_info[columns]
        df_filtered = (financials_info.query(f"ORDEM_EXERC == 'ÚLTIMO' & CNPJ_CIA in {cnpj}")).sort_values(['DENOM_CIA'])

        names_cias = df_filtered['DENOM_CIA'].unique()

        self.counterparties = names_cias

        return df_filtered
    
    def get_financials_information(self,financial_info:list,cnpj:list,suffix_list:list) -> pd.DataFrame:
        

        df_filtered = self.get_counterparty_info(cnpj,suffix_list)

        list_of_financials = {}

        for name in self.counterparties:
            info_dict = {}
            for info in financial_info:
                cp_info = df_filtered.query(f"DENOM_CIA == '{name}' & DS_CONTA == '{info}' ")['VL_CONTA']
                info_dict[info] = cp_info.iloc[0]
            list_of_financials[name] = info_dict

        
        financial_information = (pd.DataFrame(list_of_financials)).T

        return financial_information



if __name__ == "__main__":
    
    path = f'A:/Programas/Códigos VSCode/Projects/Financial_Analysis-/Consume_Data/' # Path to save the files of CVM request.
    
    year = 2023 # Year of the financials that needs to scrap of CVM.
    
    suffix = ['BPA','BPP','DRE','DFC_MI'] # Suffix that needs to get the informations: BPA and BPP are balance sheets(assets and liabilities), DRE is result of year and DFC_MI is cash flow with a indirect mode.
    
    cnpjs = ['08.070.508/0001-78','33.453.598/0001-23','08.322.396/0001-03'] # CNPJ of counterparty.

    financial_info = ['Ativo Total', 'Passivo Total', 'Patrimônio Líquido Consolidado','Caixa Líquido Atividades Operacionais'] # Financials are all the financial informations that want to scrap. 

    cvm_data = CVM_Data(year,path) # Creating a object of the class CVM_Data 

    financials_informations_counterparty = cvm_data.get_financials_information(financial_info,cnpjs,suffix) # Dataframe that return

    print(financials_informations_counterparty)