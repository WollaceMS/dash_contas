import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib
import numpy as np
import streamlit_authenticator as stauth 
from login import valida_senha

st.set_page_config(layout="wide") #deixar tela grande do streamlit
#controlador de paginas
if 'page' not in st.session_state:
    st.session_state.page ='Welcome'

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ''

if not st.session_state.logged_in:
    if st.session_state.page == 'Welcome':
        st.title('Tela de Login')

        with st.form('login_form'):
            st.subheader('Insira suas credenciais')
            username = st.text_input('Usuário')
            password = st.text_input('Senha', type='password')
            submit = st.form_submit_button('Entrar')

    if submit:
        if valida_senha(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page ='form'
            st.rerun()
        else:
            st.error('Usuário e/ou senha incoretos')

elif st.session_state.page =='form' and st.session_state.logged_in:
    
    df = pd.read_excel('Mapeamento - Processo de Importação.xls', engine='xlrd')

    st.write('# DASHBOARD IMPORTAÇÃO 2025')
    with st.container():
        col1, col2 = st.columns([1,1])
        with col1:
            total = df['Valor OC BRL'].sum()
            total = '{:_.2f}'.format(total).replace('.', ',').replace('_','.')
            st.metric('Total', f'R${total}')
        
        with col2:
            processados = len(df['Tipo'])
            st.metric('Processos', processados)
    status_imp = df['Status Importação'].value_counts().reset_index()
    status_imp.columns = ['Status Importação', 'Quantidade Status']


    status_tipo = df['Tipo'].value_counts().reset_index()
    status_tipo.columns = ['Tipo', 'Quantidade Tipo']


    status_modal = df['Modal'].value_counts().reset_index()
    status_modal.columns = ['Modal', 'Quantidade Modal']


    # Criar gráfico de pizza com Plotly
    pizza = px.pie(status_imp, names='Status Importação', values='Quantidade Status', title='Spend por Status')

    pizza.update_traces(textinfo='percent+value',  # Exibe porcentagem e valor
                        hovertemplate='Valor: %{value}<br>Porcentagem: %{percent}')

    pizza_2 = px.pie(status_tipo, names='Tipo', values='Quantidade Tipo', title='Spend por Tipo')

    pizza_2.update_traces(textinfo='percent+value',  # Exibe porcentagem e valor
                        hovertemplate='Valor: %{value}<br>Porcentagem: %{percent}')

    pizza_3 = px.pie(status_modal, names='Modal', values='Quantidade Modal', title='Spend por Modal')

    pizza_3.update_traces(textinfo='percent+value',  # Exibe porcentagem e valor
                        hovertemplate='Valor: %{value}<br>Porcentagem: %{percent}')


    with st.container():
        st.write('## Spend')
        col1, col2, col3 = st.columns([3.5,3,3])
        with col1:
            st.plotly_chart(pizza)
            

        with col2:
            st.plotly_chart(pizza_2)
            

        with col3:
            st.plotly_chart(pizza_3)
            



    def formatar_valor(valor):
        t= "R$ {:,.2f}".format(valor).replace(',','_').replace('.',',')
        return t.replace('_','.')
        

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            spend_forn = df.groupby('Fornecedor')['Valor OC BRL'].sum().reset_index()
            spend_forn = spend_forn.sort_values(by='Valor OC BRL', ascending=True)
            spend_forn['Valor Formatado'] = spend_forn['Valor OC BRL'].apply(formatar_valor)
            spend_forn["Valor_Log"] = np.log10(spend_forn["Valor OC BRL"] + 1)

            fig_spend_forn = px.bar(spend_forn, x="Valor OC BRL", y="Fornecedor", orientation='h', 
                                color='Valor_Log',
                                text='Valor Formatado',
                                title='Spend Fornecedor')


            # Posicionar os rótulos fora das barras
            fig_spend_forn.update_traces(textposition='outside')
            #fig_spend_forn.update_layout(width=1200, height=600)
            fig_spend_forn.update_layout(height=500)  # Ajuste manual para manter os graficos na mesma linha

            fig_spend_forn.update_layout(xaxis_type='log', coloraxis_showscale=False)
            

            st.plotly_chart(fig_spend_forn, use_container_width=True)


        with col2:
            spend_pais = df.groupby('Origem')['Valor OC BRL'].sum().reset_index()
            spend_pais = spend_pais.sort_values(by='Valor OC BRL', ascending=True)

            spend_pais['Valor pais'] = spend_pais['Valor OC BRL'].apply(formatar_valor)
            spend_pais["Valor_Log"] = np.log10(spend_pais["Valor OC BRL"] + 1)

            fig_spend_pais = px.bar(spend_pais, x="Valor OC BRL", y="Origem", orientation='h', 
                                color='Valor_Log',
                                text='Valor pais',
                                title='Spend por País')


            # Posicionar os rótulos fora das barras
            fig_spend_pais.update_traces(textposition='outside')
            #fig_spend_pais.update_layout(width=1200, height=600)
            fig_spend_pais.update_layout(height=500)  # Ajuste manual


            fig_spend_pais.update_layout(xaxis_type='log', coloraxis_showscale=False)

            st.plotly_chart(fig_spend_pais, use_container_width=True)

            
        with col1:
            spend_bu = df.groupby('Empresa')['Valor OC BRL'].sum().reset_index()
            spend_bu = spend_bu.sort_values(by='Valor OC BRL', ascending=True)
            spend_bu['Valor Formatado bu'] = spend_bu['Valor OC BRL'].apply(formatar_valor)
            spend_bu["Valor_Log"] = np.log10(spend_bu["Valor OC BRL"] + 1)

            fig_spend_bu = px.bar(spend_bu, x="Valor OC BRL", y="Empresa", orientation='h', 
                                text='Valor Formatado bu', color='Valor_Log',
                                title='Spend BU')


            # Posicionar os rótulos fora das barras
            fig_spend_bu.update_traces(textposition='outside')


            fig_spend_bu.update_layout(xaxis_type='log', coloraxis_showscale=False)

            st.plotly_chart(fig_spend_bu, use_container_width=True)


        with col2:
            spend_des = df.groupby('Despachante')['Valor Prestação de Contas'].sum().reset_index()
            spend_des = spend_des.sort_values(by='Valor Prestação de Contas', ascending=True)
            spend_des['Valor Formatado des'] = spend_des['Valor Prestação de Contas'].apply(formatar_valor)
            spend_des["Valor_Log"] = np.log10(spend_des["Valor Prestação de Contas"] + 1)

            fig_spend_des = px.bar(spend_des, x="Valor Prestação de Contas", y="Despachante", orientation='h', 
                                text='Valor Formatado des',color='Valor_Log',
                                title='Spend Despachante')


            # Posicionar os rótulos fora das barras
            fig_spend_des.update_traces(textposition='outside')

            fig_spend_des.update_layout(xaxis_type='log',coloraxis_showscale=False)

            st.plotly_chart(fig_spend_des, use_container_width=True)



        df['Saldo a Receber/Devolver'] = df['Saldo a Receber/Devolver'].abs()

        # Converter colunas para datetime, ignorando erros
        df['Data Pagto OC'] = pd.to_datetime(df['Data Pagto OC'], errors='coerce')
        df['Data Pagto Numerário'] = pd.to_datetime(df['Data Pagto Numerário'], errors='coerce')
        df['Data Pagto Saldo'] = pd.to_datetime(df['Data Pagto Saldo'], errors='coerce')
            

        df['Mes_oc'] = df['Data Pagto OC'].dt.to_period('M').dt.to_timestamp()
        df['Mes_num'] = df['Data Pagto Numerário'].dt.to_period('M').dt.to_timestamp()
        df['Mes_saldo'] = df['Data Pagto Saldo'].dt.to_period('M').dt.to_timestamp()




        oc = df.groupby('Mes_oc')['Valor OC BRL'].sum().reset_index()
        numerario = df.groupby('Mes_num')['Valor Numerário'].sum().reset_index()
        saldo = df.groupby('Mes_saldo')['Saldo a Receber/Devolver'].sum().reset_index()

        
        # Renomear colunas para unificar
        oc.columns = ['Mes', 'Valor']
        oc['Tipo'] = 'OC'

        numerario.columns = ['Mes', 'Valor']
        numerario['Tipo'] = 'Numerário'

        saldo.columns = ['Mes', 'Valor']
        saldo['Tipo'] = 'Saldo'

        # Concatenar tudo
        df_final = pd.concat([oc, numerario, saldo])

        df_total = df_final.groupby('Mes')['Valor'].sum().reset_index()
        
        # Converter para string no formato mês/ano
        df_total['Mes'] = df_total['Mes'].dt.strftime('%b/%Y')
        df_total['Valor_f'] = df_total['Valor'].apply(formatar_valor)

        # Criar gráfico com Plotly
        fig = px.bar(df_total, x='Mes', y='Valor',
                    title='Financeiro Pagamentos',
                    labels={'Mes': 'Mês', 'Valor': 'Valor Total'}, text= 'Valor_f'
                    )  
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig)

            





    



