from Settings_Data import *

pd.options.display.float_format = '{:.2f}'.format

class CVM_Data:


    def __init__(self,year:str,path:str) -> None:
        
        self.year = str(year)
        self.path = path


    def download_data(self, autoclean:bool = True) -> str:

        full_file_name_zip = f'{self.path}dfp_cia_aberta_{self.year}.zip'
        path_to_item = os.path.join(full_file_name_zip)
        clean_path = path_to_item.replace('.zip', '')
        self.folder_path = clean_path
        check_raw = self.check_raw_data()

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
    
    def check_raw_data(self) -> bool:

        if os.path.exists(self.folder_path):
            return True
        else:
            return False

    
    def delete_folder(self,list_not_used_files:list, clear:bool = True) -> bool:

        folder_path = self.folder_path 
        for files in list_not_used_files:
            path_to_file = os.path.join(folder_path,files)
            if os.path.exists(path_to_file):
                os.remove(path_to_file)

        if len(os.listdir(folder_path)) > 0 and clear:
            shutil.rmtree(folder_path)
            return True
        
        return False
    

    def get_financial_info(self,suffix:str) -> pd.DataFrame:

        folder_path = self.download_data()
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
    
    def get_counterparty_names(self,cnpj,suffix_list) -> list:

        df_filtered = self.get_counterparty_info(cnpj,suffix_list)
        names_cias = df_filtered['DENOM_CIA'].unique()

        self.counterparties = names_cias
        
        return names_cias
    
    def get_financials_information(self,financial_info:list,cnpj:list,suffix_list:list) -> pd.DataFrame:
        
        df_filtered = self.get_counterparty_info(cnpj,suffix_list)
        counterparties = self.get_counterparty_names(cnpj,suffix_list)

        list_of_financials = {}

        for name in counterparties:
            info_dict = {}
            unit = df_filtered.query(f"DENOM_CIA == '{name}'")['MOEDA'].str.cat(df_filtered.query(f"DENOM_CIA == '{name}'")['ESCALA_MOEDA'],sep=" | ")
            info_dict['Unit'] = "Null" if unit.empty else unit.values[-1]
            end_date = df_filtered.query(f"DENOM_CIA == '{name}'")['DT_FIM_EXERC']
            info_dict['End_Date'] = 0 if end_date.empty else pd.to_datetime(end_date.values[-1])

            for info in financial_info:                
                cp_info = df_filtered.query(f"DENOM_CIA == '{name}' & DS_CONTA == '{info}' ")['VL_CONTA']
                info_dict[info] = 0 if cp_info.empty else cp_info.values[-1]

            list_of_financials[name] = info_dict

        financial_information = (pd.DataFrame(list_of_financials)).T
        final_date = pd.to_datetime(financial_information['End_Date'])
        financial_unit = financial_information['Unit'].astype('str')
        financials = financial_information.iloc[:,2:].astype('float32')
        financial_information = pd.concat([financials,final_date,financial_unit],axis=1)

        file_not_used = list(set(self.list_used_files).symmetric_difference(set(os.listdir(self.folder_path))))  
        clear_folder = self.delete_folder(file_not_used, clear = False) #Change for False if you want to keep the folder with the csv files
        self.clear_folder = clear_folder

        return financial_information

if __name__ == "__main__":
    
    #input data from Settings_Data.py
    cvm_data = CVM_Data(year,path) # Creating a object of the class CVM_Data 
    financials_informations_counterparty = cvm_data.get_financials_information(financial_info,cnpjs,suffix) # Dataframe that return
    print(financials_informations_counterparty) # Print the dataframe