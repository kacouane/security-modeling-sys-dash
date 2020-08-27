# -*- coding: utf-8 -*-



#
#   This Code been made in order to provide a tool that should help understanding vulnerability coverage by Protection
#   It been made by Antoine Linarès:  antoine.linares@sifive.com
#



import dash
from dash.dependencies import Input, Output
import scipy as sp
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pa
import numpy as np
from dash_table.Format import Format
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Dash, Output, Input, State, Trigger
import dash_daq as daq

#
# Loading database
#
DATABASE_PATH='./.ressources/'
protection_properties = pa.read_csv(DATABASE_PATH+'Survey_Compare_Tab - export_tech_properties.csv')
attack_properties = pa.read_csv(DATABASE_PATH+'Survey_Compare_Tab - export_attack_properties.csv')
fuzzybests = pa.read_csv(DATABASE_PATH+'fuzzy_bests.csv') 

#formating database
fuzzybests = fuzzybests.drop(columns=['Unnamed: 0'])
fuzzybests['source']='fuzzing'
fuzzybests['size'] = 1 #TODO size depend on coverage ponderated ?

#
#   use Technologie name as unique key to select a row for the tech property tab
#
Master_key_Column = 'Technology'
protection_properties['id'] = protection_properties[Master_key_Column]
protection_properties.set_index('id', inplace=True, drop=False)

#
#   create a header with links linking to tech paper
#
protection_properties['Protections'] = '['+protection_properties['id']+']('+protection_properties['reference paper']+')'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       Globals                                 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

Header_Column = 'Protections'
Hidden_Columns = ['id','reference paper',Master_key_Column,Header_Column]
Cost_input_Columns = ['Cost memory','cost in process','Cost runtime']
Total_Cost_Column = 'total cost'
Attack_List = list(attack_properties['Attack'])
nb_of_data_to_display =2000
Protection_list = list(protection_properties[Master_key_Column])



#
# #   this dash app use BOOTSTRAP css files
#
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])




#
# #     the following functions are used for dynamic update of fields
#


def return_coverage(selection,database):
    subdata = pa.DataFrame(database,columns=[ i for i in protection_properties.columns])
    selection_database = subdata.query(Master_key_Column+' in '+str(selection))
    list_of_coverage = list(selection_database[column].astype('int64').max() for column in Attack_List)
    if len(list_of_coverage) != 0 :
        ret = (sum(list_of_coverage)/len(list_of_coverage))*100
    else :
        ret = 1
    return ret

def return_coverage_ponderated(selection,database,ponderation):
    subdata = pa.DataFrame(database,columns=[ i for i in protection_properties.columns])
    selection_database = subdata.query(Master_key_Column+' in '+str(selection))
    list_of_coverage = list(selection_database[column].astype('int64').max() for column in Attack_List)
    if len(list_of_coverage) != 0 :
        ret = (sum(np.multiply(list_of_coverage,ponderation))/sum(ponderation))*100
    else :
        ret = 1
    return ret



def return_cost(selection,database):
    subdata = pa.DataFrame(database,columns=[ i for i in protection_properties.columns])
    selection_database = subdata.query(Master_key_Column+' in '+str(selection))
    a = selection_database[Total_Cost_Column].sum()
    if a == 0:
        a = 1
    return(a)




#
# #     App is based on a main editable tab that is used to generate report depanding on values and user selection
# TODO add checkbox

def generate_table():
    return html.Div([dash_table.DataTable(
        id='datatable-interactivity',
        columns=
        [{"name": i, "id": i,'type':'text', "presentation":"markdown"} for i in protection_properties.columns 
        if i == Header_Column] +
        [
            {"name": i, "id": i, "editable": True if ((i in Attack_List)or (i in Cost_input_Columns)) else False} for i in protection_properties.columns
            # omit the column that should be hidden
            if (not(i in Hidden_Columns)) 
        ]
        ,
        data=protection_properties.to_dict('records'),
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
        style_cell={'textAlign': 'center'},
        css=[
            {"selector": "td.cell--selected, td.focused", "rule": 'background-color: white !important'},
            {"selector": "td.cell--selected, td.unfocused", "rule": 'background-color: white !important'},
            {"selector": ".row-1","rule": 'margin-left: 10px'},
            {"selector": ".row","rule": 'flex-wrap: nowrap'},
            {"selector": "td p","rule": 'margin: 0;text-align: center'},
        ],

    )
    ,html.Div(id='datatable-container')
    ]
    )



