import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from datetime import datetime
from flask import Flask


# Definir o diretório onde os arquivos .npz estão localizados
directory_path = r"C:\Users\usuario\Documents\supervisório\experimentos"


def load_data(file_path):
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        return None  # Arquivo não encontrado

    # Carregar os dados do arquivo .npz
    dados = np.load(file_path)
    df = pd.DataFrame({key: dados[key].flatten() for key in dados.files})

    # Verificar se os dados estão vazios
    if df.empty:
        return None  # Dados vazios

    return df


def determine_stable_index(dados):
    threshold = 0.01  # Variação máxima permitida para considerar estabilização
    # Máximo de iterações baseado no tempo
    max_iterations = len(dados["listatempo"])

    last_values = None
    stable_index = 0

    for contador in range(max_iterations):
        current_values = [dados[k][contador]
                          for k in dados if k != "listatempo"]
        if last_values is not None and all(abs(current_values[i] - last_values[i]) < threshold for i in range(len(current_values))):
            stable_index = contador
            break
        last_values = current_values

    # Adicionar uma margem para não ficar tão colado
    stable_index += 10  # Aumente esse valor conforme necessário

    return stable_index


def create_dash_application(flask_app):
    # Cria o aplicativo do Dash
    dash_app = dash.Dash(server=flask_app, name="Dashboard",
                         url_base_pathname="/dash/")

    # Define categorias para o menu suspenso (dropdown)
    categories = ['Pesos', 'Temperatura', 'Vazoes']

    # Define Dash layout
    dash_app.layout = html.Div(
        children=[
            html.Nav(
                className="navbar",
                children=[
                    html.Div(
                        className="logo",
                        children=[
                            html.Img(
                                src=dash_app.get_asset_url('gimscop.svg'),
                                alt="Logo"
                            )
                        ]
                    ),
                    html.Ul(
                        className="navbar-items",
                        children=[
                            html.Li(html.A('Home', href='/')),
                            html.Li(html.A('Time Real', href='/realtime')),
                            html.Li(html.A('Experimentos', href='/dash')),
                            html.Li(html.A('Sobre', href='/sobre')),
                        ]
                    )
                ]
            ),
            html.H1(children="Visualização de Dados"),
            html.Div(
                children="Selecione uma categoria e uma data para visualizar:"
            ),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': category, 'value': category}
                         for category in categories],
                value='Pesos'  # Valor padrão
            ),
            dcc.DatePickerSingle(
                id='date-picker-single',
                date=None,  # Valor inicial da data
                # Formato para exibir a data selecionada (brasileiro)
                display_format='DD/MM/YYYY',
                # Estilo opcional para o componente
                style={'display': 'inline-block'}
            ),
            html.Button('Enviar', id='submit-button', n_clicks=0),
            dcc.Graph(id="graph-output"),
        ]
    )

    @dash_app.callback(
        Output("graph-output", "figure"),
        [Input("submit-button", "n_clicks")],
        [State("date-picker-single", "date"),
         State("category-dropdown", "value")]
    )
    def update_graph(n_clicks, selected_date, category):
        if n_clicks > 0 and selected_date and category:
            # Converter selected_date para um objeto datetime
            selected_datetime = datetime.strptime(selected_date, "%Y-%m-%d")

            # Construir o nome do arquivo baseado na data selecionada
            file_name = selected_datetime.strftime("%d-%m-%y")
            file_path = os.path.join(directory_path, f"{file_name}.npz")

            # Carregar os dados com base no caminho do arquivo
            df = load_data(file_path)
            if df is None:
                return go.Figure(data=go.Scatter(), layout=go.Layout(title="Dados não disponíveis"))

            # Determinar o índice onde os dados se estabilizam
            stable_index = determine_stable_index(df.to_dict("list"))

            # Preparar o objeto de figura do Plotly
            fig = go.Figure()
            fig.update_layout(
                title=f"{category.capitalize()} vs Tempo ({
                    selected_datetime.strftime('%d-%m-%Y')})",
                xaxis_title="Tempo (min)",
                autosize=True,
                height=600,
                width=1920
            )

            # Adicionar os gráficos com base na categoria selecionada até o índice de estabilização
            for column in df.columns:
                if column == "listatempo":
                    continue  # Ignorar a coluna 'listatempo'

                if category == "Pesos" and (column.startswith("P") or column == "P0") and column != "PWM":
                    fig.add_trace(go.Scatter(
                        x=df["listatempo"][:stable_index] / 60, y=df[column][:stable_index], name=column))

                elif category == "Temperatura" and column.startswith("T"):
                    if column.endswith("_sp"):
                        fig.add_trace(go.Scatter(
                            x=df["listatempo"][:stable_index] / 60, y=df[column][:stable_index],
                            name=column, line=dict(width=2, dash='dot', color='gray')))
                    else:
                        fig.add_trace(go.Scatter(
                            x=df["listatempo"][:stable_index] / 60, y=df[column][:stable_index], name=column))

                elif category == "Vazoes" and (column == "PWM" or column == "B1" or column == "B2" or column == "B3"):
                    fig.add_trace(go.Scatter(
                        x=df["listatempo"][:stable_index] / 60, y=df[column][:stable_index], name=column))

            # Verificar se nenhum dado foi adicionado ao gráfico
            if len(fig.data) == 0:
                return go.Figure(data=go.Scatter(), layout=go.Layout(title=f"Sem dados disponíveis para '{category}'"))

            return fig

        return go.Figure(data=go.Scatter(), layout=go.Layout(title="Selecione uma data e categoria e clique em 'Enviar'"))

    return dash_app


# CSS para estilizar a navbar
external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    {
        "href": "https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap",
        "rel": "stylesheet",
    },
    "assets/style.css",  # Arquivo CSS local com estilos personalizados
]
