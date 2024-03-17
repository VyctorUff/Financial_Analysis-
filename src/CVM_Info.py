from Settings_Data import *

pd.options.display.float_format = '{:.2f}'.format

class CVM_Data:


    def __init__(self,year:str,path:str) -> None:
        
        self.year = str(year)
        self.path = path


    def download_inf_data(self, autoclean:bool = True) -> str:

        full_file_name_zip = f'{self.path}dfp_cia_aberta_{self.year}.zip'
        path_to_item = os.path.join(full_file_name_zip)
        clean_path = path_to_item.replace('.zip', '')
        self.financial_folder_path = clean_path
        check_raw = self.check_raw_data(clean_path)

        if check_raw!=True:

            URL = f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{self.year}.zip'

            download = requests.get(URL)

            with open(full_file_name_zip, 'wb') as file:
            
                file.write(download.content)

            with zipfile.ZipFile(path_to_item, 'r') as zipobj:
                zipobj.extractall(path = clean_path)

            if autoclean:
                # Delete the folder
                os.remove(path_to_item)


        return clean_path
    
    def check_raw_data(self,path:str) -> bool:

        if os.path.exists(path):
            return True
        else:
            return False

    
    def delete_folder(self,list_not_used_files:list, folder_path: str, clear:bool = True) -> bool:

        for files in list_not_used_files:
            path_to_file = os.path.join(folder_path,files)
            if os.path.exists(path_to_file):
                os.remove(path_to_file)

        if len(os.listdir(folder_path)) > 0 and clear:
            shutil.rmtree(folder_path)
            return True
        
        return False
    

    def get_financial_info(self,suffix:str) -> pd.DataFrame:

        folder_path = self.download_inf_data()
        zip_file_name = f'dfp_cia_aberta_{suffix}_con_{self.year}.csv'
        path_csv = os.path.join(folder_path, zip_file_name)

        with open(path_csv,'r') as file:

            df_data = pd.read_csv(file,sep=';', encoding='ISO-8859-1')

        self.df_data = df_data
        self.csv_names = zip_file_name

        return df_data


    def get_counterparty_info(self, cnpj:list,suffix_list:list ) -> pd.DataFrame:

        columns = ['CNPJ_CIA', 'DT_REFER', 'VERSAO', 'DENOM_CIA', 'CD_CVM', 'GRUPO_DFP', 'MOEDA', 'ESCALA_MOEDA', 
                   'ORDEM_EXERC', 'DT_FIM_EXERC', 'CD_CONTA', 'DS_CONTA', 'VL_CONTA']
        
        financials_info = pd.DataFrame(columns = columns)

        list_csv_files = []

        for i in suffix_list:
            financials_info = pd.merge(financials_info,self.get_financial_info(i),how="outer")
            list_csv_files.append(self.csv_names)

        financials_info = financials_info[columns]
        df_filtered = (financials_info.query(f"ORDEM_EXERC == 'ÚLTIMO' & CNPJ_CIA in {cnpj}")).sort_values(['DENOM_CIA'])

        self.list_used_files = list_csv_files

        return df_filtered
    
    def get_counterparty_names(self,cnpj:list,suffix_list:list) -> list:

        df_filtered = self.get_counterparty_info(cnpj,suffix_list)
        names_cias = df_filtered['DENOM_CIA'].unique()
        
        self.counterparties = names_cias
        
        return names_cias
    
    def get_name_from_cnpj(self,cnpj:list) -> pd.DataFrame:

        df_filtered = self.get_counterparty_info(cnpj,['BPA'])
        df_filtered = df_filtered[['CNPJ_CIA','DENOM_CIA']]
        name_cnpj = {}
        cnpj_filter = [value for value in cnpj if not len(str(value).split()) == 0 and value is not None and value != 0]

        if len(cnpj_filter) != 0:
            for cnpj in cnpj_filter:
                
                name = df_filtered.query(f"CNPJ_CIA == '{cnpj}'")['DENOM_CIA'].unique()
                name_cnpj[name[-1]] = cnpj

            df_name_cnpj = (pd.DataFrame([name_cnpj]).T)
            df_name_cnpj.columns = ['CNPJ']
            return df_name_cnpj
        
            
    def get_financials_information(self,financial_info:list,cnpj:list,suffix_list:list) -> pd.DataFrame:
        
        df_filtered = self.get_counterparty_info(cnpj,suffix_list)
        counterparties = self.get_counterparty_names(cnpj,suffix_list)

        list_of_financials = {}

        for name in counterparties:
            info_dict = {}
            unit = df_filtered.query(f"DENOM_CIA == '{name}'")['MOEDA'].str.cat(df_filtered.query(f"DENOM_CIA == '{name}'")['ESCALA_MOEDA'],sep=" | ")
            info_dict['Unit'] = None if unit.empty else unit.values[-1]
            end_date = df_filtered.query(f"DENOM_CIA == '{name}'")['DT_FIM_EXERC']
            info_dict['End_Date'] = None if end_date.empty else pd.to_datetime(end_date.values[-1])

            for info in financial_info:                
                cp_info = df_filtered.query(f"DENOM_CIA == '{name}' & DS_CONTA == '{info}' ")['VL_CONTA']
                info_dict[info] = 0 if cp_info.empty else cp_info.values[-1]

            list_of_financials[name] = info_dict

        financial_information = (pd.DataFrame(list_of_financials)).T
        final_date = pd.to_datetime(financial_information['End_Date'])
        financial_unit = financial_information['Unit'].astype('str')
        financials = financial_information.iloc[:,2:].astype('float32')
        financial_information = pd.concat([financials,final_date,financial_unit],axis=1)

        file_not_used = list(set(self.list_used_files).symmetric_difference(set(os.listdir(self.financial_folder_path))))  
        clear_folder = self.delete_folder(file_not_used,self.financial_folder_path, clear = False) #Change for True if you want to delete the folder with the csv files
        self.clear_folder = clear_folder

        return financial_information


    def download_ticker_name(self,autoclean:bool = True) -> pd.DataFrame:

        full_path_fica_zip = f'{self.path}fca_cia_aberta_{self.year}.zip'
        path_to_zip_fca = os.path.join(full_path_fica_zip)
        clean_path_fca = path_to_zip_fca.replace('.zip', '')
        self.fca_folder_path = clean_path_fca
        check_raw = self.check_raw_data(clean_path_fca)

        if check_raw!=True:

            URL = f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_{self.year}.zip'

            download = requests.get(URL)

            with open(full_path_fica_zip, 'wb') as file:
            
                file.write(download.content)

            with zipfile.ZipFile(path_to_zip_fca, 'r') as zipobj:
                zipobj.extractall(path = clean_path_fca)

            if autoclean:
                # Delete the folder
                os.remove(path_to_zip_fca)


        return clean_path_fca
    
    def get_ticker_info(self) -> pd.DataFrame:

        folder_path_ticker = self.download_ticker_name()
        zip_file_name_ticker = f'fca_cia_aberta_valor_mobiliario_{self.year}.csv'
        path_csv = os.path.join(folder_path_ticker, zip_file_name_ticker)
        self.zip_file_name_ticker = zip_file_name_ticker

        with open(path_csv,'r') as file:

            df_val_mob = pd.read_csv(file,sep=';', encoding='ISO-8859-1')

        return df_val_mob
    
    def get_ticker_name(self,cnpjs:list) -> pd.DataFrame:

        df_val_mob = self.get_ticker_info()
        tickers = {}
        ord_act = "Ações Ordinárias"
        pref_act = "Ações Preferenciais"
        for cnpj in cnpjs:
            tickers_list = []
            ticker_ord = df_val_mob.query(f"CNPJ_Companhia == '{cnpj}' & Valor_Mobiliario == '{ord_act}' ")['Codigo_Negociacao']
            ticker_ord_fill = None if ticker_ord.empty else ticker_ord.values[-1]
            tickers_list.append(ticker_ord_fill)
            ticker_pref = df_val_mob.query(f"CNPJ_Companhia == '{cnpj}' & Valor_Mobiliario == '{pref_act}' ")['Codigo_Negociacao']
            ticker_pref_fill = None if ticker_pref.empty else ticker_pref.values[-1]
            tickers_list.append(ticker_pref_fill)
            tickers[cnpj] = tickers_list

        ticker_info_df = (pd.DataFrame(tickers).T)
        name_cnpj = self.get_name_from_cnpj(cnpjs)

        ticker_info_df = pd.merge(ticker_info_df, name_cnpj, left_index=True, right_on='CNPJ')
        ticker_info_df.columns = ['Ordinary Shares','Preference Shares','CNPJ']
        
        #Removing the files that are not used
        full_dir = os.listdir(self.fca_folder_path)
        if self.zip_file_name_ticker in full_dir:
            full_dir.remove(self.zip_file_name_ticker)

        fca_file_not_used = full_dir
        clear_fca_folder = self.delete_folder(fca_file_not_used,self.fca_folder_path, clear = False) #Change for True if you want to delete all the folder with the csv files
        self.clear_fca_folder = clear_fca_folder



        return ticker_info_df
    
    def get_concat_cvm_data(self,financial_info:list,cnpjs:list,suffix:list) -> pd.DataFrame:

        financials = self.get_financials_information(financial_info,cnpjs,suffix)
        ticker = self.get_ticker_name(cnpjs)

        df_concat = pd.concat([financials,ticker],axis=1)
        
        return df_concat
        

if __name__ == "__main__":
    
    cvm_data = CVM_Data(year,path) # Creating a object of the class CVM_Data 
    concat_cvm_data = cvm_data.get_concat_cvm_data(financial_info,cnpjs,suffix)
    print(concat_cvm_data)