#
# #     This dropdown is used to have a better view of selected techs but selection is shared with main tab
#

def dropdown():
    return html.Div([
    dcc.Dropdown(
        id='dropdown-selector',
        options= [{'label':i,'value':i} for i in protection_properties['id']],
        multi=True,
        placeholder="Select one or more protection technology ...",
    ),
    ])


#
# #     This alert is used to display if input are weird
#

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
# #     This alert is used to display when update is in progress for fuzz tab
#

def alertUpdate():
    return html.Div([
        dbc.Alert(
           "Update in progress",
            id="alert-progress",
            is_open=False,
            # duration=20000,
            color="warning",
            dismissable=True,
        ),
    ])

#
# #     This tab should contain selected protection coverage attributes as well as attacks properties 
#

def selection_coverage_attributes():
    return html.Div([
        dash_table.DataTable(
            id="select-attribute-coverage",
            style_cell=dict(whiteSpace='normal',textAlign='center'),
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
                                {
                    'if':{
                        'column_id': 'Attacks'
                    },
                    'width': '40%'
                },
                                {
                    'if':{
                        'column_id': 'Attack easyness factor'
                    },
                    'width': '30%'
                },
                {
                    'if':{
                        'column_id': 'Selection accumulated Coverage'
                    },
                    'width': '30%'
                },
            ],
            style_table={'overflowX': 'auto'},
            css=[
                {"selector": "td p","rule": 'margin: 0;text-align: center'},
            ]
        )
    ])


#
# #     This tab should contain selected protection cost attributes 
#

def selection_cost_attributes():
    return html.Div([
        dash_table.DataTable(
            id="select-attribute",
            style_cell={'textAlign': 'center'},
                       
        )
    ])


#
# #     This digit display should contain selected protection attributes total
#

def selection_total_cost():
    return html.Div([
        daq.LEDDisplay(
            label="Total Cost",
            id="total-display",
        )
    ])


#
# #     This display should contain an overview of the best results from the fuzz campain
#

def generate_fuzzy_report(dataset):
    fig = px.scatter_3d(
        dataset,
        y="cost",
        z="coverage",
        color="coverage over cost ponderated",
        x="nb_tech_used",
        height=1200,
        hover_data=["techs"],
        symbol='source',
        size='size',
        size_max=24,
        color_continuous_scale='Viridis')
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene_camera = dict(eye=dict(x=-1.5, y=-0.75, z=1.5)),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
            )
    )
    return fig



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
    selection_subset = protection_properties.loc[values]
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
        table_synced_value_1 = [np.where(protection_properties.index == sync_value[i])[0][0] for i in range(len(sync_value))] if sync_value != dropdown_sync_value else dash.no_update
    else:
        selection_subset = protection_properties.loc[selection_table]
        dropdown_sync_value = list(selection_subset[Master_key_Column])
        table_synced_value_1 = [np.where(protection_properties.index == sync_value[i])[0][0] for i in range(len(sync_value))] if sync_value != dropdown_sync_value else dash.no_update
    
    if selection_dropdown is None:
        table_synced_value = None
        dropdown_sync_value_1 = sync_value if sync_value != selection_dropdown else dash.no_update
    else:
        table_synced_value =[np.where(protection_properties.index == selection_dropdown[i])[0][0] for i in range(len(selection_dropdown))]
        dropdown_sync_value_1 = sync_value if sync_value != selection_dropdown else dash.no_update
    
    return [dropdown_sync_value_1,table_synced_value_1]



#
# #     folowing callback may be splitted into several but the reuse of values generated in summary tab make it easier this way
#

