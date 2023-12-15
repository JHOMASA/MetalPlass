import pandas as pd
import requests
import numpy as np
import dash
from dash import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash_table.Format import Format 
import dash_bootstrap_components as dbc

# Function to fetch exchange rate
def get_exchange_rate(from_currency="USD", to_currency="PEN"):
    api_key = "0c00579d0429fa2941633032280cfda245e31825"
    url = "https://api.getgeoapi.com/v2/currency/convert"
    params = {
        "api_key": api_key,
        "from": from_currency,
        "to": to_currency,
        "amount": 10,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        rates = data.get('rates', {})
        exchange_rate = rates.get(to_currency, {}).get('rate')

        if exchange_rate is not None:
            return float(exchange_rate)
        else:
            print(f"Exchange rate not found for {from_currency} to {to_currency} in the API response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch exchange rate. {e}")
        return None
    except ValueError as ve:
        print(f"Error parsing JSON response. {ve}")
        return None

# Sample data (replace this with your actual data)
data = {
    "Gastos fijo Mensual": ["Experiam (Central de Riesgo)", "Alquiler de Local Industrial y Administrativo", "Utiles de Aseo Personal Administ y Almacen", "Gastos de Representación_Ventas", "Combustible Despachos _Ventas", "Movilidades Personal", "Telefonos Fijo", "Lineas y equipos Moviles", "Utiles de Oficina Admint, Ventas y Almacen", "Seguros, Vida, Familiar", "Mantenimiento de Sistemas Starsoft", "Fibra de Internet dedicada Empresarial", "Poliza Seguro Todo Riesgo_Camioneta BMW"],
    "Amount (S/)": [265.80, 1000.00, 500.00, 2000.00, 2500.00, 1000.00, 0.00, 1560.00, 500.00, 1687.00, 0.00, 785.88, 0.00],
    "Monto Fijo Mensual ($)": ["#¡VALOR!"] * 13,
    "Enero": ["#¡VALOR!"] * 13,
    "Febrero": ["#¡VALOR!"] * 13,
    "Marzo": ["#¡VALOR!"] * 13,
    "Abril": ["#¡VALOR!"] * 13,
    "Mayo": ["#¡VALOR!"] * 13,
    "Junio": ["#¡VALOR!"] * 13,
    "Julio": ["#¡VALOR!"] * 13,
    "Agosto": ["#¡VALOR!"] * 13,
    "Setiembre": ["#¡VALOR!"] * 13,
    "Octubre": ["#¡VALOR!"] * 13,
    "Noviembre": ["#¡VALOR!"] * 13,
    "Diciembre": ["#¡VALOR!"] * 13,
    "TOTAL": ["#¡VALOR!"] * 13,
}

data1 = {
    "Gastos variables Mensual": [
        "Pago Energia Electrica Local Administrativo",
        "Planilla de Remuneraciones (Sueldos y RxH)",
        "Gastos de Peajes_PEX",
        "Gastos de Combustible_Despachos Vtas",
        "Costos y Gastos Financieros",
        np.nan
    ],
    "Expense Detail": ["SOLES"] * 6,
    "Enero": [101.40, 373.50, 30601.63, 429.41,5800.00, np.nan],
    "Febrero": [148.50, 527.50, 32538.20, 892.36,5800.00, np.nan],
    "Marzo": [125.00, 709.50, 31485.11, 618.56,5800.00, np.nan],
    "Abril": [148.40, 701.50, 31995.10, 562.32, 5800.00,np.nan],
    "Mayo": [125.00, 474.00, 31378.52, 998.12, 5800.00,np.nan],
    "Junio": [219.00, 309.00, 31485.22,948.91, 5800.00,np.nan],
    "Julio": [230.70, 298.50, 31780.88, 670.72, 5800.00,np.nan],
    "Agosto": [418.90, 314.50, 33128.73,583.41, 5800.00,np.nan],
    "Setiembre": [124.00, 341.50,33548.82,238.99, 5800.00,np.nan],
    "Octubre": [np.nan] * 6,
    "Noviembre": [np.nan] * 6,
    "Diciembre": [np.nan] * 6,
}

df = pd.DataFrame(data)
df1 = pd.DataFrame(data1)

# Replace placeholder values with NaN in both DataFrames
df.replace('#¡VALOR!', np.nan, inplace=True)
df1.replace('#¡VALOR!', np.nan, inplace=True)

usd_to_pen_rate = get_exchange_rate()
pen_to_usd_rate = get_exchange_rate(from_currency="PEN", to_currency="USD")

if usd_to_pen_rate is None:
    print("Exchange rate not available. Please try again later.")
else:
    # Convert from Soles to dollars
    numeric_cols = df1.select_dtypes(include=[np.number]).columns
    df1[numeric_cols] = df1[numeric_cols].div(pen_to_usd_rate, axis=0).where(df1[numeric_cols].notna(),
                                                                             df1[numeric_cols])

    # Convert Amount (S/) to dollars using exchange rate and handle NaN
    if usd_to_pen_rate:
        df["Monto Fijo Mensual ($)"] = df["Amount (S/)"] / usd_to_pen_rate
        df[df.columns[3:15]] = df["Monto Fijo Mensual ($)"].apply(lambda x: [x] * 12).to_list()
    
    if usd_to_pen_rate:
        for month in df1.columns[2:14]:  # Adjust the range based on your actual data
            df1[f"{month}_DOLARES"] = df1[month] / usd_to_pen_rate


    # Calculate the TOTAL column by summing values from Enero to Diciembre
    df["TOTAL"] = df[df.columns[3:15]].sum(axis=1)

    # Initialize the Dash app
    app = dash.Dash(__name__)
    server = app.server
    app.layout = html.Div([
     html.H1("Finance Dashboard", style={'color': 'white'}),
     html.Div([
        html.H2("Gastos Fijos Mensuales", style={'color': 'white'}),
        html.P("GASTOS FIJOS MONETARIO", style={'color': 'white'}),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id='gastos-fijos-table',
                    columns=[{'name': col, 'id': col} for col in df.columns],
                    data=df.to_dict('records'),
                    style_table={'overflowX': 'auto', 'margin-bottom': '20px'},
                    style_header={"backgroundColor": "#1f2536", "padding": "0px, 5px", 'color': 'white'},
                    style_data_conditional=[
                        {
                            'if': {'column_id': col},
                            "backgroundColor": "#242a3b",
                            "color": "#d0ef84",
                            'textAlign': 'right'
                        }
                        for col in df.columns
                    ],
                ),
                width=12  # Full width on all screens
            ),     
        ]),
        html.Div([
            html.H2("Gastos Variables Mensuales", style ={'color': 'white'}),
            html.P("GASTOS VARIABLES MONETARIO", style = {'color': 'white'}),
            dbc.Row([
                dbc.Col(
                    dash_table.DataTable(
                        id='gastos-variables-table',
                        columns=[
                            {'name': col, 'id': col, 'format': Format(nully='--')}
                            for col in df1.columns
                        ],
                        data=df1.to_dict('records'),
                        style_table = {'overflowX': 'auto', 'margin-bottom': '20px'},
                        style_data_conditional = [
                            {
                                'if': {'column_id': col},
                                "backgroundColor": "#242a3b", 
                                "color": "#d0ef84",
                                'textAlign': 'right'
                             }
                            for col in df1.columns
                        ] ,
                        style_header = {"backgroundColor": "#1f2536", "padding": "0px, 5px", 'color': 'white'}
            ),
            width = 12 
            ),
            ]),
        ]),
        html.Div([
            html.Label("Month", style={'color': 'white', 'margin-bottom': '10px'}),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} for month in df1.columns[2:]],
                value=df1.columns[2],
                style={'width': '70%', 'color': '#000000', 'margin-bottom': '10px', 'margin-right': '2%'}
             ),

            html.Label("Gastos Variables", style={'color': 'white', 'margin-bottom': '10px'}),
            dcc.Dropdown(
                id='gastos-variable-dropdown',
                options=[{'label': gasto, 'value': gasto} for gasto in df1['Gastos variables Mensual'].dropna().unique()],
                value=df1['Gastos variables Mensual'].dropna().unique()[0],
                style={'width': '70%', 'margin-bottom': '40px'}
         ),
         ], style={'display': 'inline-block', 'width': '45%', 'margin-left': '5%', 'vertical-align': 'top'}),

         dcc.Graph(id='bar-chart', style={'width': '40%', 'margin': 'auto'}),
      ], style = {'backgroundColor': '#1f2536'})  
])
def round_values_for_table(df):
    return df.round(2).astype(str)
