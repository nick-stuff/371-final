import pandas as pd
import json
import dash
import dash_core_components as dcc
import plotly.express as px
import dash_html_components as html
from dash import ctx
from dash import callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_table

#data = pd.read_csv('healthcare_dataset.csv')
data = pd.read_csv('financial_data.csv')

app = dash.Dash(__name__)
clicks = 0

#categories = ["Medical Condition", "Medication", "Blood Type"]

app.layout = html.Div([
    html.H1("Welcome!"),
    html.Button("Create New Dashboard", id="new-dashboard", n_clicks=0),
    dcc.Tabs(id='new-dashboard-output', children=[]),
    #html.Div(id='table-container')
])

@app.callback(
    Output('new-dashboard-output', 'children'),
    [Input('new-dashboard', "n_clicks")],
    [State('new-dashboard-output', 'children')],
    
)
def add_dashboard(nclicks, tabs):
    if nclicks > 0:
        tab_id = f'tab-{nclicks}'
       
        content = dcc.Tab(label=f'Dashboard {nclicks}', value=tab_id, children = [
                html.Div(id=tab_id, children=[
                    html.Label("Select Stock:"),
                    dcc.Dropdown(
                        id={'type': 'stock-filter', 'tab_id': tab_id},
                        options=[{'label': stock, 'value': stock} for stock in data['Stock'].unique()],
                        multi=True,
                        value=[]
                    ),
                    html.Label("Select Date:"),
                    dcc.Dropdown(
                        id={'type': 'date-filter', 'tab_id': tab_id},
                        options=[{'label': date, 'value': date} for date in data['Date'].unique()],
                        multi=True,
                        value=[]
                    ),
                    dcc.Graph(id = {'type': 'revenue-filter', 'tab_id': tab_id}),
                    html.A("Export Data as CSV", id= {'type': 'export-link', 'tab_id': tab_id}, download="exported_data.csv", href="", target="_blank"),
                    html.Div(id={'type': 'table-container', 'tab_id': tab_id})
                ])
            ])
        tabs.append(content)
        return tabs
    else:
        return [html.Div()]



@app.callback(
    [Output({'type': 'table-container', 'tab_id': ALL}, 'children'),
     Output({'type': 'revenue-filter', 'tab_id':ALL}, 'figure'),
     Output({'type': 'export-link', 'tab_id': ALL}, 'href')],
    [Input({'type': 'stock-filter', 'tab_id': ALL}, 'value'),
     Input({'type': 'date-filter', 'tab_id': ALL}, 'value')],
    [State('new-dashboard-output', 'children')]
)

def makeVisualTable(Stocks, Dates, tabs):

    print(Stocks)

    if Stocks is None or tabs is None:
        return dash.no_update
    
    ctx_msg = json.dumps({
        'states': ctx.states,
        'triggered': ctx.triggered,
        'inputs': ctx.inputs
    }, indent=2)
    
    
    #print(ctx_msg)



    
    tab_id = ctx.triggered_id

    tables = []
    figs = []
    links = []

    

    for (i, value) in enumerate(Stocks):
        filtered_data = data[data['Stock'].isin(value) & data['Date'].isin(Dates[i])]
        fig = px.bar(
            filtered_data.groupby(['Stock', 'Date']).sum().reset_index(),
            x='Stock', y='Revenue', color='Date',
            labels={'Revenue': 'Total Revenue'},
            title='Total Revenue by Stock and Date'
        )
        figs.append(fig)
        export_href = f'data:text/csv;charset=utf-8,{filtered_data.to_csv(index=False)}'
        links.append(export_href)
        table_data = filtered_data.to_dict('records')
        table = dash_table.DataTable(
            columns=[{'name': column, 'id': column} for column in filtered_data.columns],
            data=table_data,
            style_table={'height': '300px', 'overflowY': 'auto'},
            page_size=10
        )
        tables.append(html.Div(table))

    

    #for (i, value) in enumerate(Stocks):
    #    filtered_data = data[value]
        
    
    return tables,figs,links



    #return [html.Div(f"Tab {tab_id}, Dropdown {i + 1} = {value}") for (i, value) in enumerate(colsSelected)]


    

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)