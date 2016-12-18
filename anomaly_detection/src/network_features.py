import dpkt
import socket

#filename='/Users/kartik/Desktop/Siebel Project/microgrid_with_background_traffic/s3-eth5-s5-eth2.pcap'

def dst_list(filename):
    dst_list = []
    i = 0
    start_ts = 0

    print "Extracting features from: ",filename
    pcap_reader = open(filename,'r')
    #print pcap_reader
    for ts, pkt in dpkt.pcap.Reader(pcap_reader):
        final_ts = ts
        if i == 0:
          start_ts = ts

        eth=dpkt.ethernet.Ethernet(pkt) 
        if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
           continue

        ip=eth.data
        #print socket.inet_ntoa(ip.dst)
        if ip.dst in dst_list:
            pass
        else:
            dst_list.append(ip.dst)


        i += 1
    return dst_list, start_ts, final_ts



def network_features(filename, dst_list, start, end):
  #dst_list, start, end = dst_list(filename)
  stats = {}

  for ip_dst in dst_list:
      if ip_dst in stats:
          pass 
      else:
          stats[socket.inet_ntoa(ip_dst)] = []

      tcp_list = [0] * (int(end-start)+1)
      udp_list = [0] * (int(end-start)+1)
      byte_list = [0] * (int(end-start)+1)
      stats_list = []

      for ts, pkt in dpkt.pcap.Reader(open(filename,'r')):

          eth=dpkt.ethernet.Ethernet(pkt) 
          if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
             continue

          ip=eth.data

          if ip.dst == ip_dst:
            byte_list[int(ts-start)]+= len(pkt)

          if ip.p==dpkt.ip.IP_PROTO_TCP and ip.dst == ip_dst:
            tcp_list[int(ts-start)]+=1


          if ip.p==dpkt.ip.IP_PROTO_UDP and ip.dst == ip_dst:
            udp_list[int(ts-start)]+=1

      stats_list.append(tcp_list)
      stats_list.append(udp_list)
      stats_list.append(byte_list)
      stats[socket.inet_ntoa(ip_dst)] = stats_list

    

  return stats