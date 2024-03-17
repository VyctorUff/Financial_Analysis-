from Settings_Data import *
begin = time.time()
from CVM_Info import CVM_Data


class Financials_Indicators(CVM_Data):

    def __init__(self) -> None:
        super().__init__(year,path)


    def get_list_names(self) -> list:

        df_info_all = self.get_financial_info('BPA')
        df_cnpj_name = df_info_all[['CNPJ_CIA','DENOM_CIA']]
        self.df_cnpj_name = df_cnpj_name
        
        names = df_cnpj_name['DENOM_CIA'].unique().tolist()

        return names
    
    def get_cpnj_by_name(self,names_list:list) -> list:

        df_info_all = self.get_financial_info('BPA')
        df_cnpj_name = df_info_all[['CNPJ_CIA','DENOM_CIA']]
        cnpj_list = []
        names = [value for value in names_list if not len(str(value).split()) == 0 and value is not None and value != 0]

        for name in names:
            cnpj = df_cnpj_name.query(f"DENOM_CIA == '{name}'")['CNPJ_CIA'].unique()
            cnpj_list.append(cnpj[-1])

        return cnpj_list

    
    def get_ticker_value_history(self,cnpj:list, start_date:datetime, end_date:datetime,type_value:str = 'Adj Close') -> pd.DataFrame: # The Type_value is the type of value that wants to get from the ticker. The default is the adjusted close value. If you want get all the values, just put 'All' in the type_value.
        
        ticker_financials = self.get_ticker_name(cnpj)
        self.ticker_financials = ticker_financials

        def get_ticker_value(ticker:str) -> pd.Series:
            if not ticker is None:
                ticker = str(ticker) + '.SA'
                if type_value == 'All':
                    try:
                        return yf.download(ticker, start=start_date, end=end_date, actions = True,progress=False)
                    except Exception as e:
                        print(f'Ticker named {ticker} not found, error{e}')
                else:
                    try:
                        return yf.download(ticker, start=start_date, end=end_date, actions = True,progress=False)[type_value]
                    except Exception as e:
                        print(f'Ticker named {ticker} not found, error{e}')
            else:
                end = end_date-timedelta(days=1)
                index_date = pd.date_range(start=start_date, end=(end if end_date < datetime.now() else datetime.now()))
                return pd.Series(0,index=index_date)
            
        tickers_cp = {}
        for cp in cnpj:
            tickers_value = {}
            ord_share = ticker_financials.query(f"CNPJ == '{cp}'")['Ordinary Shares'].values[-1]
            prim_share = ticker_financials.query(f"CNPJ == '{cp}'")['Preference Shares'].values[-1]
            tickers_value['Ordinary Shares'] = get_ticker_value(ord_share)
            tickers_value['Preference Shares'] = get_ticker_value(prim_share)
            name = ticker_financials.query(f"CNPJ == '{cp}'").index.values[-1]
            tickers_cp[name] = tickers_value

        return tickers_cp
    

    def get_shares_graph(self,cnpj:str, start_date:datetime, end_date:datetime,type_value:str = 'Adj Close',type_share:list = ['Ordinary Shares'] ) -> object:

        ticker_values = self.get_ticker_value_history(cnpj,start_date,end_date,type_value)
        df = self.ticker_financials
        cp_names_list = []
        ordanary_shares = []
        preference_shares = []
        traces = []
        for cp_name,share_tp in ticker_values.items():
            cp_names_list.append(cp_name)
            for share,value in share_tp.items():
                if not (value == 0).all():
                    if share in type_share:
                        if share == 'Ordinary Shares':
                            ordanary_shares.append(value)

                        elif share == 'Preference Shares':
                            preference_shares.append(value)
                        else:
                            ordanary_shares.append(value)
                            preference_shares.append(value)
                    
                    tck = df.query(f"index == '{cp_name}'")[share].values[-1]
                    traces.append(go.Scatter( x= value.index, y= value.values, mode='lines', name=f'{cp_name.split()[0].title()}-{tck}'))
                else:
                    pass
        layout = go.Layout(title='Share Value', xaxis_title ='Date', yaxis_title ='Price (BRL)')
        fig = go.Figure(data=traces,layout=layout)
        #fig.show()

        return fig

    #def get_EBITDA
        
    def get_divideds_yield(self,cnpj:list, start_date:datetime, end_date:datetime,type_value:str = 'Dividends') -> pd.DataFrame:
        
        dividends_ticker_values = self.get_ticker_value_history(cnpj,start_date,end_date,type_value)
        df = self.ticker_financials
        dividends_yield = {}
        for cp_name,share_tp in dividends_ticker_values.items():
            dividens_payed = []
            for share,value in share_tp.items():
                if not (value == 0).all():
                    non_zero = value[value != 0].index
                    for i in non_zero:
                        dividens_payed.append(i.strftime('%Y-%m-%d'))
                        dividens_payed.append(value[i])

                    tck = df.query(f"index == '{cp_name}'")[share].values[-1]
                    dividends_yield[tck] = dividens_payed

        return dividends_yield
    
    
    def CAGR(self,begin:float,end:float,period:int) -> float:
        return (end/begin)**(1/period)-1
    

if __name__ == '__main__':

    a = Financials_Indicators()
    df_concat = a.get_ticker_value_history(cnpjs,datetime(2024,1,1),datetime(2024,3,1))
    print(df_concat)