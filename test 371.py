import pandas as pd
import json
import dash
import dash_core_components as dcc
import plotly.express as px
import dash_html_components as html
from dash import callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_table

class Model:
    def __init__(self, data):
        self.data = data

    def filterData(self, val, date):
        return(data[data['Stock'].isin(val) & data['Date'].isin(date)])
    
    def exportHref(self, filtered):
        return(f'data:text/csv;charset=utf-8,{filtered.to_csv(index=False)}')
    
    def getData(self):
        return self.data
    

class View:
    def createTab(self, clicks, tabID, data):
        content = dcc.Tab(label=f'Dashboard {clicks}', value=tabID, children = [
                html.Div(id=tabID, children=[
                    html.Label("Select Stock:"),
                    dcc.Dropdown(
                        id={'type': 'stock-filter', 'tab_id': tabID},
                        options=[{'label': stock, 'value': stock} for stock in data['Stock'].unique()],
                        multi=True,
                        value=[]
                    ),
                    html.Label("Select Date:"),
                    dcc.Dropdown(
                        id={'type': 'date-filter', 'tab_id': tabID},
                        options=[{'label': date, 'value': date} for date in data['Date'].unique()],
                        multi=True,
                        value=[]
                    ),
                    dcc.Graph(id = {'type': 'revenue-filter', 'tab_id': tabID}),
                    html.A("Export Data as CSV", id= {'type': 'export-link', 'tab_id': tabID}, download="exported_data.csv", href="", target="_blank"),
                    html.Div(id={'type': 'table-container', 'tab_id': tabID})
                ])
            ])
        return(content)
    def getFig(self, filtered):
        fig = px.bar(
            filtered.groupby(['Stock', 'Date']).sum().reset_index(),
            x='Stock', y='Revenue', color='Date',
            labels={'Revenue': 'Total Revenue'},
            title='Total Revenue by Stock and Date'
        )
        return(fig)
    def getTable(self, filtered, tabledata):
        table = dash_table.DataTable(
            columns=[{'name': column, 'id': column} for column in filtered.columns],
            data=tabledata,
            style_table={'height': '300px', 'overflowY': 'auto'},
            page_size=10
        )
        return(table)



class Controller:
    def __init__(self, app, model, view):
        self.app = app
        self.model = model
        self.view = view
        self.clicks = 0
        self.app.layout = html.Div([
            html.H1("Welcome!"),
            html.Button("Create New Dashboard", id="new-dashboard", n_clicks=0),
            dcc.Tabs(id='new-dashboard-output', children=[]),
        ])
        self.setupDashboard()
    
    def setupDashboard(self):
        @self.app.callback(
            Output('new-dashboard-output', 'children'),
            [Input('new-dashboard', "n_clicks")],
            [State('new-dashboard-output', 'children')],
        )
        def add_dashboard(nclicks, tabs):
            if nclicks > 0:
                tab_id = f'tab-{nclicks}'
                content = self.view.createTab(nclicks, tab_id, self.model.getData())
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
 
            if Stocks is None or tabs is None:
                return dash.no_update
 
            tables = []
            figs = []
            links = []

            for (i, value) in enumerate(Stocks):
                filtered_data = self.model.filterData(value, Dates[i])
                fig = self.view.getFig(filtered_data)
                figs.append(fig)
                export_href = self.model.exportHref(filtered_data)
                links.append(export_href)
                table_data = filtered_data.to_dict('records')
                table = self.view.getTable(filtered_data, table_data)
                tables.append(html.Div(table))
            
            return tables,figs,links







    

if __name__ == '__main__':
    data = pd.read_csv('financial_data.csv')
    app = dash.Dash(__name__)
    model = Model(data)
    view = View()
    controller = Controller(app, model, view)
    app.run_server(debug=True, host='0.0.0.0', port=8050)
