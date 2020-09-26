import json
import sys
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import matplotlib.pyplot as plt


import plotly.tools as tls
tls.set_credentials_file(username='kumar19', api_key='mldCB5cEZ1uYrcuAQAoi')


def get_bro_x(filepath):
    x = []
    with open(filepath, "r") as infile:
        for l in infile.readlines():
            bro_dict = json.loads(l)
            x.append(bro_dict['latency']*1000)

    print (f"{filepath} Mean Latency: {np.mean(x)}")
    print (f"{filepath} Stdev Latency: {np.std(x)}")
    return x

x_production = get_bro_x(sys.argv[1])
x_emulated = get_bro_x(sys.argv[2])
x_replay = get_bro_x(sys.argv[3])


n, bins, patches = plt.hist(x_production, 50, facecolor='green', alpha=0.75)
plt.xlabel('Latency (Production)')
plt.ylabel('Frequency')
plt.title('Frequency of Transaction Latency in milliseconds')
plt.grid(True)
plt.yticks(rotation=45)
plt.show()


n, bins, patches = plt.hist(x_emulated, 50, facecolor='green', alpha=0.75)
plt.xlabel('Latency (Emulated)')
plt.ylabel('Frequency')
plt.title('Frequency of Transaction Latency in milliseconds')
plt.grid(True)
plt.yticks(rotation=45)
plt.show()

n, bins, patches = plt.hist(x_replay, 50, facecolor='green', alpha=0.75)
plt.xlabel('Latency (Replay)')
plt.ylabel('Frequency')
plt.title('Frequency of Transaction Latency in milliseconds')
plt.grid(True)
plt.yticks(rotation=45)
plt.show()
#
#
# trace1 = go.Histogram(
#     x=x_production,
#     opacity=0.75
# )
# trace2 = go.Histogram(
#     x=x_emulated,
#     opacity=0.1
# )
# trace3 = go.Histogram(
#     x=x_replay,
#     opacity=0.75
# )
# data = [trace1, trace2, trace3]
# layout = go.Layout(
#     barmode='overlay'
# )
# fig = go.Figure(data=data, layout=layout)
# py.plot(fig)
