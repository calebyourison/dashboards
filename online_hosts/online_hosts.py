import datetime
from ipaddress import IPv4Address

from dash import Dash, html, dash_table, dcc, Input, Output

from tech_tools.cli import ping_range_ip
from tech_tools.utilities import local_ip
from tech_tools.utilities import tcp_ip_port_scanner

update_frequency_seconds = 30

my_ip = local_ip()

hosts = {
    '8.8.8.8': 'google',
    str(my_ip): 'my_machine',
    '127.0.0.1': 'my_loopback',
    '10.11.61.132': 'offline_machine',
}

ports = [80, 443]

page_background_color = 'rgb(217,250,245)'
data_table_header = "rgb(102,242,218)"
data_table_background = "rgb(149,206,250)"

offline_host_color = 'rgb(202,81,81)'


def current_ping_data():
    ping_responses = ping_range_ip([ip for ip in hosts.keys()], timeout=2)
    host_responses = [
        {'ip_address': ip_address,
         'host': name,
         'ping_response': 'online' if IPv4Address(ip_address) in ping_responses else 'offline'
         }
        for ip_address, name in hosts.items()
    ]
    return host_responses

def current_tcp_ip_ports_data():
    tcp_ip_ports_responses = tcp_ip_port_scanner([ip for ip in hosts.keys()], ports, df=False)
    hosts_responses = [
        {'ip_address': str(ipaddress),
         'host': hosts[str(ipaddress)],
         'responsive_ports': [str(port) + ',' for port in responsive_ports]}
        for ipaddress, responsive_ports in tcp_ip_ports_responses.items()
    ]
    return hosts_responses

def ping_response_table():
    table = dash_table.DataTable(
                id='ping_table',
                data = current_ping_data(),
                columns = [
                    {
                        'name':'host',
                        'id': 'host'
                    },
                    {
                        'name':'ip_address',
                        'id': 'ip_address'
                    },
                    {
                        'name': 'ping_response',
                        'id': 'ping_response'
                    }
                ],
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor=data_table_header),
                style_data=dict(backgroundColor=data_table_background),
                sort_action='native',
                style_data_conditional=[
                    {'if': {
                        'filter_query': '{ping_response} = "offline"',
                        'column_id': 'ping_response'
                    },
                        'background_color': offline_host_color
                    }
                ]
            )

    return table

def tcp_ip_ports_response_table():
    table = dash_table.DataTable(
                id='tcp_ip_ports_table',
                data = current_tcp_ip_ports_data(),
                columns = [
                    {
                        'name':'host',
                        'id': 'host'
                    },
                    {
                        'name':'ip_address',
                        'id': 'ip_address'
                    },
                    {
                        'name': 'responsive_ports',
                        'id': 'responsive_ports'
                    }
                ],
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor=data_table_header),
                style_data=dict(backgroundColor=data_table_background),
                sort_action='native',
            )

    return table

def update_layout():
    layout = html.Div(
        style={"backgroundColor": page_background_color},
        children=[
            html.H2("Host Dashboard"),
            html.H3("Updated: " + str(datetime.datetime.now().replace(microsecond=0)), id='current_time'),

            dcc.Interval(
                id='update_interval',
                interval=update_frequency_seconds * 1000,
                n_intervals=0
            ),

            html.Div(
                id='ping_table_div',
                children=[
                    html.H4('Host Ping Responses'),
                    ping_response_table(),
                ]
            ),

            html.Div(
                id='tcp_ip_ports_table_div',
                children=[
                    html.H4('Hosts Responding On Ports: ' + str(ports)),
                    tcp_ip_ports_response_table()
                ]
            ),
        ]
    )

    return layout


app = Dash(prevent_initial_callbacks=True)

app.layout = update_layout

@app.callback(
    [
        Output(component_id='current_time', component_property='children'),
        Output(component_id='ping_table', component_property='data')],
        Output(component_id='tcp_ip_ports_table', component_property='data'),
    [Input('update_interval', 'n_intervals')]
    )
def update(interval):
    print('updating')

    updated_time = [html.Span("Updated: " + str(datetime.datetime.now().replace(microsecond=0)))]
    print(updated_time)

    updated_ping_data = current_ping_data()
    print(updated_ping_data)

    updated_tcp_ip_ports_data = current_tcp_ip_ports_data()
    print(updated_tcp_ip_ports_data)

    return updated_time, updated_ping_data, updated_tcp_ip_ports_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5050)