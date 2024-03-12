from CVM_Info import CVM_Data
from Settings_Data import *
from openpyxl import Workbook, load_workbook
import warnings
from datetime import date,datetime

class Credit_Model_Fill:
    
    def __init__(self,year:int,path:str,suffix:list,cnpjs:list,financial_info_credit_model:list) -> None:
        self.year = year
        self.path = path
        self.suffix = suffix
        self.cnpjs = cnpjs
        self.financial_info_credit_model = financial_info_credit_model
        self.cvm_data = CVM_Data(self.year,self.path)
        warnings.simplefilter(action='ignore', category=UserWarning) # Removing the UserWarning from openpyxl due to Data Validation in excel file.
        
        
    def get_financials(self) -> pd.DataFrame: 

        df_financials = self.cvm_data.get_financials_information(self.financial_info_credit_model,self.cnpjs,self.suffix) # Dataframe that return
        self.df_financials_raw = df_financials

        return df_financials
    
    def get_filter_financials(self) -> pd.DataFrame:

        df_financials_raw = self.get_financials()

        min_end_date = pd.to_datetime(f'{self.year}-12-31')

        df_financials_filtered = df_financials_raw.loc[df_financials_raw['End_Date'] >= min_end_date]
        self.df_financials_filtered = df_financials_filtered
        self.min_end_date = min_end_date

        return df_financials_filtered
    
    def get_outdated_companies(self) -> list:

        if 'self.df_financials_raw' and 'self.min_end_date' not in globals():
            self.get_filter_financials()

        outdated_names = list(self.df_financials_raw.loc[self.df_financials_raw['End_Date'] < self.min_end_date].index.values)
        self.outdated_names = outdated_names

        return outdated_names
    
    def get_avaliable_cias(self) -> list: 

        names_cias = self.cvm_data.get_counterparty_names(self.cnpjs,self.suffix)
        updated_names = list(set(names_cias).symmetric_difference(set(self.get_outdated_companies())))
        self.updated_names = updated_names

        return updated_names

    def get_output_path(self,name:str) -> list: 

        today = date.today().strftime("%Y%b%d")

        path_output_credit_file = f"{self.path}{name} - CSR & Rating - {self.year} - {today}.xlsm"

        self.output_path = path_output_credit_file
            
        return path_output_credit_file
   
    def get_wb(self,std_credit_file_name:str = '0 - CSR & Rating.xlsm') -> object:
                
        path_input_credit_file = f"{self.path}{std_credit_file_name}"
        wb = load_workbook(path_input_credit_file, keep_vba=True)
        self.wb = wb
        
        return wb 
    
    def get_excel_workbook(self) -> object:
        
        wb = self.get_wb()
        credit_sheet = wb['SACP']
        self.credit_sheet = credit_sheet
        
        return credit_sheet
    
    def set_unit_adjustments(self,name:str) -> None: 

        # Removing the data validation from the cell
        equivalences_unit = {"unidade": 10**6,"mil": 10**3, "milhão": 10**0, "bilhão": 10**-3}

        credit_sheet = self.credit_sheet
        df_financials = self.df_financials_filtered

        units = df_financials['Unit'].str.lower()
        units['GERDAU S.A.'] = "dolar | milhão" 
        
        for key, value in equivalences_unit.items():
            if key in units[name]:
                credit_sheet["B4"] = key
                credit_sheet["B5"] = value                  
                    
        if "real" in units[name]:
            credit_sheet["C4"] = "BRL"
            credit_sheet["C5"] = 1

        else:
            credit_sheet["C4"] = "Not BRL"
            credit_sheet["C5"] = float(input("Please, inform the FX: "))
            credit_sheet["E5"] = credit_sheet["C5"].value

        credit_sheet["D5"] = credit_sheet["B5"].value * credit_sheet["C5"].value


    def save_credit_file(self,output_path:str) -> None:

        self.wb.save(output_path)

    
    def set_financials_correspondes(self)-> dict:

        financiasl_correspondence = {"Ativo Circulante": "C22", "Ativo Não Circulante":"C23","Caixa e Equivalentes de Caixa": "C32","Estoques": "C31","Imobilizado": "C29",
                             "Intangível":"C26","Goodwill":"C27", "Passivo Circulante":"C36","Passivo Não Circulante":"C37","Dividendos e JCP a Pagar":"C28",
                             "Patrimônio Líquido Consolidado": "C40","Capital Social Realizado":"C43", "Caixa Líquido Atividades Operacionais":"C19",
                             "Depreciação e amortização":"C9", "Imposto de Renda e Contribuição Social sobre o Lucro":"C17","Resultado Financeiro":"C14",
                             "Despesas Financeiras":"C13","Receitas Financeiras":"C12","Resultado Antes do Resultado Financeiro e dos Tributos":"C8", "Lucro/Prejuízo Consolidado do Período":"C18"}
        
        return financiasl_correspondence

    def fill_credit_file(self) -> None:
    
        df_financials = self.get_filter_financials()
        name_cias = self.get_avaliable_cias()
        outdated_names = self.get_outdated_companies()
        financiasl_correspondence = self.set_financials_correspondes()

        exceptions = ["Despesas Financeiras","Imposto de Renda e Contribuição Social sobre o Lucro"]

        for name in name_cias:
            credit_sheet = self.get_excel_workbook()

            output_path = self.get_output_path(name)
            self.set_unit_adjustments(name)

            for key, value in financiasl_correspondence.items():
                credit_sheet[value] = df_financials.loc[name,key]
                if key in exceptions:
                    credit_sheet[value] = credit_sheet[value].value * -1

            self.save_credit_file(output_path)

        if len(outdated_names) == 0:
            print("The credit file was updated successfully with all companies.")

        else:
            print(f"The companies {outdated_names} are outdated, the credit assessment of these companies has not been completed.")

if __name__ == "__main__":

    credit_model = Credit_Model_Fill(year,path,suffix,cnpjs,financial_info_credit_model)
    fill_data = credit_model.fill_credit_file()