@app.callback(
    [Output('select-attribute-coverage', 'data'),
    Output('select-attribute-coverage', 'columns'),
    Output('datatable-interactivity-pie-coverage', 'figure'),
    Output('datatable-interactivity-pie-coverage-ponderated', 'figure'),
    Output('uncovered-attack', 'data'),
    Output('covered-attack', 'data'),
    ],
    [Input('sync', 'data'),
    Input('datatable-interactivity', 'data'),
    Input('select-attribute-coverage', 'data_timestamp')
    ],[State('select-attribute-coverage', 'data')]
    )

def generate_summary(
 selected_rows, # the tech selected by both checkboxes and dropdown system
 datatab, # is protection_properties but updated by user
 updated_datas_timestamp, #just to have access to the data updated by user (easyness factor)
 updated_datas           ):
    

    # we need an up to date database of attack properties if user have changed the factor
    if not(updated_datas is None):
        attack_easyness_updated = []
        for row in updated_datas:
            attack_easyness_updated.append(int(row['Attack easyness factor']))
    else:
        attack_easyness_updated = list(attack_properties['Attack implementation cost'])
    # at this point easyness factor should be up to date

    #we need properties of the selected rows
    if selected_rows is None:
        dff = protection_properties
    else:
        subdata = pa.DataFrame(datatab,columns=[ i for i in protection_properties.columns])
        subdata['id'] = subdata[Master_key_Column]
        subdata.set_index('id', inplace=True, drop=False)
        dff = subdata.loc[selected_rows]
    # at this point we should have all the datas needed to get coverage of selection 

    #
    # # the following is needed to have a dynamic (potentially extensible) tab
    #
    accucoverage= pa.DataFrame({
        "Attacks":Attack_List,
        "Attack easyness factor":attack_easyness_updated,
        "Selection accumulated Coverage": list(dff[column].astype('int64').max() for column in Attack_List) #values in tab are or 0 or 1 so OR(array) is equivalent to max(array)
        })
    accucoverage['factor_hidden']=accucoverage['Selection accumulated Coverage']*(accucoverage['Attack easyness factor']) #used later
    accucoverage['Attack-with-ref'] = '['+attack_properties['Attack']+']('+attack_properties['related article']+')' #useful to display link

    columns_accucoverage = [
        {"name": 'Attacks', "id": 'Attack-with-ref', "editable": False,"presentation":"markdown"},
        {"name": "Attack easyness factor", "id": "Attack easyness factor", "editable": True},
        {"name": 'Selection accumulated Coverage', "id": 'Selection accumulated Coverage', "editable": False}
    ]
    
    #
    # #     following data are used for coverage pie display
    #
    Pie_coverage_data = {
        'coverage':['vulnerability remaining','covered attacks'],
        'nb':[(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]).count()[0],(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 1]).count()[0]]
        }
    Pie_coverage_graph= px.pie(Pie_coverage_data,
         values='nb',
         names='coverage',
         color='coverage',
         color_discrete_map={'vulnerability remaining':'tomato','covered attacks':'lightgreen'}
         )

    #
    # #     following data are used for coverage ponderated pie display
    #
    Pie_coverage_ponderated_data= {
        'coverage':['vulnerability remaining ponderated','covered attacks ponderated'],
        'nb':[(accucoverage['Attack easyness factor'].sum())-(accucoverage['factor_hidden'].sum()),accucoverage['factor_hidden'].sum()]
        }
    Pie_coverage_ponderated_graph = px.pie(Pie_coverage_ponderated_data,
        values='nb',
        names='coverage',
        color='coverage',
        color_discrete_map={'vulnerability remaining ponderated':'#CC0000','covered attacks ponderated':'#007E33'}
        )

    return [accucoverage.to_dict('records'),columns_accucoverage,       
        Pie_coverage_graph,
        Pie_coverage_ponderated_graph,
        list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 0]['Attacks']), # Theses two lists are useful to display uncovered attack in red in the main tab
        list(accucoverage.loc[accucoverage['Selection accumulated Coverage']== 1]['Attacks']),
        ]


