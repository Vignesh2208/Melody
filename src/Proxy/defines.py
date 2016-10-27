
# Error Defines
SUCCESS  = 1
FAILURE = 0
IS_SHARED = 1
BUF_NOT_INITIALIZED = -1
TEMP_ERROR = -2

# Other Defines
PROXY_NODE_ID = 0
CMD_QUIT = 1
MAXPKTSIZE  = 1000
SOCKET_TIMEOUT = 5


PROXY_UDP_PORT = 6000         #Proxy listens on this port for udp pkts from PowerSim
POWERSIM_UDP_PORT = 5500      #Power Simulator listens on this port for udp pkts from Proxy
DEFAULT_HOST_UDP_PORT = 5100  #Every network simulated node listens on this port by default for udp pkts from other nodes
DEFAULT_POWERSIM_IP = "127.0.0.1"