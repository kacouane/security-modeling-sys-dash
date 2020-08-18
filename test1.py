# -*- coding: utf-8 -*-
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
#dataset

dataset = pa.read_csv('/home/antoine/Documents/GDrive/CFI_survey/test excel/Survey_Compare_Tab-database.csv')

dataset['id'] = dataset['Technology']
dataset.set_index('id', inplace=True, drop=False)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


#generate table 

#TODO make it cute and dropdown filter? or extern ?
# @app.callback(
#     [Output('datatable-container', 'children'),
#     ],
#     [Trigger("dropdown-selector", "value"),
#     ],
#     )
def generate_table():
    max_rows=50
    return html.Div([dash_table.DataTable(
    # return dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i} for i in dataset.columns
            # omit the id column
            if i != 'id'
        ],
        data=dataset.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows= [],
        page_action="native",
        # page_current= 0,
        # page_size= max_rows,
        # striped=True,
        # style_as_list_view=True,
        # style_cell={
        #     'whiteSpace': 'normal',
        #     'height': 'auto',
        # },

        fixed_columns={'headers': True, 'data': 1},style_table={'minWidth': '100%'},
        css=[
            # {"selector": ".dash-spreadsheet-container table", "rule": '--text-color: green !important'},
            {"selector": "td.cell--selected, td.focused", "rule": 'background-color: white !important'},
            {"selector": "td.cell--selected, td.unfocused", "rule": 'background-color: white !important'},
            {"selector": ".row-1","rule": 'margin-left: 10px'},
            {"selector": ".row","rule": 'flex-wrap: nowrap'},
        ],

        # style_table={'overflowX': 'auto',},
    )
    ,html.Div(id='datatable-container')
    ]#,style={'padding':25}
    )


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
    style =  [{
        'if': { 'column_id': i },
        'background_color': 'rgb(255, 200, 200)'
    } for i in uncovered_attacks]
    style += [{
        'if': { 'column_id': i },
        'background_color': 'rgb(200, 255, 200)'
    } for i in covered_attacks] 
    if not (selected_rows is None):
         style += [{ 
            'if': {
                    'filter_query': '{{Technology}} = {}'.format('\''+i+'\''),
                },
        'background_color': 'rgb(200, 200, 255)'
        } for i in selected_rows
        ]  
    return style


@app.callback(
    Output('datatable-interactivity', 'data'),
    [Input('datatable-interactivity', 'data_timestamp')],
    [State('datatable-interactivity', 'data'),
    ],
    # [Trigger('datatable-interactivity', 'data'),
    # ],
)
def update_computed_columns(data_timestamp,data_input):
    for row in data_input:
        row['total cost'] = int(row['Cost memory']) + int(row['cost in process'])+ int(row['Cost runtime'])
        # print(row['Technology'],row['total cost'])
    return data_input



def dropdown():
    return html.Div([
    dcc.Dropdown(
        id='dropdown-selector',
        options= [{'label':i,'value':i} for i in dataset['Technology']],
        multi=True,
        placeholder="Select one or more protection technology ...",
        # value=['NX bit']
    ),
    


    # html.Label('Text Input'),
    # dcc.Input(value='MTL', type='text'),

    # html.Label('Slider'),
    # dcc.Slider(
    #     min=0,
    #     max=9,
    #     marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
    #     value=5,
    # )
],style={'padding': 10})


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
    return list(selection_subset['Technology'])


@app.callback(
    [ Output('dropdown-selector', 'value'),
    Output('datatable-interactivity', 'selected_rows'),
    ],
    [Input("sync", "data"),
     State('datatable-interactivity', 'selected_row_ids'),
     State('dropdown-selector','value'),
    ])   
