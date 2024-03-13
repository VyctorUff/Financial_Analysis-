from Settings_Data import *
from CVM_Info import CVM_Data


class Financials_Indicators(CVM_Data):

    def __init__(self) -> None:
        super().__init__(year,path)

    def teste(self):
        print(self.path)




    def CAGR(self,begin:float,end:float,period:int) -> float:
        return (end/begin)**(1/period)-1
    








if __name__ == '__main__':
    a = Financials_Indicators()
    df = a.get_financials_information(financial_info,cnpjs,suffix)
    print(df)