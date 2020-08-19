# -*- coding: utf-8 -*-



#
#   This Code been made in order to provide a tool that should help undestanding vulnerability coverage by Protection
#   It been made by Antoine Linarès:  antoine.linares@sifive.com
#



import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pa
import numpy as np
from dash_table.Format import Format, Sign
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Dash, Output, Input, State, Trigger
import plotly.graph_objects as go

#
# Loading database
#

dataset = pa.read_csv('/home/antoine/Documents/GDrive/CFI_survey/test excel/Survey_Compare_Tab-database.csv')

#
#   use Technologie name as unique key to select a row
#
Master_key_Column = 'Technology'
dataset['id'] = dataset[Master_key_Column]
dataset.set_index('id', inplace=True, drop=False)

#
#   create a header with links linking to tech paper
#
dataset['Protections'] = '['+dataset['id']+']('+dataset['reference paper']+')'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       Globals                                 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

Header_Column = 'Protections'
Hidden_Columns = ['id','reference paper',Master_key_Column,Header_Column]
Cost_input_Columns = ['Cost memory','cost in process','Cost runtime']
Total_Cost_Column = 'total cost'
Attack_List = dataset.columns[2:22]


#
#   this dash app use BOOTSTRAP css files
#


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


#
# #     App is based on a main editable tab that is used to generate report depanding on values and user selection
#TODO check inputs and non editable columns TODO add checkbox

def generate_table():
    return html.Div([dash_table.DataTable(
        id='datatable-interactivity',
        columns=
        [{"name": i, "id": i,'type':'text', "presentation":"markdown"} for i in dataset.columns 
        if i == Header_Column] +
        [
            {"name": i, "id": i} for i in dataset.columns
            # omit the column that should be hidden
            if (not(i in Hidden_Columns)) 
        ]
        ,
        data=dataset.to_dict('records'),
        editable=True,
        filter_action="native", #TODO check if we don't just add a reset sort button and remove this 
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows= [],
        page_action="native",
        fixed_columns={'headers': True, 'data': 1},
        style_table={'minWidth': '100%'},
        css=[
            {"selector": "td.cell--selected, td.focused", "rule": 'background-color: white !important'},
            {"selector": "td.cell--selected, td.unfocused", "rule": 'background-color: white !important'},
            {"selector": ".row-1","rule": 'margin-left: 10px'},
            {"selector": ".row","rule": 'flex-wrap: nowrap'},
        ],

    )
    ,html.Div(id='datatable-container')
    ]
    )



#
# #     This dropdown is used to have a better view of selected techs
#

def dropdown():
    return html.Div([
    dcc.Dropdown(
        id='dropdown-selector',
        options= [{'label':i,'value':i} for i in dataset['id']],
        multi=True,
        placeholder="Select one or more protection technology ...",
    ),
    ])


#
# #     This alert is used to display if input are weird
# FIXME use toast instead

def alerter():
    return html.Div([
        dbc.Alert(
           "Input in attack coverage should be or 0 or 1",
            id="alert-input",
            is_open=False,
            duration=20000,
            color="danger",
            dismissable=True,
        ),
    ])

#
# #     This tab should contain selected protection attributes 
#

def selection_attributes():
    return html.Div([
        dash_table.DataTable(
            id="select-attribute",
            style_cell={'textAlign': 'center'},
        )
    ])



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                      Callbacks starts here                    #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


#
# #     First callback update style of main tab depending on selection 
#

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('sync', 'data'),
    Input('uncovered-attack', 'data'),
    Input('covered-attack', 'data')
    ],
    [Trigger('datatable-interactivity', 'data'),
    ],
    group='style_maintab'
    )