def updateur(sync_value,selection_table,selection_dropdown):

    if selection_table is None:
        dropdown_sync_value = None
        # print("dropdown:",dropdown_sync_value,sync_value)
        table_synced_value_1 = [np.where(dataset.index == sync_value[i])[0][0] for i in range(len(sync_value))] if sync_value != dropdown_sync_value else dash.no_update
    else:
        selection_subset = dataset.loc[selection_table]
        dropdown_sync_value = list(selection_subset['Technology'])
        # print("dropdown:",dropdown_sync_value,sync_value)
        table_synced_value_1 = [np.where(dataset.index == sync_value[i])[0][0] for i in range(len(sync_value))] if sync_value != dropdown_sync_value else dash.no_update
    if selection_dropdown is None:
        table_synced_value = None
        # print("table:",selection_dropdown,sync_value)
        dropdown_sync_value_1 = sync_value if sync_value != selection_dropdown else dash.no_update
    else:
        table_synced_value =[np.where(dataset.index == selection_dropdown[i])[0][0] for i in range(len(selection_dropdown))]
        # print("table:",selection_dropdown,sync_value)
        dropdown_sync_value_1 = sync_value if sync_value != selection_dropdown else dash.no_update
    # print("output:",dropdown_sync_value_1,table_synced_value_1)
    return [dropdown_sync_value_1,
    table_synced_value_1
    ]


@app.callback(
    [
    Output('attack-coverage-summary-tab-container', 'children'),
    Output('datatable-interactivity-pie-container', 'figure'),
    Output('uncovered-attack', 'data'),
    Output('covered-attack', 'data'),
    ],
    [
    Input('sync', 'data'),
    Input('datatable-interactivity', 'data')
    ],
    # [Trigger("dropdown-selector", "value"),
    # ],
     )

def generate_summary(#row_ids,
 selected_rows,
 datatab 
#  active_cell 
):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=dataset.to_rows('dict')` when you initialize
    # the component.
    
    if selected_rows is None:
        dff = dataset
        # print("something happened")
    else:
        subdata = pa.DataFrame(datatab,columns=[ i for i in dataset.columns])
        subdata['id'] = subdata['Technology']
        subdata.set_index('id', inplace=True, drop=False)
        # print(dataset.loc[dataset.index[selected_rows]])
        # dff = dataset.loc[dataset.index[selected_rows]]
        dff = subdata.loc[selected_rows]
    # active_row_id = active_cell['row_id'] if active_cell else None
    # active_row = dataset.loc[active_row_id] if active_cell else None

   
    accucoverage= pa.DataFrame({
        "Attacks":dataset.columns[2:22],
        "Selection accumulated Coverage": list(dff[column].astype('int64').max() for column in dataset.columns[2:22]) #list(max(dff[column].max(),active_row[column]) for column in dataset.columns[2:22])  if active_cell else 
        })
    # print('\n\n',list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]['Attacks']),'\n',list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 1]['Attacks']))
    df= pa.DataFrame({
        'coverage':['vulnerability remaining','covered attacks'],
        'nb':[(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]).count()[0],(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 1]).count()[0]]#accucoverage['Attacks'].count()-sum(accucoverage['Selection accumulated Coverage']),sum(accucoverage['Selection accumulated Coverage'])]
        })
    #labels =['covered attacks','vulnerability remaining']
    #values = list(accucoverage['Selection accumulated Coverage'].value_counts(bins=[0,1]))
    # print(list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]['Attacks']))
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

    
#here is the display
app.layout = dbc.Container(
    [
        html.H1(children='Fancy Title',style={'textAlign': 'center'}),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([ 
                    dbc.CardHeader('Protection Technology survey datas:'),
                    html.Div(generate_table()),
                    
                ],
                # body=True,
                ),
                html.Div(dropdown()),
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
            
            # dbc.Col(dcc.Graph(id='datatable-interactivity-pie-container')),
            # dbc.Col(dropdown())
        ]),
        dcc.Store(id="sync"),
        dcc.Store(id="uncovered-attack"),
        dcc.Store(id="covered-attack"),
        #dropdown()
        #TODO generate report
        #generate best solution
    ],
    fluid=True,
)

if __name__ == '__main__':
    app.run_server(debug=True)