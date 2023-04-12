import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table, State
import dash_bootstrap_components as dbc

df_data = pd.read_csv("https://github.com/datenlabor01/LS/raw/main/ls_draft.csv")
app = Dash(external_stylesheets = [dbc.themes.LUX])

#Dropdown for indicator: 
indicator_dropdown = dcc.Dropdown(options=sorted(df_data["indicator"].unique()),
                             value='HDI-Rang', style={"textAlign": "center"}, clearable=False, multi=False, placeholder='Indikator auswählen (Default: HDI-Rang)')

#Dropdown for country:
country_dropdown = dcc.Dropdown(options=sorted(df_data["Country"].unique()),
                             value='All', style={"textAlign": "center"}, clearable=True, multi=False, placeholder='Land auswählen für Einzeltabelle mit Jahresangabe des Indikators')

text2 = "Diese Anwendung wird als Prototyp vom BMZ Datenlabor angeboten. Sie kann Fehler enthalten und ist als alleinige Entscheidungsgrundlage nicht geeignet. Außerdem können Prototypen ausfallen oder kurzfristig von uns verändert werden. Sichern Sie daher wichtige Ergebnisse per Screenshot oder Export. Die Anwendung ist vorerst intern und sollte daher nicht ohne Freigabe geteilt werden. Wenden Sie sich bei Fragen gerne an datenlabor@bmz.bund.de"

app.layout = dbc.Container([
      dbc.Row([
         html.Div(html.Img(src="https://github.com/datenlabor01/LS/raw/main/logo.png", style={'height':'80%', 'width':'20%'})),
         html.H1(children='Prototyp Ländersachstand'),
         html.P(children = "Das ist ein Prototyp, der Fehler enthalten kann. Weltbank-Indikatoren werden per API für die letzten fünf Jahre abgefragt und der aktuellste Wert übernommen. Der HDI wird per csv-Datei eingelesen. Der ODA-Rang von DEU wird für 2021 nach Brutto ODA und bilaterale DAC-Geber berechnet.")],
         style={'textAlign': 'center'}),
      #App button:
      dbc.Row([
         dbc.Button(children = "Über diese App", id = "textbutton", color = "light", className = "me-1",
                    n_clicks=0, style={'textAlign': 'center', "width": "30rem"})
      ], justify = "center"),
      dbc.Row([
            dbc.Collapse(dbc.Card(dbc.CardBody([
               dbc.Badge(text2, className="text-wrap"),
               ])), id="collapse", style={'textAlign': 'center', "width": "60rem"}, is_open=False),
      ], justify = "center"),
      #Dynamic elements:
      dbc.Row([
        dbc.Col([indicator_dropdown], width = 8),
      ],justify = "center"),

      dbc.Row([
         dbc.Badge(id = "text", className="text-wrap"),
         dcc.Graph(id='map', style={'textAlign': 'center'}),
      ]),

      dbc.Row([
        dbc.Col([country_dropdown, html.Br()], width = 8),
      ],justify = "center"),

      #Data Table:
      dbc.Row([
         my_table := dash_table.DataTable(
         df_data.to_dict('records'), [{"name": i, "id": i} for i in df_data.columns],
         filter_action="native", sort_action="native", page_size= 25,
         style_cell={'textAlign': 'left', "whiteSpace": "normal", "height": "auto"},
         style_header={'backgroundColor': 'rgb(11, 148, 153)', 'color': 'black', 'fontWeight': 'bold'},
             style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(235, 240, 240)',
        }], export_format= "xlsx"),
         ]),
])

#Button to display text:
@app.callback(
    Output("collapse", "is_open"),
    [Input("textbutton", "n_clicks")],
    [State("collapse", "is_open")],
)

def collapse(n, is_open):
   if n:
      return not is_open
   return is_open

@app.callback(
    [Output('map', 'figure'), Output(my_table, "data"), Output(my_table, "columns")],
    [Input(indicator_dropdown, 'value'), Input(country_dropdown, 'value')]
)

def update_map(selected_indicator, selected_country):

   if (selected_indicator == "HDI-Rang") | (selected_indicator == []):
      dat_fil = df_data[df_data["indicator"] == "HDI_Rank"]
   else:
      dat_fil = df_data[df_data["indicator"] == selected_indicator]

   if (selected_country == "All") | (selected_country == None):
      dat_table = df_data.pivot_table(index='Country', columns='indicator', values='Value').reset_index()
   else:
      dat_table = df_data[df_data["Country"] == selected_country]
      dat_table = dat_table.pivot_table(index='Country', columns=['indicator', "last_year"], values='Value').reset_index()
      dat_table.columns = dat_table.columns.map(('{0[0]} {0[1]}'.format))
   
   if dat_fil.empty == False:
      figMap = px.choropleth(dat_fil, locations = "economy", locationmode="ISO-3", hover_data= ["Country", "last_year"],
                             color_continuous_scale="Fall", color="Value", range_color=(min(dat_fil["Value"]), max(dat_fil["Value"])))

   return figMap, dat_table.to_dict("records"), [{"name": i, "id": i} for i in dat_table.columns]

if __name__ == '__main__':
    app.run_server(debug=True)