#
# #     following callback display the cost properties of the system made by user selected elements
#
@app.callback(
    [Output('select-attribute', 'data'),
    Output('select-attribute', 'columns'),
    Output('total-display', 'value'),
    Output('fade-when-selection', 'is_in'),
    ],
    [Input('sync', 'data'),
    Input('datatable-interactivity', 'data')
    ])
def updateCost(selection,mega_tab):
    if (selection is None) or (selection == []):
        data = []
        sum_cost = 0
        columns = []
        display = False
    else :
        solution_cost = []
        for row in mega_tab:
            if row[Master_key_Column] in selection :
                solution_cost.append(row[Total_Cost_Column])
        data = pa.DataFrame({
            'Protection Selected': list(selection),
            'Cost': list(solution_cost),
        })
        data = data.to_dict('records')
        columns = [{"name": i, "id": i} for i in ['Protection Selected','Cost']]
        display = True
        sum_cost = sum(solution_cost)
        if sum_cost == 0:
            sum_cost = 1
    return [data,columns,sum_cost,display]


#
# #     folowing callback should display the solutions generated during fuzzing
#
@app.callback(
    [Output('fuzzy-data-display', 'figure'),
    ],
    [Input('sync', 'data'),
    Input('datatable-interactivity', 'data'),
    Input('updated-fuzzy', 'data'),
    Input('select-attribute-coverage', 'data'),
    ]
    )
def fuzzy_graph(selection,data_uptodate,fuzzy_uptodate,attack_properties):
    if fuzzy_uptodate is None :
        to_report = fuzzybests
        to_report['coverage over cost ponderated'] = to_report['coverage_over_cost']
    else:
        to_report = pa.read_json(fuzzy_uptodate,orient='split')
    if not((selection is None) or (selection == [])):
        attack_properties = pa.DataFrame(attack_properties)
        attack_factor = list(attack_properties['Attack easyness factor'])
        selection = {
            'techs':str(selection),
            'coverage':return_coverage(selection,data_uptodate),
            'cost':return_cost(selection,data_uptodate),
            'source':'selection',
            'nb_tech_used':len(selection),
            'size':4,
            'coverage ponderated':return_coverage_ponderated(selection,data_uptodate,attack_factor),
        }
        if selection['cost'] == 0:
            selection['cost']=1
        
        selection['coverage over cost ponderated']=selection['coverage ponderated']/selection['cost']
        to_report = to_report.append(selection,ignore_index = True)
    return generate_fuzzy_report(to_report)


#
# #     folowing callback should manage update button and alert of update in progress
#
@app.callback(
    [Output('update-button', 'children'),
    Output('update-button', 'disabled'),
    Output('alert-progress', 'is_open'),
    ],
    [Input('update-button', 'n_clicks'),
    ],
    group='buttongroup'
    )
def button_handler(click):
    context = dash.callback_context
    if (context.triggered[0]['prop_id']) == 'update-button.n_clicks':
        return [[dbc.Spinner(size="sm"), " Loading..."],True,True]
    return [["Update fuzzy graph with modified values (may take time)"],False,False]

@app.callback([Output('update-button', 'children'),
    Output('update-button', 'disabled'),
    Output('alert-progress', 'is_open'),
    ],
    [Input('generation-status', 'is_open'),
    ],group='buttongroup'
    )
def finish_update_handler(finish):
    return [["Update fuzzy graph with modified values (may take time)"],False,False]



#
# #     folowing callback should update fuzzy best solutions with changed characteristics
#
@app.callback(
    [Output('updated-fuzzy', 'data'),
    Output('generation-status', 'is_open')
    ],
    [Input('select-attribute-coverage', 'data'),
    Input('datatable-interactivity', 'data'),
    Input('update-button', 'disabled'),
    ],
    )
