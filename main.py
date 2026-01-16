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
    @st.cache_data
    def df():
        df = pd.read_excel('Mapeamento - Processo de Importação.xls', engine='xlrd')
        return df
    df = df()

    df['Data Pagto OC'] = pd.to_datetime(df['Data Pagto OC'], errors='coerce')

    filtro_ano = st.selectbox('Selecione o ano', df['Data Pagto OC'].dropna().dt.year.unique())
    filtro_empresa = st.selectbox('Selecione a empresa', df['Empresa'].unique())

    def formatar_valor(valor):
        t= "R$ {:,.2f}".format(valor).replace(',','_').replace('.',',')
        return t.replace('_','.')
    
    st.write('# DASHBOARD IMPORTAÇÃO')
    with st.container():
        col1, col2 = st.columns([1,1])
        with col1:
            
            # Máscara alinhada ao df (sem usar dropna separadamente)
            mask = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)

            # Se também quiser filtrar pela empresa:
            mask = mask & (df['Empresa'] == filtro_empresa)

            total = df.loc[mask, 'Valor OC BRL'].sum()
            total_fmt = '{:_.2f}'.format(total).replace('.', ',').replace('_','.')

            st.metric('Total (BRL)', total_fmt)

        
        with col2:
            processados = len(df.loc[mask, 'Tipo'])
            st.metric('Processos', processados)



    pizza_filtro = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)
    df_filtrado_pizza = df.loc[pizza_filtro, :]
    status_imp = (
        df_filtrado_pizza
        .groupby('Status Importação', as_index=False)['Valor OC BRL']
        .sum())



    status_tipo = (df_filtrado_pizza.groupby('Tipo', as_index=False)['Valor OC BRL'].sum())
   


    status_modal = (df_filtrado_pizza.groupby('Modal', as_index=False)['Valor OC BRL'].sum())
   


    # Criar gráfico de pizza com Plotly
    pizza = px.pie(status_imp, names='Status Importação', values='Valor OC BRL', title='Status')

    pizza.update_traces(textinfo='percent+value', textposition='outside', # Exibe porcentagem e valor
                        hovertemplate='Valor: %{value}<br>Porcentagem: %{percent}')

    pizza_2 = px.pie(status_tipo, names='Tipo', values='Valor OC BRL', title='Tipo')

    pizza_2.update_traces(textinfo='percent+value',textposition='outside',  # Exibe porcentagem e valor
                         hovertemplate='Valor: %{value}<br>Porcentagem: %{percent}')

    pizza_3 = px.pie(status_modal, names='Modal', values='Valor OC BRL', title='Modal')

    
    pizza_3.update_traces(
        textinfo='percent+value',
        textposition='outside',
        # personaliza o texto fora (quebra de linha opcional)
        hovertemplate=(
            'Valor: R$ %{value:,.2f}<br>'
            'Participação: %{percent}'
        )
    )



    with st.container():
        st.write('## Spend')
        col1, col2, col3 = st.columns([3.5,3,3])
        with col1:
            st.plotly_chart(pizza)
            

        with col2:
            st.plotly_chart(pizza_2)
            

        with col3:
            st.plotly_chart(pizza_3)
            


    with st.container():
        
        filtro_forn = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)
        df_filtrado_forn = df.loc[filtro_forn, :]
            
        spend_forn = df_filtrado_forn.groupby('Fornecedor')['Valor OC BRL'].sum().reset_index()
        spend_forn = spend_forn.sort_values(by='Valor OC BRL', ascending=True)
        spend_forn['Valor Formatado'] = spend_forn['Valor OC BRL'].apply(formatar_valor)
        spend_forn["Valor_Log"] = np.log10(spend_forn["Valor OC BRL"] + 1)

        fig_spend_forn = px.bar(spend_forn, x="Valor OC BRL", y="Fornecedor", orientation='h', 
                            color='Valor_Log',
                            text='Valor Formatado',
                            title='Spend Fornecedor')
        # Esconder todo o eixo X
        fig_spend_forn.update_xaxes(visible=False)



        # Posicionar os rótulos fora das barras
        fig_spend_forn.update_traces(textposition='outside')
        #fig_spend_forn.update_layout(width=1200, height=600)
        fig_spend_forn.update_layout(height=500)  # Ajuste manual para manter os graficos na mesma linha

        fig_spend_forn.update_layout(xaxis_type='log', coloraxis_showscale=False)
        

        st.plotly_chart(fig_spend_forn, use_container_width=True)

        filtro_pais = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)
        df_filtrado_pais = df.loc[filtro_pais, :]

        spend_pais = df_filtrado_pais.groupby('Origem')['Valor OC BRL'].sum().reset_index()
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
        # Esconder todo o eixo X
        fig_spend_pais.update_xaxes(visible=False)


        st.plotly_chart(fig_spend_pais, use_container_width=True)


        filtro_bu = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)
        df_filtrado_bu = df.loc[filtro_bu, :]



        spend_bu = df_filtrado_bu.groupby('Empresa')['Valor OC BRL'].sum().reset_index()
        spend_bu = spend_bu.sort_values(by='Valor OC BRL', ascending=True)
        spend_bu['Valor Formatado bu'] = spend_bu['Valor OC BRL'].apply(formatar_valor)
        spend_bu["Valor_Log"] = np.log10(spend_bu["Valor OC BRL"] + 1)

        fig_spend_bu = px.bar(spend_bu, x="Valor OC BRL", y="Empresa", orientation='h', 
                            text='Valor Formatado bu', color='Valor_Log',
                            title='Spend BU')


        # Posicionar os rótulos fora das barras
        fig_spend_bu.update_traces(textposition='outside')


        fig_spend_bu.update_layout(xaxis_type='log', coloraxis_showscale=False)
        # Esconder todo o eixo X
        fig_spend_bu.update_xaxes(visible=False)


        st.plotly_chart(fig_spend_bu, use_container_width=True)

        filtro_des = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)
        df_filtrado_des = df.loc[filtro_des, :]
    
        spend_des = df_filtrado_des.groupby('Despachante')['Valor Prestação de Contas'].sum().reset_index()
        spend_des = spend_des.sort_values(by='Valor Prestação de Contas', ascending=True)
        spend_des['Valor Formatado des'] = spend_des['Valor Prestação de Contas'].apply(formatar_valor)
        spend_des["Valor_Log"] = np.log10(spend_des["Valor Prestação de Contas"] + 1)

        fig_spend_des = px.bar(spend_des, x="Valor Prestação de Contas", y="Despachante", orientation='h', 
                            text='Valor Formatado des',color='Valor_Log',
                            title='Spend Despachante')


        # Posicionar os rótulos fora das barras
        fig_spend_des.update_traces(textposition='outside')
        # Esconder todo o eixo X
        fig_spend_des.update_xaxes(visible=False)


        fig_spend_des.update_layout(xaxis_type='log',coloraxis_showscale=False)

        st.plotly_chart(fig_spend_des, use_container_width=True)




        mask_finan = df['Data Pagto OC'].notna() & (df['Data Pagto OC'].dt.year == filtro_ano)
        df_filtrado_finan = df.loc[mask_finan, :]

        df_filtrado_finan['Mês'] = df_filtrado_finan['Data Pagto OC'].dt.to_period('M').astype(str)

        
        # Garanta que as colunas são numéricas (evita problemas de dtype)
        cols_valor = ['Valor Total da Importação', 'Valor OC BRL']
        df_filtrado_finan[cols_valor] = df_filtrado_finan[cols_valor].apply(pd.to_numeric, errors='coerce')



        df_bar_mes = (
            df_filtrado_finan
            .groupby('Mês', as_index=False)[cols_valor]
            .sum()
        )

        df_long_mes = df_bar_mes.melt(id_vars='Mês', value_vars=cols_valor,
                                    var_name='Métrica', value_name='Valor')

        fig_mes = px.bar(
            df_long_mes,
            x='Mês',
            y='Valor',
            color='Métrica',
            barmode='stack',
            title=f'Valores Empilhados por Mês — {filtro_ano}',
            color_discrete_sequence=['#3e95cd', '#8ecae6'],
            text_auto=True 
        )
        fig_mes.update_layout(yaxis_title='Valor (BRL)', xaxis_title='Mês', legend_title='Métrica', template='plotly_white')
        fig_mes.update_yaxes(tickprefix='R$ ', separatethousands=True)


        st.plotly_chart(fig_mes, use_container_width=True)





       

        

            





    



