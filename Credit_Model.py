from CVM_Info import CVM_Data
from Settings_Data import *
from openpyxl import Workbook, load_workbook
import warnings
from datetime import date

class Credit_Model_Fill:
    
    def __init__(self,year:int,path:str,suffix:list,cnpjs:list,financial_info_credit_model:list) -> None:
        self.year = year
        self.path = path
        self.suffix = suffix
        self.cnpjs = cnpjs
        self.financial_info_credit_model = financial_info_credit_model
        warnings.simplefilter(action='ignore', category=UserWarning) # Removing the UserWarning from openpyxl due to Data Validation in excel file.
        

    def get_financials(self) -> pd.DataFrame:

        cvm_data = CVM_Data(self.year,self.path)
        df_financials = cvm_data.get_financials_information(self.financial_info_credit_model,self.cnpjs,self.suffix) # Dataframe that return

        self.df_financials = df_financials

        return df_financials
    
    def get_wb(self) -> object:
                
        std_credit_file_name = '0 - CSR & Rating.xlsm'
        path_input_credit_file = f"{self.path}{std_credit_file_name}"
        wb = load_workbook(path_input_credit_file, keep_vba=True)
        self.wb = wb

        return wb
    
    def get_excel_workbook(self) -> object:

        credit_sheet = self.wb['SACP']
        self.credit_sheet = credit_sheet

        return credit_sheet
    
    def get_output_path(self) -> list:

        cvm_data = CVM_Data(self.year,self.path)
        names_cias = cvm_data.get_counterparty_names(self.cnpjs,self.suffix)
        today = date.today().strftime("%Y%b%d")

        path_output_credit_file = []
        for name in names_cias:
            path_output_credit_file.append(f"{self.path}{name} - CSR & Rating - {self.year} - {today}.xlsm")

        self.output_path = path_output_credit_file
        self.names_cias = names_cias

        return path_output_credit_file
    
    def set_unit_adjustments(self) -> None:

        # Removing the data validation from the cell
        equivalences_unit = {"unidade": 10**6,"mil": 10**3, "milhão": 10**0, "bilhão": 10**-3}

        credit_sheet = self.credit_sheet
        df_financials = self.df_financials

        units = df_financials['Unit'].unique()[0].lower()
        for key, value in equivalences_unit.items():
            if key in units:
                credit_sheet["B4"] = key
                credit_sheet["B5"] = value
        if "real" in units:
            credit_sheet["C4"] = "BRL"
            credit_sheet["C5"] = 1
        else:
            credit_sheet["C4"] = "Not BRL"
            credit_sheet["C5"] = input("Please, inform the FX: ")
            credit_sheet["E5"] = credit_sheet["C5"]

        credit_sheet["D5"] = credit_sheet["B5"].value * credit_sheet["C5"].value


    def save_credit_file(self, iterator) -> None:

        #output_path = self.get_output_path()
        self.wb.save(self.output_path[iterator])

    
    def set_financials_correspondes(self)-> dict:

        financiasl_correspondence = {"Ativo Circulante": "C22", "Ativo Não Circulante":"C23","Caixa e Equivalentes de Caixa": "C32","Estoques": "C31","Imobilizado": "C29",
                             "Intangível":"C26","Goodwill":"C27", "Passivo Circulante":"C36","Passivo Não Circulante":"C37","Dividendos e JCP a Pagar":"C28",
                             "Patrimônio Líquido Consolidado": "C40","Capital Social Realizado":"C43", "Caixa Líquido Atividades Operacionais":"C19",
                             "Depreciação e amortização":"C9", "Imposto de Renda e Contribuição Social sobre o Lucro":"C17","Resultado Financeiro":"C14",
                             "Despesas Financeiras":"C13","Receitas Financeiras":"C12","Resultado Antes do Resultado Financeiro e dos Tributos":"C8", "Lucro/Prejuízo Consolidado do Período":"C18"}
        
        return financiasl_correspondence


    def fill_credit_file(self) -> None:

        df_financials = self.get_financials()
        self.get_wb()
        credit_sheet = self.get_excel_workbook()
        self.set_unit_adjustments()
        financiasl_correspondence = self.set_financials_correspondes()
        self.output_path = self.get_output_path()


        exceptions = ["Despesas Financeiras","Imposto de Renda e Contribuição Social sobre o Lucro"]
        
        iterator = -1
        for name in self.names_cias:
            iterator += 1
            for key, value in financiasl_correspondence.items():
                credit_sheet[value] = df_financials.loc[name,key]
                if key in exceptions:
                    credit_sheet[value] = credit_sheet[value].value * -1

            self.save_credit_file(iterator)

if __name__ == "__main__":

    credit_model = Credit_Model_Fill(year,path,suffix,cnpjs,financial_info_credit_model)
    credit_fill = credit_model.fill_credit_file()
