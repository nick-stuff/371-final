import pandas as pd
import json
import dash
import dash_core_components as dcc
import plotly.express as px
import dash_html_components as html
from dash import callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_table
from flask import Flask, session

#deals with data operations
class Model:
    # user authentication 
    def __init__(self, data):
        self.data = data
        self.users = {'nick': 'password', 'diego': 'password', 'nemo': 'password', 'ambarish': 'password', 'max': 'password', 'youry': 'password'}
        
    #returns selected stock and date text from csv
    def filterData(self, val, date):
        return(data[data['Stock'].isin(val) & data['Date'].isin(date)])
    
    #helps export csv
    def exportHref(self, filtered):
        return(f'data:text/csv;charset=utf-8,{filtered.to_csv(index=False)}')
    
    #returns data from selected options
    def getData(self):
        return self.data
    
    #checks user and password
    def checkUser(self,username,password):
        try:
            #if users username == password return true
            if self.users[username] == password:
                #print('true!')
                return True
            return False
        #exception error catches user does not exist
        except KeyError:
            return False

#returns front end "view" how it looks   
class View:
    #shows everything related to dashboard
    #refactor?
    def getAuthLayout(self):
        #html div
        layout = html.Div([
            #html h1
            html.H1("Dashboard"),
            #html button
            html.Button("Create New Dashboard", id="new-dashboard", n_clicks=0),
            dcc.Tabs(id='new-dashboard-output', children=[]),
        ])
        #returns layout of auth page
        return layout
    #returns information related to login username password button etc..
    def getLoginLayout(self):
        #html div, header, input, button, div
        layout = html.Div([
            html.H1("Login"),
            dcc.Input(id='username-input', type='text', placeholder='Enter username'),
            dcc.Input(id='password-input', type='password', placeholder='Enter password'),
            html.Button('Login', id='login-button', n_clicks=0),
            html.Div(id='output-message')
        ])
        #returns layout of login page
        return layout
    
    #generating main content on dashboard
    #stock drop down date drop down type table graphs export button
    def createTab(self, clicks, tabID, data):
        
        content = dcc.Tab(label=f'Dashboard {clicks}', value=tabID, children = [
                #html div
                html.Div(id=tabID, children=[
                    #html label
                    html.Label("Select Stock:"),
                    dcc.Dropdown(
                        #html dropdown
                        id={'type': 'stock-filter', 'tab_id': tabID},
                        options=[{'label': stock, 'value': stock} for stock in data['Stock'].unique()],
                        multi=True,
                        value=[]
                    ),
                    #html label
                    html.Label("Select Date:"),
                    #html dropdown
                    dcc.Dropdown(
                        id={'type': 'date-filter', 'tab_id': tabID},
                        options=[{'label': date, 'value': date} for date in data['Date'].unique()],
                        multi=True,
                        value=[]
                    ),
                    #html graph
                    dcc.Graph(id = {'type': 'revenue-filter', 'tab_id': tabID}),
                    html.A("Export Data as CSV", id= {'type': 'export-link', 'tab_id': tabID}, download="exported_data.csv", href="", target="_blank"),
                    html.Div(id={'type': 'table-container', 'tab_id': tabID})
                ])
            ])
        return(content)
    #returning bar chart of data
    def getFig(self, filtered):
        fig = px.bar(
            filtered.groupby(['Stock', 'Date']).sum().reset_index(),
            x='Stock', y='Revenue', color='Date',
            labels={'Revenue': 'Total Revenue'},
            title='Total Revenue by Stock and Date'
        )
        return(fig)
    #returning table with columns as name of the columns of csv
    def getTable(self, filtered, tabledata):
        table = dash_table.DataTable(
            columns=[{'name': column, 'id': column} for column in filtered.columns],
            data=tabledata,
            style_table={'height': '300px', 'overflowY': 'auto'},
            page_size=10
        )
        return(table)

#class controller generates all the views and draws on the model for what the user sees
#has access to model and view
class Controller:

    def __init__(self, app, model, view):
        #all instances of model view app and all instance variables
        self.app = app
        self.model = model
        self.view = view
        self.clicks = 0
        self.setup = True
        self.dashlayout =self.view.getAuthLayout()

        self.app.layout = html.Div(id='page-content', children = self.view.getLoginLayout())

        self.setupAuthenticate()
        self.setupDashboard()

    #setup callbacks for login page      
    def setupAuthenticate(self):
        @self.app.callback(
        [Output('page-content', 'children')],
        [Input('login-button', 'n_clicks')],
        [State('username-input', 'value'),
         State('password-input', 'value')])
        
        def authenticate(n_clicks, username, password):
            if n_clicks is None:
                return [self.view.getLoginLayout()]
            if self.model.checkUser(username,password):
                return [self.view.getAuthLayout()]
            else:
                return [self.view.getLoginLayout()]
   
    #setup callbacks for dashboard
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
        #call backs for 
        #stock drop down date drop down type table graphs export button and link to export for that specific tab
        def makeVisualTable(Stocks, Dates, tabs):
 
            if Stocks is None or tabs is None:
                return dash.no_update
 
            tables = []
            figs = []
            links = []
            #its going thru each tab and for each tab its generating the correct figure link table to be displayed
            #and each one the is a change regenerates 
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

#Driver code
if __name__ == '__main__':
    data = pd.read_csv('financial_data.csv')
    flask_app = Flask(__name__)
    flask_app.secret_key = 'my_secret_key'
       
    app = dash.Dash(__name__, server = flask_app)
  
    model = Model(data)
    view = View()
    controller = Controller(app, model, view)

    app.run_server(debug=True, host='0.0.0.0', port=8050)