def update_styles(selected_rows,uncovered_attacks,covered_attacks):
    # uncovered attack are red
    style =  [{
        'if': { 'column_id': i },
        'background_color': 'rgb(255, 200, 200)'
    } for i in uncovered_attacks]
    # covered ones are green
    style += [{
        'if': { 'column_id': i },
        'background_color': 'rgb(200, 255, 200)'
    } for i in covered_attacks] 
    # selected rows are blue
    if not (selected_rows is None):
         style += [{ 
            'if': {
                    'filter_query': '{{id}} = {}'.format('\''+i+'\''),
                },
        'background_color': 'rgb(200, 200, 255)'
        } for i in selected_rows
        ]
    style += [{
        'if': {
            'filter_query': '{{{attack}}} = NA'.format(attack = attack),
            'column_id': attack
            },
        'backgroundColor': '#B10DC9',
        'color': 'white'
    } for attack in Attack_List
    ]
    return style


#
# #     Second callback update value of main tab depending on input made by user (rise alert if value are out of scope)
#

@app.callback(
    [Output('datatable-interactivity', 'data'),Output("alert-input", "is_open"),
    ],
    [Input('datatable-interactivity', 'data_timestamp')],
    [State('datatable-interactivity', 'data'),
    ])
def update_columns(data_timestamp,data_input):
    for row in data_input:
        row[Total_Cost_Column] = sum(int(row[i]) for i in Cost_input_Columns) 
    for row in data_input:
        for attack in Attack_List:
            if not(int(row[attack]) in [0,1]):
                row[attack] = 'NA'
                return [data_input,True]
    
    return [data_input,False]




#
# #     next three callbacks are used to sync tech selected in both dropdown and main tab
# FIXME display error in debug mode but work

@app.callback(Output("sync", "data"),
    Input('dropdown-selector','value'),
    group='row_selector'
    )
def callback_dropdown(values):
    return values

@app.callback(Output("sync", "data"),
    Input('datatable-interactivity', 'selected_row_ids'),
    group='row_selector'
    )
def callback_tab(values):
    selection_subset = dataset.loc[values]
    return list(selection_subset[Master_key_Column])


@app.callback(
    [Output('dropdown-selector', 'value'),
    Output('datatable-interactivity', 'selected_rows'),
    ],
    [Input("sync", "data"),
     State('datatable-interactivity', 'selected_row_ids'),
     State('dropdown-selector','value'),
    ])   
def updateur(sync_value,selection_table,selection_dropdown):
    if selection_table is None:
        dropdown_sync_value = None
        table_synced_value_1 = [np.where(dataset.index == sync_value[i])[0][0] for i in range(len(sync_value))] if sync_value != dropdown_sync_value else dash.no_update
    else:
        selection_subset = dataset.loc[selection_table]
        dropdown_sync_value = list(selection_subset[Master_key_Column])
        table_synced_value_1 = [np.where(dataset.index == sync_value[i])[0][0] for i in range(len(sync_value))] if sync_value != dropdown_sync_value else dash.no_update
    
    if selection_dropdown is None:
        table_synced_value = None
        dropdown_sync_value_1 = sync_value if sync_value != selection_dropdown else dash.no_update
    else:
        table_synced_value =[np.where(dataset.index == selection_dropdown[i])[0][0] for i in range(len(selection_dropdown))]
        dropdown_sync_value_1 = sync_value if sync_value != selection_dropdown else dash.no_update
    
    return [dropdown_sync_value_1,table_synced_value_1]


#
# #     folowing callback may be splitted into several but the reuse of values generated in summary tab make it easier this way
#

@app.callback(
    [Output('attack-coverage-summary-tab-container', 'children'),
    Output('datatable-interactivity-pie-container', 'figure'),
    Output('uncovered-attack', 'data'),
    Output('covered-attack', 'data'),
    ],
    [Input('sync', 'data'),
    Input('datatable-interactivity', 'data')
    ])

