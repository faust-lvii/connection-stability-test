import asyncio
import sys
from datetime import datetime
import webbrowser
from pathlib import Path

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from flask import Flask

from config.config import Config
from core.network_probe import NetworkProbe
from core.data_store import DataStore

# Global değişkenler
probes = []
probe_data = {}
data_store = None
monitoring_active = False

# Flask ve Dash uygulamasını oluştur
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Ağ İzleme Sistemi", className="text-center my-4"),
            
            # Durum kartı
            dbc.Card([
                dbc.CardBody([
                    html.H4("Sistem Durumu", className="card-title"),
                    html.Div([
                        html.P(id='status-text', children="İzleme Durumu: Beklemede", className="mb-2"),
                        dbc.Button(
                            "İzlemeyi Başlat",
                            id='start-stop-button',
                            color="success",
                            className="me-2"
                        ),
                    ]),
                ])
            ], className="mb-4"),
            
            # Kontrol kartı
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Hedef:", className="fw-bold"),
                            dcc.Dropdown(
                                id='target-dropdown',
                                placeholder="İzlenecek hedefi seçin"
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Güncelleme Aralığı:", className="fw-bold"),
                            dcc.Dropdown(
                                id='interval-dropdown',
                                options=[
                                    {'label': '1 saniye', 'value': 1},
                                    {'label': '5 saniye', 'value': 5},
                                    {'label': '10 saniye', 'value': 10},
                                    {'label': '30 saniye', 'value': 30},
                                    {'label': '1 dakika', 'value': 60}
                                ],
                                value=1,
                                placeholder="Güncelleme sıklığını seçin"
                            ),
                        ], width=6),
                    ]),
                ])
            ], className="mb-4"),
            
            # Metrikler kartı
            dbc.Card([
                dbc.CardBody([
                    html.H4("Anlık Metrikler", className="card-title mb-3"),
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Gecikme", className="text-center"),
                                    html.H3(id='current-latency', children="-", className="text-center text-primary")
                                ])
                            ]),
                            width=4
                        ),
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Paket Kaybı", className="text-center"),
                                    html.H3(id='current-packet-loss', children="-", className="text-center text-danger")
                                ])
                            ]),
                            width=4
                        ),
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Durum", className="text-center"),
                                    html.H3(id='current-status', children="-", className="text-center")
                                ])
                            ]),
                            width=4
                        ),
                    ])
                ])
            ], className="mb-4"),
            
            # Grafik kartı
            dbc.Card([
                dbc.CardBody([
                    html.H4("Performans Grafikleri", className="card-title"),
                    dcc.Graph(id='metrics-graph'),
                    dcc.Interval(
                        id='interval-component',
                        interval=1000,  # milisaniye cinsinden
                        n_intervals=0
                    )
                ])
            ], className="mb-4"),
            
            # Tablo kartı
            dbc.Card([
                dbc.CardBody([
                    html.H4("Son Ölçümler", className="card-title"),
                    html.Div(id='metrics-table')
                ])
            ])
        ], width=12)
    ])
], fluid=True)

