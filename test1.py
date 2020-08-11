import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pa

#dataset

dataset = pa.read_csv('/home/antoine/Documents/GDrive/CFI_survey/test excel/Survey_Compare_Tab-database.csv')

dataset['id'] = dataset['Technology']
dataset.set_index('id', inplace=True, drop=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


#generate table 

#TODO make it cute and dropdown filter? or extern ?

def generate_table(dataframe, max_rows=30):
    return dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": False} for i in dataset.columns
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
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= max_rows,
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
    )
def dropdown():
    return html.Div([
    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        id='dropdown-selector',
        options= [{'label':i,'value':i} for i in dataset['Technology']],
        multi=True
    ),
    


    html.Label('Text Input'),
    dcc.Input(value='MTL', type='text'),

    html.Label('Slider'),
    dcc.Slider(
        min=0,
        max=9,
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
        value=5,
    )
],style={'padding': 10})


#here is the display
app.layout = html.Div(children=[
    html.H1(children='test display'),
    generate_table(dataset),
   html.Div( [html.Div(id='datatable-interactivity-container'), html.Div(dcc.Graph(id='datatable-interactivity-pie-container')),html.Hr(),dropdown()],style={'columnCount': 2,'padding': 10}),
    #dropdown()
    #TODO generate report
    #generate best solution
])

@app.callback(
    [Output('datatable-interactivity-container', 'children'),Output('datatable-interactivity-pie-container', 'figure')],
    [Input('datatable-interactivity', 'derived_virtual_row_ids'),
     Input('datatable-interactivity', 'selected_row_ids'),
     Input('datatable-interactivity', 'active_cell')])

def update_graphs(row_ids, selected_row_ids, active_cell):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=dataset.to_rows('dict')` when you initialize
    # the component.
    selected_id_set = set(selected_row_ids or [])

    if selected_row_ids is None:
        dff = dataset
        # pandas Series works enough like a list for this to be OK
        row_ids = dataset['id']
    else:
        dff = dataset.loc[selected_row_ids]

    active_row_id = active_cell['row_id'] if active_cell else None
    active_row = dataset.loc[active_row_id]

   
    accucoverage= pa.DataFrame({
        "Attacks":dataset.columns[2:22],
        "Selection accumulated Coverage": list(max(dff[column].max(),active_row[column]) for column in dataset.columns[2:22])  if active_cell else list(dff[column].max() for column in dataset.columns[2:22])
        })
    df= pa.DataFrame({
        'coverage':['vulnerability remaining','covered attacks'],
        'nb':[accucoverage['Attacks'].count()-sum(dff[column].max()for column in dataset.columns[2:22]),sum(dff[column].max()for column in dataset.columns[2:22])]
        #'nb':[(accucoverage.loc[accucoverage["Selection accumulated Coverage"]==0].count()),(accucoverage.loc[accucoverage["Selection accumulated Coverage"]==1].count())]
        })
    #labels =['covered attacks','vulnerability remaining']
    #values = list(accucoverage['Selection accumulated Coverage'].value_counts(bins=[0,1]))
    
    return html.Div([ 
        html.Label('Selection summary:'),
        dash_table.DataTable(columns=[{"name": i, "id": i} for i in accucoverage.columns],data=accucoverage.to_dict('records')),
        #'Output: {}'.format(accucoverage['Attacks'].count()),
        #dash_table.DataTable(data=accucoveragepie.to_dict('records')),
        #px.pie(data=accucoveragepie)
        ]),px.pie(df, values='nb', names='coverage')

    


if __name__ == '__main__':
    app.run_server(debug=True)
#print(dataset)
