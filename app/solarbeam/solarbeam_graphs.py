import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

NO_MARGINS={'t':0, 'r':0, 'b': 0, 'l': 0}

def calc_costo_instalacion(kwp):
    costo = 0
    if kwp < 2.5:
        costo = 1400 * kwp
    elif kwp < 15:
        costo = 1300 * kwp
    elif kwp < 100:
        costo = 1200 * kwp
    elif kwp < 250:
        costo = 1100 * kwp
    else:
        costo = 1000 * kwp

    return costo * 20

def calc_costo_mto(kwp, año):
    costo = 0
    if kwp < 5:
        costo = 35 * kwp
    elif kwp < 15:
        costo = 36 * kwp
    elif kwp < 30:
        costo = 33 * kwp
    elif kwp < 50:
        costo = 27 * kwp
    elif kwp < 100:
        costo = 37 * kwp
    elif kwp < 250:
        costo = 35 * kwp
    else:
        costo = 28 * kwp

    return costo * año * 20

def get_ahorros_graph(ahorro_df, cap=1):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ahorro_df['year'], y=ahorro_df[f'ahorro_sin_inflacion-{cap}'], name='Ahorro sin inflación'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ahorro_df['year'], y=ahorro_df[f'ahorro_con_inflacion-{cap}'], name='Ahorro con inflación'
        )
    )
    fig.update_layout(
        yaxis_title='MXN', xaxis_title='Años', margin={'t': 15, 'r': 15, 'l':0, 'b':0},
        legend={'orientation': 'h', 'xanchor': 'center', 'x':0.5}
    )
    return fig.to_json()

def get_comp_consumo_graph(consumo_df):
    consumo_df['consumo_total'] = consumo_df[['kwh-base', 'kwh-inter', 'kwh-punta']].sum(axis=1)

    fig = make_subplots(rows=2, cols=1, subplot_titles=('Comparación de generación y consumo', 'Facturación mensual'))

    #SUBPLOT 1
    fig.add_trace(go.Bar(
        x= consumo_df.mes, y=consumo_df['generation'], name = "Generación solar", marker_color="orange",
            hovertemplate= '<i>Mes:</i> %{x}<br><i>Consumo:</i><b> %{y}</b><extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x= consumo_df.mes, y=consumo_df['consumo_total'], name = "Consumo actual", marker_color="blue",
            hovertemplate= '<i>Mes:</i> %{x}<br><i>Consumo:</i><b> %{y}</b><extra></extra>'
    ))

    #SUBPLOT2 
    fig.add_trace(go.Bar(
        x= consumo_df.mes, y=consumo_df[f'nuevo_precio_kwh-1'], name = "Nueva facturación", marker_color="orange",
            hovertemplate= '<i>Mes:</i> %{x}<br><i>Costo:</i><b> $%{y:.2f}<b><extra></extra>', opacity=0.5
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        x= consumo_df.mes, y=consumo_df['precio_kwh'], name = "Facturación actual", marker_color="blue",
            hovertemplate= '<i>Mes:</i> %{x}<br><i>Costo:</i><b> $%{y:.2f}</b><extra></extra>', opacity=0.5
    ), row=2, col=1)

    fig.update_layout(
        xaxis_title="Meses", yaxis_title="Energía kWh",
        xaxis2_title="Meses", yaxis2_title="Costo Pesos $MXN",
        margin={'t': 15}
    )

    return fig.to_json()

def get_expected_gen_graph(consumo_df, cap=1):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=consumo_df['mes'], y=consumo_df[f'generation-{cap}'], name="Generación",
        hovertemplate='<i>Fecha: %{x}</i><br><i>Produccion solar: </i><b>%{y} kWp</b><extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Fecha', yaxis_title= "kWp de producción solar",
        margin=NO_MARGINS
    )

    return fig.to_json()

def get_riv_graph(ahorro_df, cap=1):
    ahorro_df['fecha'] = pd.date_range(start='2020-01-01', end='2045-01-01', freq='y')


    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ahorro_df['fecha'], y=ahorro_df[f'ahorro_sin_inflacion-{cap}'], mode='lines', name='Ahorro sin incremento', marker_color='green',
        hovertemplate='<i>Ahorro sin incremento: </i><b> %{y:$,.2f}</b><extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=ahorro_df['fecha'], y=ahorro_df[f'ahorro_con_inflacion-{cap}'], mode='lines', name='Ahorro con inflación', marker_color='blue',
        hovertemplate='<i>Ahorro con inflación: </i><b> %{y:$,.2f}</b><extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=ahorro_df['fecha'], y=ahorro_df[f'costo_total-{cap}'], mode='lines', name='Inversión más mantenimiento', marker_color='yellow',
        hovertemplate='<i>Inversión más mantenimiento: </i><b> %{y:$,.2f}</b><extra></extra>'
    ))

    fig.update_layout(xaxis_title='Año', yaxis_title="$MXN", margin=NO_MARGINS)
    return fig.to_json()

def get_expected_prod_graph(solar_info_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=solar_info_df['ind'], y=solar_info_df['generacion_graph'], name="Generación",
        hovertemplate='<i>Fecha: %{x}</i><br><i>Produccion solar: </i><b>%{y} kWp</b><extra></extra>'
    ))

    fig.update_layout(
        title="Producción anual esperada", xaxis_title='Fecha', yaxis_title= "kWp de producción solar"
    )
    return fig.to_dict()

def get_riv_cap_graph(riv_dict, cap):
    df = pd.DataFrame.from_dict(riv_dict, orient='index', columns=['riv']).reset_index().sort_values('index')
    df['capacidad'] = (df['index'].astype(float) * 100).astype(str) + '%'

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['capacidad'], y=df['riv'], mode='lines+markers', name='RIV', marker_color='green',
        hovertemplate='<i>RIV: </i><b> %{y:.2f}</b><extra></extra>'
    ))
        
    fig.update_layout(
        title="Retorno de inveresión por diferentes capacidades del sistema",
        xaxis_title="Capacidades del sistema", yaxis_title="Años de retorno de inversión",
    )

    return fig.to_json()

def get_consumo_graphs(consumo_dict, ahorro_dict, solar_info_dict, riv_inf_dict, riv_noinf_dict):
    consumo_df = pd.DataFrame(consumo_dict)
    ahorro_df = pd.DataFrame(ahorro_dict)
    ahorro_df.to_csv('ahorro.csv')
    solar_info_df = pd.DataFrame(solar_info_dict)
    capacidad = consumo_df['cap-1'][0]

    graphs = {
        'ahorros': get_ahorros_graph(ahorro_df),
        'genProyectada': get_expected_gen_graph(consumo_df),
        'comparacionConsumo': get_comp_consumo_graph(consumo_df),
        'riv': get_riv_graph(ahorro_df),
        'rivCapInf': get_riv_cap_graph(riv_inf_dict, capacidad)
    }

    costos = {
        'inversion': f"{calc_costo_instalacion(capacidad):,.2f}",
        'mantenimiento': f"{calc_costo_mto(capacidad, 1):,.2f}"
    }

    return graphs, f"{capacidad:,.2f}", costos