def generate_summary(
 selected_rows, # the tech selected by both checkboxes and dropdown system
 datatab # is dataset but updated by user
                    ):
    if selected_rows is None:
        dff = dataset
    else:
        subdata = pa.DataFrame(datatab,columns=[ i for i in dataset.columns])
        subdata['id'] = subdata[Master_key_Column]
        subdata.set_index('id', inplace=True, drop=False)
        dff = subdata.loc[selected_rows]

    accucoverage= pa.DataFrame({
        "Attacks":Attack_List,
        "Selection accumulated Coverage": list(dff[column].astype('int64').max() for column in Attack_List) 
        })
    df= pa.DataFrame({
        'coverage':['vulnerability remaining','covered attacks'],
        'nb':[(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]).count()[0],(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 1]).count()[0]]#accucoverage['Attacks'].count()-sum(accucoverage['Selection accumulated Coverage']),sum(accucoverage['Selection accumulated Coverage'])]
        })

    return [
        dash_table.DataTable(
            # id='summary-coverage-tab',
            columns=[{"name": i, "id": i} for i in accucoverage.columns],
            data=accucoverage.to_dict('records'),
            style_data_conditional=[
                {
                    'if':{
                        'filter_query':'{Selection accumulated Coverage}=0',
                        'column_id': 'Selection accumulated Coverage'
                    },
                    'color': 'tomato',
                    'fontWeight': 'bold'
                },
                {
                    'if':{
                        'filter_query':'{Selection accumulated Coverage}=1',
                        'column_id': 'Selection accumulated Coverage'
                    },
                    'color': 'green',
                    'fontWeight': 'bold'
                },
            ],
            style_cell={'textAlign': 'center'},
            include_headers_on_copy_paste=True,
        ),       
        px.pie(df, values='nb', names='coverage',color='coverage',color_discrete_map={'vulnerability remaining':'tomato','covered attacks':'lightgreen'}),
        list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]['Attacks']),
        list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 1]['Attacks']),
        ]

#
# #     folowing callback should display properties of the system made by selected elements
#
@app.callback(
    [Output('select-attribute', 'data'),
    Output('select-attribute', 'columns'),
    # Output('uncovered-attack', 'data'),
    # Output('covered-attack', 'data'),
    ],
    [Input('sync', 'data'),
    Input('datatable-interactivity', 'data')
    ])
def propertify(selection,mega_tab):
    if selection is None:
        data = []
    else :
        subdata = pa.DataFrame(mega_tab,columns=[ i for i in dataset.columns])
        data = [{
            "Protection Selected": i,
            "Cost": subdata[subdata[Master_key_Column]== i][Total_Cost_Column]
        } for i in selection]
    columns = [{"name": i, "id": i} for i in ['Protection Selected','Cost']]
    return [data,columns]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                      Display is here                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #   



app.layout = dbc.Container(
    [
        html.H1(children='Fancy Title',style={'textAlign': 'center'}),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([ 
                    dbc.CardHeader('Protection Technology survey datas:'),
                    html.Div(alerter()),
                    html.Div(generate_table()),
                    
                ],
                # body=True,
                ),
                html.Div(dropdown(),style={'padding': 10}),
            ],md=8
            ),
            dbc.Card([ 
                dbc.CardHeader('Selection summary:'),
                dbc.Col([
                    # dbc.Card([ 
                        html.Div(id='attack-coverage-summary-tab-container',style={'padding': 15}),

                    dbc.Row(dcc.Graph(id='datatable-interactivity-pie-container'))
                    #  ],
                    #  body=True,
                    #  ),
                ],),
            ],
            
            ),
        ]),
        dbc.Row( [
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Sytem generated have properties:'),
                    dbc.CardBody([
                    html.Div(selection_attributes()),
                    ])
                ]),
            ],md=2
            ),
            # dbc.Col(dcc.Graph(id='datatable-interactivity-pie-container')),
            # dbc.Col(dropdown())
        ],#style={'padding': 15}#,md=3
        ),
        dcc.Store(id="sync"),
        dcc.Store(id="uncovered-attack"),
        dcc.Store(id="covered-attack"),
        #TODO generate report
        #generate best solution
    ],
    fluid=True,
)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                      App start here                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == '__main__':
    app.run_server(debug=True)