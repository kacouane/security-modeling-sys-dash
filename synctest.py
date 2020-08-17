import dash
import dash_html_components as html
# import dash_extensions # import group #CallbackGrouper
import dash_core_components as dcc
from dash_extensions.enrich import Dash, Output, Input, State


# app = Dash()
# app.layout = html.Div([html.Button("Button 1", id="btn1"), html.Button("Button 2", id="btn2"), html.Div(id="div")])
# # dcb = DashCallbackBlueprint() 


# @app.callback(Output("div", "children"), [Input("btn1", "n_clicks")],group="g1")
# def click_btn1(n_clicks):
#     return "You clicked btn1"


# @app.callback(Output("div", "children"), [Input("btn2", "n_clicks")],group="g1") 
# def click_btn2(n_clicks):
#     return "You clicked btn2"


# # dcb.register(app)  

# if __name__ == '__main__':
#     app.run_server()

# Create app.
min_value, max_value = 100, 1000
app = Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = html.Div([
    dcc.Input(id="input", type="numeric", min=min_value, max=max_value),
    dcc.Slider(id="slider", min=min_value, max=max_value),
    dcc.Store(id="sync")
])

# Create grouped callbacks.
# dcb = CallbackGrouper()

@app.callback(Output("sync", "data"), [Input("input", "value")],group="my_group")
def sync_input_value(value):
    return value

@app.callback(Output("sync", "data"), [Input("slider", "value")],group="my_group")
def sync_slider_value(value):
    return value

@app.callback([Output("input", "value"), Output("slider", "value")], [Input("sync", "data")],
              [State("input", "value"), State("slider", "value")])
def update_components(current_value, input_prev, slider_prev):
    # Update only inputs that are out of sync (this step "breaks" the circular dependency).
    input_value = current_value if current_value != input_prev else dash.no_update
    slider_value = current_value if current_value != slider_prev else dash.no_update
    return [input_value, slider_value]

# dcb.register(app)

if __name__ == '__main__':
    app.run_server(debug=False)