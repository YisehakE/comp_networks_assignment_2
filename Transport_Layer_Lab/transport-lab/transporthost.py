from cougarnet.util import \
        ip_str_to_binary, ip_binary_to_str

from headers import IPv4Header, UDPHeader, TCPHeader, \
        IP_HEADER_LEN, UDP_HEADER_LEN, TCP_HEADER_LEN, \
        TCPIP_HEADER_LEN, UDPIP_HEADER_LEN
from host import Host
from mysocket import UDPSocket, TCPSocketBase

class TransportHost(Host):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.socket_mapping_udp = {}
        self.socket_mapping_tcp = {}

    def handle_tcp(self, pkt: bytes) -> None:
      # 1. Parse the IP packet for headers (i.e IP & UDP) and data stream
      ip_hdr = pkt[:IP_HEADER_LEN]
      tcp_hdr = pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN]

      # 2. Convert parsed bytes into respective header objects, extract attributes
      ip_hdr_obj = IPv4Header.from_bytes(ip_hdr)
      ip_src, ip_dst = ip_hdr_obj.src, ip_hdr_obj.dst

      tcp_hdr_obj = UDPHeader.from_bytes(tcp_hdr)
      tcp_sport, tcp_dport = tcp_hdr_obj.sport, tcp_hdr_obj.dport

      data_len_ip, data_len_tcp = ip_hdr_obj.length - TCPIP_HEADER_LEN, tcp_hdr_obj.length - TCP_HEADER_LEN

      # 3. Look for open UDP socket correspondting to dst addr & port of given packet
      incoming_tuple = (ip_dst, tcp_dport, ip_src, tcp_sport)
      instance_tuple = (ip_dst, tcp_dport, None, None)

      if self.socket_mapping_tcp.get(incoming_tuple) is not None:
          # if data_len_ip == data_len_tcp:
          self.socket_mapping_tcp.get(incoming_tuple).handle_packet(pkt)
      elif self.socket_mapping_tcp.get(instance_tuple) is not None:
          # if data_len_ip == data_len_tcp:
          self.socket_mapping_tcp.get(instance_tuple).handle_packet(pkt)
      else:
          self.no_socket_tcp(pkt) # TODO: determine if call is needed
        
    def handle_udp(self, pkt: bytes) -> None:
        ''' 
          References:
            1) CLASS LECTURE // Lecture 05: Transport (slide 11-AFTER)
            2) ONLINE SOURCE // Registered ports: https://www.sciencedirect.com/topics/computer-science/registered-port

          Questions
            Q: With approach 1, are we assuming local address/port is the source addr/port?
            A: Yes
            
            Q: We are not responsible for fleshing out the send_ip_packet & notify_on_data
              - So what would we need to pass in if built-in libraries are not needed? 
            A: You are to utilize the sockets in the mapping, and use the send/handle functions you built

            Q: What is the key/value pair of socket_mapping_udp?
            A: Key = tuple[dst. addr -> str, dst. port -> int], Value= UDPSocket
        '''
        # 1. Parse the IP packet for headers (i.e IP & UDP) and data stream
        ip_hdr = pkt[:IP_HEADER_LEN]
        udp_hdr = pkt[IP_HEADER_LEN:UDPIP_HEADER_LEN]

        # 2. Convert parsed bytes into respective header objects, extract attributes
        ip_hdr_obj = IPv4Header.from_bytes(ip_hdr)
        ip_dst = ip_hdr_obj.dst

        udp_hdr_obj = UDPHeader.from_bytes(udp_hdr)
        udp_dport = udp_hdr_obj.dport

        data_len_ip, data_len_udp = ip_hdr_obj.length - UDPIP_HEADER_LEN, udp_hdr_obj.length - UDP_HEADER_LEN

        # 3. Look for open UDP socket correspondting to dst addr & port of given packet
        if self.socket_mapping_udp.get((ip_dst, udp_dport)) is not None:
            # if data_len_ip == data_len_udp and ip_hdr_obj.checksum == udp_hdr_obj.checksum:
            self.socket_mapping_udp.get((ip_dst, udp_dport)).handle_packet(pkt)
        else:
            self.no_socket_udp(pkt) # TODO: determine if call is needed

    def install_socket_udp(self, local_addr: str, local_port: int,
            sock: UDPSocket) -> None:
        self.socket_mapping_udp[(local_addr, local_port)] = sock

    def install_listener_tcp(self, local_addr: str, local_port: int,
            sock: TCPSocketBase) -> None:
        self.socket_mapping_tcp[(local_addr, local_port, None, None)] = sock

    def install_socket_tcp(self, local_addr: str, local_port: int,
            remote_addr: str, remote_port: int, sock: TCPSocketBase) -> None:
        self.socket_mapping_tcp[(local_addr, local_port, \
                remote_addr, remote_port)] = sock

    def no_socket_udp(self, pkt: bytes) -> None:
        pass

    def no_socket_tcp(self, pkt: bytes) -> None:
        pass