@app.callback(
    Output('gastos-variables-table', 'data'),
    [Input('month-dropdown', 'value'), Input('gastos-variable-dropdown', 'value')]
)
def update_gastos_variables_table(selected_month, selected_gasto_variable):
    if selected_month in df1.columns:
        dollars_column = f'{selected_month}_DOLARES'
        if dollars_column in df1.columns:
            filtered_df1 = df1[df1['Gastos variables Mensual'] == selected_gasto_variable]

            if not filtered_df1.empty:
                return round_values_for_table(filtered_df1).to_dict('records')

    return []

# Callback to update Gastos Fijos table
@app.callback(
    Output('gastos-fijos-table', 'data'),
    [Input('month-dropdown', 'value')]
)
def update_gastos_fijos_table(selected_month):
    if selected_month in df.columns:
        return round_values_for_table(df).to_dict('records')

    return []

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('month-dropdown', 'value'), Input('gastos-variable-dropdown', 'value')]
)
def update_bar_chart(selected_month, selected_gasto_variable):
    if selected_month in df1.columns:
        dollars_column = f'{selected_month}_DOLARES'
        if dollars_column in df1.columns:
            filtered_df1 = df1[df1['Gastos variables Mensual'] == selected_gasto_variable]

            if not filtered_df1.empty:
                fig = go.Figure()

                # Add a trace for the selected month
                fig.add_trace(
                    go.Bar(x=filtered_df1['Gastos variables Mensual'],
                           y=filtered_df1[selected_month],
                           text = filtered_df1[selected_month].round(2).astype(str) + ' Soles',
                           name=f'Amount in Soles ({selected_month})',
                           marker_color='#79d1c3',
                           textposition = 'auto',
                           width = 0.2,
                           offset = -0.1
                           )
                )
                fig.add_trace(
                    go.Bar(x=filtered_df1['Gastos variables Mensual'],
                           y=filtered_df1[dollars_column],
                           text= filtered_df1[dollars_column].round(2).astype(str) + ' Dollars',
                           name=f'Amount in Dollars ({selected_month})',
                           marker_color='#10316b',
                           textposition = 'auto',
                           width = 0.2,
                           offset = 0.1)
                )
                
                # Customize the layout if needed
                fig.update_layout(
                    xaxis_title='Gastos variables Mensual',
                    yaxis_title='Amount (in Currency)',
                    barmode='group',
                    bargap = 0.8,
                    width = 900,
                    height = 400,
                    margin=dict(t=0, b=0, l=50,r = 50, autoexpand=True)
                )   
                fig.update_layout(margin= dict(t=0, b=0, l=50, r=100, autoexpand= True))
                return fig

    return go.Figure()
        
if __name__ == '__main__':
    app.run_server(debug=True, port= 8051)