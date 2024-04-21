import sys
sys.path.append('A:\\Programas\\Códigos VSCode\\Projects\\Financial_Analysis\\src')
from Financials_Indicators import *
import streamlit as st

#st.write('Hello World!')
#st.header('My first app in Streamlit!')
financials = Financials_Indicators()

default_name = ['PETROLEO BRASILEIRO S.A. PETROBRAS']
default_cnpj = ['33.000.167/0001-01']
default_start_date = pd.to_datetime('01-01-2023',format='%d-%m-%Y')
default_end_date = pd.to_datetime('01-03-2024',format='%d-%m-%Y')
options_names = financials.get_list_names()


if "names_list" not in st.session_state:
    st.session_state["names_list"] = default_name

if 'cnpjs_list' not in st.session_state:
    st.session_state['cnpjs_list'] = default_cnpj

if 'start_date' or 'end_date' not in st.session_state:
    st.session_state['start_date'] = default_start_date
    st.session_state['end_date'] = default_end_date

with st.container():

    def update():

        st.session_state.names_list = st.session_state.temp_names_list
        st.session_state.cnpjs_list = financials.get_cpnj_by_name(sorted(st.session_state.names_list))
        st.session_state.cnpjs_list = [value for value in st.session_state.cnpjs_list if not len(str(value).split()) == 0 and value is not None and value != 0]
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        if len(st.session_state.cnpjs_list) == 0:
            st.session_state.cnpjs_list = default_cnpj
        fig = financials.get_shares_graph(st.session_state.cnpjs_list,st.session_state.start_date,st.session_state.end_date,type_share=['Ordinary Shares'])
        st.plotly_chart(fig,use_container_width=True)
    
    st.session_state.temp_names_list = st.session_state.names_list

    start_date = pd.to_datetime(st.date_input('Start Date',default_start_date,on_change=update))
    end_date = pd.to_datetime(st.date_input('End Date',default_end_date,on_change=update))
    if st.session_state.start_date != start_date or st.session_state.end_date != end_date:
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date

    names_list = st.multiselect("Select the company",options = options_names,key= "temp_names_list" ,default = default_name, on_change=update)

#Next Steps
#st.title('Financials Analysis')
#st.write('This is a simple app that can show you the financials of some companies in Brazil.')
#st.write('You can select the company and the financials that you want to see.')
#st.write('The informations are from the CVM (Comissão de Valores Mobiliários) that is the Brazilian SEC.')