@app.callback(
    [Output('metrics-graph', 'figure'),
     Output('metrics-table', 'children'),
     Output('current-latency', 'children'),
     Output('current-packet-loss', 'children'),
     Output('current-status', 'children'),
     Output('current-status', 'className')],
    [Input('interval-component', 'n_intervals'),
     Input('target-dropdown', 'value')]
)
def update_metrics(n_intervals, target):
    # Boş grafik şablonunu oluştur
    empty_fig = go.Figure()
    empty_fig.update_layout(
        title='Veri Bekleniyor...',
        xaxis=dict(title='Zaman'),
        yaxis=dict(title='Değer'),
        height=400,
        annotations=[dict(
            text='İzleme başlatıldığında veriler burada görüntülenecek',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0.5,
            y=0.5
        )]
    )

    if not target or target not in probe_data or not monitoring_active:
        return empty_fig, [], "-", "-", "Beklemede", "text-center text-warning h3"
    
    data = probe_data[target]
    if not data:
        return empty_fig, [], "-", "-", "Beklemede", "text-center text-warning h3"

    # Grafik oluştur
    fig = go.Figure()
    
    times = [d['timestamp'] for d in data]
    latencies = [d.get('latency', 0) for d in data]
    
    fig.add_trace(go.Scatter(
        x=times,
        y=latencies,
        name='Gecikme (ms)',
        line=dict(color='blue')
    ))
    
    packet_losses = [d.get('packet_loss', 0) for d in data]
    fig.add_trace(go.Scatter(
        x=times,
        y=packet_losses,
        name='Paket Kaybı (%)',
        line=dict(color='red'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Ağ Performans Metrikleri',
        xaxis=dict(title='Zaman'),
        yaxis=dict(title='Gecikme (ms)'),
        yaxis2=dict(title='Paket Kaybı (%)', overlaying='y', side='right'),
        height=400,
        margin=dict(t=30, b=30, l=50, r=50)
    )

    # Tablo oluştur
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Zaman"),
                html.Th("Hedef"),
                html.Th("Durum"),
                html.Th("Gecikme (ms)"),
                html.Th("Paket Kaybı (%)")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(d['timestamp']),
                html.Td(d['target']),
                html.Td(d['status']),
                html.Td(str(d.get('latency', '-'))),
                html.Td(str(d.get('packet_loss', '-')))
            ]) for d in reversed(data[-10:])  # Son 10 veriyi göster
        ])
    ], bordered=True, hover=True, striped=True)

    # Anlık değerler
    last_data = data[-1]
    latency = f"{last_data.get('latency', '-')} ms"
    packet_loss = f"{last_data.get('packet_loss', '-')}%"
    status = last_data['status']
    status_class = {
        'OK': 'text-center text-success h3',
        'FAIL': 'text-center text-danger h3',
        'ERROR': 'text-center text-warning h3'
    }.get(status, 'text-center text-secondary h3')

    return fig, table, latency, packet_loss, status, status_class

@app.callback(
    [Output('start-stop-button', 'children'),
     Output('start-stop-button', 'color'),
     Output('status-text', 'children')],
    [Input('start-stop-button', 'n_clicks')],
    [State('start-stop-button', 'children')]
)
def toggle_monitoring(n_clicks, current_text):
    if n_clicks is None:
        return "İzlemeyi Başlat", "success", "İzleme Durumu: Beklemede"
    
    global monitoring_active
    if current_text == "İzlemeyi Başlat":
        monitoring_active = True
        return "İzlemeyi Durdur", "danger", "İzleme Durumu: Aktif"
    else:
        monitoring_active = False
        return "İzlemeyi Başlat", "success", "İzleme Durumu: Durduruldu"

async def update_data():
    """Arka planda sürekli veri toplama."""
    while True:
        if monitoring_active:
            for probe, interval in probes:
                try:
                    data = await probe.perform_check()
                    await data_store.store_metrics(data)
                    
                    if probe.target not in probe_data:
                        probe_data[probe.target] = []
                    
                    probe_data[probe.target].append(data)
                    if len(probe_data[probe.target]) > 100:  # Son 100 veriyi tut
                        probe_data[probe.target].pop(0)
                except Exception as e:
                    print(f"Veri güncelleme hatası: {str(e)}")
        
        await asyncio.sleep(1)

async def main():
    """Ana uygulama fonksiyonu."""
    try:
        global probes, data_store, probe_data
        
        # Yapılandırmayı yükle
        config = Config("config.yaml")
        
        # Veritabanı bağlantılarını oluştur
        data_store = DataStore(
            influx_url=config.get('influxdb.url'),
            influx_token=config.get('influxdb.token'),
            influx_org=config.get('influxdb.org'),
            influx_bucket=config.get('influxdb.bucket'),
            postgres_dsn=config.get('postgresql.dsn')
        )

        # Ağ izleyicilerini oluştur
        for target in config.get('targets', []):
            probe = NetworkProbe(
                target=target['address'],
                timeout=1.0
            )
            probes.append((probe, target['interval']))
            probe_data[target['address']] = []

        # Dropdown seçeneklerini güncelle
        app.layout['target-dropdown'].options = [
            {'label': target['name'], 'value': target['address']}
            for target in config.get('targets', [])
        ]
        
        # Veri toplama görevini başlat
        asyncio.create_task(update_data())
        
        # Tarayıcıyı aç
        webbrowser.open('http://localhost:8050')
        
        # Sunucuyu başlat
        app.run_server(debug=False, use_reloader=False)

    except Exception as e:
        print(f"Uygulama başlatma hatası: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 