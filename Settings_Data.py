path = f'A:/Programas/Códigos VSCode/Projects/Financial_Analysis-/Consume_Data/' # Path to save the files of CVM request.
    
year = 2023 # Year of the financials that needs to scrap of CVM.
    
suffix = ['BPA','BPP','DRE','DFC_MI'] # Suffix that needs to get the informations: BPA and BPP are balance sheets(assets and liabilities), DRE is result of year and DFC_MI is cash flow with a indirect mode.
    
cnpjs = ['08.070.508/0001-78','33.453.598/0001-23','08.322.396/0001-03'] # CNPJ of counterparty.

financial_info = ['Ativo Total', 'Passivo Total', 'Patrimônio Líquido Consolidado','Caixa Líquido Atividades Operacionais'] # Financials are all the financial informations that want to scrap.     