def updateur(attack_info,protect_info,asked_update):
    # Prevent any update when values are changed and no update button pressed
    context = dash.callback_context
    if not(asked_update):
        raise dash.exceptions.PreventUpdate
    
    updated_fuzzy = fuzzybests
    attack_info = pa.DataFrame(attack_info)
    attack_factor = list(attack_info['Attack easyness factor'])

    def updateur_cost_helper(x):
        return return_cost((list(j[1:-1] for j in (x[1:-1]).split(', '))),protect_info)
    def updateur_coverage_ponderated_helper(x):
        return return_coverage_ponderated((list(j[1:-1] for j in (x[1:-1]).split(', '))),protect_info,attack_factor)
    def updateur_coverage_helper(x):
        return return_coverage((list(j[1:-1] for j in (x[1:-1]).split(', '))),protect_info)

    updated_fuzzy['cost'] = updated_fuzzy['techs'].apply(updateur_cost_helper)
    updated_fuzzy['coverage'] = updated_fuzzy['techs'].apply(updateur_coverage_helper)
    updated_fuzzy['coverage ponderated'] = updated_fuzzy['techs'].apply(updateur_coverage_ponderated_helper)
    updated_fuzzy['coverage over cost ponderated']=updated_fuzzy['coverage ponderated']/updated_fuzzy['cost']

    return [updated_fuzzy.to_json(orient='split'),True]





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                      Display is here                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #   

app.layout = dbc.Container(
    [
        html.H1([dcc.Markdown("Protection coverage simulation [more about](https://github.com/kacouane/security-sys-dash)")],style={'textAlign': 'center'}),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([ 
                    dbc.CardHeader('Protection Technology properties:',style={'fontWeight': 'bold'}),
                    html.Div(alerter()),
                    html.Div(generate_table()),
                    html.Div(dropdown(),style={'padding': 10}),
                    html.Div(dbc.Button("Update fuzzy graph with modified values (may take time)",
                    id="update-button",
                    outline=True,
                    color="warning",
                    block=True)
                    ,style={'padding': 15}
                ),  
                ]
                ),
            ],md=8
            ),
            dbc.Col([
            dbc.Card([ 
                dbc.CardHeader('Selection protection summary:',style={'fontWeight': 'bold'}),
                dbc.Col([
                    html.Div(selection_coverage_attributes(),style={'padding': 15}),

                    dbc.Row([
                        dbc.Col(dcc.Graph(id='datatable-interactivity-pie-coverage'),md=6),
                        dbc.Col(dcc.Graph(id='datatable-interactivity-pie-coverage-ponderated'),md=6),
                    ])
                ]),
            ]),
            ],md=4),
        ]),
        
        dbc.Row( [
            dbc.Col([
                dbc.Fade(
                dbc.Card([
                    dbc.CardHeader('System chosen Cost properties:'),
                    dbc.CardBody(
                    dbc.Row([
                    dbc.Col(html.Div(selection_cost_attributes())),
                    dbc.Col(html.Div(selection_total_cost(),style={'padding-left': 5}),md=2),
                    ]),
                    )
                ]),
                id="fade-when-selection",
                is_in=False,
                ),
            ],md=4
            ),
            dbc.Col([
                dbc.Card([
                dbc.CardHeader('Graph made from the 2000 best configuration output of a fuzzing campain:'),
                dbc.CardBody([
                    alertUpdate(),
                    html.Div(dcc.Graph(id='fuzzy-data-display'),style={"padding": 10}),
                ]
                )])
            ],style={"padding": 5}
            ),

        ]
        ),

        dcc.Store(id="sync"),
        dcc.Store(id="uncovered-attack"),
        dcc.Store(id="covered-attack"),
        dcc.Store(id='updated-fuzzy'),
        dbc.Toast(
            ["Thank you for your time ;-p"],
            id="generation-status",
            header="Update of fuzzy database done",
            is_open=False,
            dismissable=False,
            duration=5000,
            icon="success",
            style={"position": "fixed", "bottom": 66, "left": 10, "width": 350},
        ),
        #TODO generate report
        #generate best solution
    ],
    fluid=True,
)




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                      App start here                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == '__main__':
    app.run_server(debug=False)