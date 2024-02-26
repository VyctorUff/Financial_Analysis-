import pandas as pd
import requests
import zipfile
import os


path = f'A:/Programas/Códigos VSCode/Projects/Financial_Analysis-/Consume_Data/' # Path to save the files of CVM request.
    
year = 2023 # Year of the financials that needs to scrap of CVM.
    
suffix = ['BPA','BPP','DRE','DFC_MI'] # Suffix that needs to get the informations: BPA and BPP are balance sheets(assets and liabilities), DRE is result of year and DFC_MI is cash flow with a indirect mode.
    
cnpjs = ['08.070.508/0001-78','33.453.598/0001-23','08.322.396/0001-03'] # CNPJ of counterparty.

financial_info = ["Ativo Total","Ativo Circulante", "Ativo Não Circulante","Caixa e Equivalentes de Caixa","Estoques","Imobilizado","Intangível","Goodwill",
                "Passivo Circulante","Passivo Não Circulante","Dividendos e JCP a Pagar","Patrimônio Líquido Consolidado","Capital Social Realizado",
                "Caixa Líquido Atividades Operacionais","Depreciação e amortização",
                "Imposto de Renda e Contribuição Social sobre o Lucro","Despesas Financeiras","Receitas Financeiras","Resultado Antes do Resultado Financeiro e dos Tributos"] # Financial_info are all the financial informations that want to scrap.     

financial_info_credit_model = ["Ativo Total","Ativo Circulante", "Ativo Não Circulante","Caixa e Equivalentes de Caixa","Estoques","Imobilizado","Intangível","Goodwill",
                "Passivo Circulante","Passivo Não Circulante","Dividendos e JCP a Pagar","Patrimônio Líquido Consolidado","Capital Social Realizado",
                "Caixa Líquido Atividades Operacionais","Depreciação e amortização",
                "Imposto de Renda e Contribuição Social sobre o Lucro","Despesas Financeiras","Receitas Financeiras", "Resultado Financeiro",
                "Resultado Antes do Resultado Financeiro e dos Tributos","Lucro/Prejuízo Consolidado do Período","Variações cambiais, líquidas", "Efeito líquido dos derivativos"] # Financial_info will be used in credit model.
