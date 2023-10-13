from __future__ import annotations

import random


TCP_FLAGS_SYN = 0x02
TCP_FLAGS_RST = 0x04
TCP_FLAGS_ACK = 0x10

TCP_STATE_LISTEN = 0
TCP_STATE_SYN_SENT = 1
TCP_STATE_SYN_RECEIVED = 2
TCP_STATE_ESTABLISHED = 3
TCP_STATE_FIN_WAIT_1 = 4
TCP_STATE_FIN_WAIT_2 = 5
TCP_STATE_CLOSE_WAIT = 6
TCP_STATE_CLOSING = 7
TCP_STATE_LAST_ACK = 8
TCP_STATE_TIME_WAIT = 9
TCP_STATE_CLOSED = 10

from headers import IPv4Header, UDPHeader, TCPHeader, \
        IP_HEADER_LEN, UDP_HEADER_LEN, TCP_HEADER_LEN, \
        TCPIP_HEADER_LEN, UDPIP_HEADER_LEN

#From /usr/include/linux/in.h:
IPPROTO_TCP = 6 # Transmission Control Protocol
IPPROTO_UDP = 17 # User Datagram Protocol

from icecream import ic

class UDPSocket:
    def __init__(self, local_addr: str, local_port: int,
            send_ip_packet_func: callable,
            notify_on_data_func: callable) -> UDPSocket:

        self._local_addr = local_addr
        self._local_port = local_port
        self._send_ip_packet = send_ip_packet_func
        self._notify_on_data = notify_on_data_func

        self.buffer = []

    ''' Helper function to parse headers and data from a packet.
    @Type pkt: bytes
    @param pkt: a packet from a host containing header and data info to be handled.
    
    @Rtype: tuple[bytes, bytes, bytes]
    @Return: A tuple consisting of IP header, UDP header, & raw data byte streams in order.
    '''
    def parse_packet(self, pkt: bytes) -> tuple(bytes, bytes, bytes):
        # TODO: flesh out helper function
        ip_hdr = pkt[:IP_HEADER_LEN]
        udp_hdr = pkt[IP_HEADER_LEN:UDPIP_HEADER_LEN]
        data = pkt[UDPIP_HEADER_LEN:]

        return ip_hdr, udp_hdr, data
        

    def handle_packet(self, pkt: bytes) -> None:
        # 1. parse the packet
        # ip_hdr, udp_hdr, data = self.parse_packet(pkt)
        ip_hdr = pkt[:IP_HEADER_LEN] # Extract IP header in packet first
        udp_hdr = pkt[IP_HEADER_LEN:UDPIP_HEADER_LEN] # Extract UDP header from packet second
        data = pkt[UDPIP_HEADER_LEN:] # Extract raw data from packet last

        ip_hdr_obj = IPv4Header.from_bytes(ip_hdr)
        udp_hdr_obj = UDPHeader.from_bytes(udp_hdr)

        remote_addr = ip_hdr_obj.src
        remote_port = udp_hdr_obj.sport
      
         # 2. Append data | remote OG IP addr | remote OG port
        self.buffer.append((data, remote_addr, remote_port))

        # 3. Call self._notify_on_data() to let application know data needs to be read
        self._notify_on_data()

    @classmethod
    def create_packet(cls, src: str, sport: int, dst: str, dport: int,
            data: bytes=b'') -> bytes:
        pkt = b''
        ''' Creating IP header:
              TTL - Default value of 64
              Length - Length of IP Datagram [IP header len. + data len.]
              Protocol - Next headers' associated proto. value [next header -> UDP: 17]
              Checksum - Default value of 0
              Src addr - Source address from function arg [src]
              Dst addr - Destination address from function arg [dst]
        '''
        ip_datagram_len = UDPIP_HEADER_LEN + len(data)


        ip_hdr_obj = IPv4Header(ip_datagram_len, 64, IPPROTO_UDP, 0, src, dst)
        pkt += ip_hdr_obj.to_bytes()


        ''' Creating UDP header:
              Src port - Source port from this socket [sport]]
              Dst port - Destination port from function arg [dport]
              Length -  Length of UDP Datagram [UDP header len. + data len.]
              Checksum - Default value of 0
        '''
        udp_datagram_length = UDP_HEADER_LEN + len(data)
        udp_hdr_obj = UDPHeader(sport, dport, udp_datagram_length, 0)
        pkt += udp_hdr_obj.to_bytes()

        pkt += data # Add the data stream after headers

        return pkt

    def send_packet(self, remote_addr: str, remote_port: int,
            data: bytes) -> None:
        pkt = self.create_packet(self._local_addr, self._local_port, remote_addr, remote_port, data)
        self._send_ip_packet(pkt) # TODO: figure out if pkt the only arg to send

    def recvfrom(self) -> tuple[bytes, str, int]:
        return self.buffer.pop(0)

    def sendto(self, data: bytes, remote_addr: str, remote_port: int) -> None:
        self.send_packet(remote_addr, remote_port, data)


class TCPSocketBase:
    def handle_packet(self, pkt: bytes) -> None:
        pass

class TCPListenerSocket(TCPSocketBase):
    def __init__(self, local_addr: str, local_port: int,
            handle_new_client_func: callable, send_ip_packet_func: callable,
            notify_on_data_func: callable) -> TCPListenerSocket:

        # These are all vars that are saved away for instantiation of TCPSocket
        # objects when new connections are created.
        self._local_addr = local_addr
        self._local_port = local_port
        self._handle_new_client = handle_new_client_func

        self._send_ip_packet_func = send_ip_packet_func
        self._notify_on_data_func = notify_on_data_func

   

    def handle_packet(self, pkt: bytes) -> None:
        ip_hdr = IPv4Header.from_bytes(pkt[:IP_HEADER_LEN])
        tcp_hdr = TCPHeader.from_bytes(pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN])
        data = pkt[TCPIP_HEADER_LEN:]

        if tcp_hdr.flags & TCP_FLAGS_SYN:
            sock = TCPSocket(self._local_addr, self._local_port,
                    ip_hdr.src, tcp_hdr.sport,
                    TCP_STATE_LISTEN,
                    send_ip_packet_func=self._send_ip_packet_func,
                    notify_on_data_func=self._notify_on_data_func)

            self._handle_new_client(self._local_addr, self._local_port,
                    ip_hdr.src, tcp_hdr.sport, sock)

            sock.handle_packet(pkt)


class TCPSocket(TCPSocketBase):
    def __init__(self, local_addr: str, local_port: int,
            remote_addr: str, remote_port: int, state: int,
            send_ip_packet_func: callable,
            notify_on_data_func: callable) -> TCPSocket:

        # The local/remote address/port information associated with this
        # TCPConnection
        self._local_addr = local_addr
        self._local_port = local_port
        self._remote_addr = remote_addr
        self._remote_port = remote_port

        # The current state (TCP_STATE_LISTEN, TCP_STATE_CLOSED, etc.)
        self.state = state

        # Helpful methods for helping us send IP packets and
        # notifying the application that we have received data.
        self._send_ip_packet = send_ip_packet_func
        self._notify_on_data = notify_on_data_func

        # Base sequence number
        self.base_seq_self = self.initialize_seq()

        # Base sequence number for the remote side
        self.base_seq_other = None


    @classmethod
    def connect(cls, local_addr: str, local_port: int,
            remote_addr: str, remote_port: int,
            send_ip_packet_func: callable,
            notify_on_data_func: callable) -> TCPSocket:
        sock = cls(local_addr, local_port,
                remote_addr, remote_port,
                TCP_STATE_CLOSED,
                send_ip_packet_func, notify_on_data_func)

        sock.initiate_connection()

        return sock


    def handle_packet(self, pkt: bytes) -> None:
        ip_hdr = IPv4Header.from_bytes(pkt[:IP_HEADER_LEN])
        tcp_hdr = TCPHeader.from_bytes(pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN])
        data = pkt[TCPIP_HEADER_LEN:]

        if self.state != TCP_STATE_ESTABLISHED:
            self.continue_connection(pkt)

        if self.state == TCP_STATE_ESTABLISHED:
            if data:
                # handle data
                self.handle_data(pkt)
            if tcp_hdr.flags & TCP_FLAGS_ACK:
                # handle ACK
                self.handle_ack(pkt)


    def initialize_seq(self) -> int:
        return random.randint(0, 65535)


    def initiate_connection(self) -> None:
        # TODO: complete for Lab 1:: Part 3

        # 1. 


        # 2. 


        # 3.

        pass
    

    ''' Helper function to parse headers and data from a packet.
    @Type pkt: 
    @param pkt: 
    
    @Rtype: Tuple[bytes, bytes, bytes]
    @Return: A tuple consisting of IP header, TCP header, and raw data byte streams in order.
    '''
    def parse_packet(self, pkt: bytes) -> tuple(bytes, bytes, bytes):
        # TODO: flesh out helper function
        ip_hdr = pkt[:IP_HEADER_LEN]
        tcp_hdr = pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN]
        data = pkt[TCPIP_HEADER_LEN:]

        return ip_hdr, tcp_hdr, data
        
    ''' 
      Reference(s)
        1) CLASS LECTURE // Lecture 07: TCP (slide 19-25)
        2) 

      Question(s)
        Q: When do we start to care to send NACKs, if a packet was a not received?
        A: 

        Q:
    
    '''
    def handle_syn(self, pkt: bytes) -> None:
        '''
        Flow 1: This is the first packet sent... 
                    Host A (client) -> Host B (server)
      
        '''
        # 1. Parse the packet for headers and data
        # ip_hdr, tcp_hdr, data = self.parse_packet(pkt)
  
        ip_hdr = pkt[:IP_HEADER_LEN]
        tcp_hdr = pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN]
        data = pkt[TCPIP_HEADER_LEN:]

        ip_hdr_obj = IPv4Header.from_bytes(ip_hdr)
        tcp_hdr_obj = TCPHeader.from_bytes(tcp_hdr)

        tcp_flag = tcp_hdr_obj.flags
        tcp_seq = tcp_hdr_obj.seq

        # 2. Check if SYN was sent in flags
        # 3. Set remote-side base seq of this class to TCP header seqno, 
        # 4. Send this packet through this class's send_packet, using 
        #    seq--ack--flags specified in prompt AND this packet's parsed data
        # 5. Set state to SYN_RECEIVED to indicate Host B (server) received Host A's SYN

        if tcp_flag & TCP_FLAGS_SYN: # Bitwise check if 2nd bit from right is "lit" up
            self.base_seq_other = tcp_seq
            syn_ack = TCP_FLAGS_ACK | TCP_FLAGS_SYN # Combined bit at 2nd pos. from right and 5th pos from right (i.e 0x12)
            self.send_packet(seq=self.base_seq_self, ack=self.base_seq_other + 1, flags=syn_ack, data=data)
            self.state = TCP_STATE_SYN_RECEIVED
        else:
            pass # do nothing is SYN flag was not signified in tcp header of packet
            

    def handle_synack(self, pkt: bytes) -> None:
        '''
        Flow 2: This is the second packet sent...
                      Host B (server) -> Host A (client)
        
        '''
        # 1. Parse the packet for headers and data
        ip_hdr = pkt[:IP_HEADER_LEN]
        tcp_hdr = pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN]
        data = pkt[TCPIP_HEADER_LEN:]

        ip_hdr_obj = IPv4Header.from_bytes(ip_hdr)
        tcp_hdr_obj = TCPHeader.from_bytes(tcp_hdr)

        tcp_ack = tcp_hdr_obj.ack
        tcp_flag = tcp_hdr_obj.flags
        tcp_seq = tcp_hdr_obj.seq

        # 2. Check if SYN AND ACK was sent in flags
        # 3. Set remote-side base seq of this class to TCP header seqno, 
        # 4. Send this packet through this class's send_packet, using 
        #    seq--ack--flags specified in prompt AND this packet's parsed data
        # 5. Set state to SYN_RECEIVED to indicate Host B (server) received Host A's SYN
        
        # Bitwise check if 2nd AND 5th bits from right are "lit" up AND whether tcp's ack is this class' base seqno + 1
        if (tcp_flag & (TCP_FLAGS_SYN | TCP_FLAGS_ACK)) and tcp_ack == self.base_seq_self + 1: 
            self.base_seq_other = tcp_seq
            self.send_packet(seq=self.base_seq_self, ack=self.base_seq_other + 1, flags=TCP_FLAGS_ACK, data=data)
            self.state = TCP_STATE_ESTABLISHED
        else:
            pass # do nothing is SYN and ACK flags was not signified in tcp header of packet

    def handle_ack_after_synack(self, pkt: bytes) -> None:
        '''
         Flow 3: This is the last packet sent... 
                      Host A (client) -> Host B (server)
        
        '''

        ip_hdr = pkt[:IP_HEADER_LEN]
        tcp_hdr = pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN]
        data = pkt[TCPIP_HEADER_LEN:]

        ip_hdr_obj = IPv4Header.from_bytes(ip_hdr)
        tcp_hdr_obj = TCPHeader.from_bytes(tcp_hdr)

        tcp_ack = tcp_hdr_obj.ack
        tcp_flag = tcp_hdr_obj.flags
        tcp_seq = tcp_hdr_obj.seq

        # 2. Check if SYN AND ACK was sent in flags
        # 3. Set remote-side base seq of this class to TCP header seqno, 
        # 4. Send this packet through this class's send_packet, using 
        #    seq--ack--flags specified in prompt AND this packet's parsed data
        # 5. Set state to SYN_RECEIVED to indicate Host B (server) received Host A's SYN
        
        # Bitwise check if 2nd AND 5th bits from right are "lit" up AND whether tcp's ack is this class' base seqno + 1
        if (tcp_flag & TCP_FLAGS_ACK) and tcp_ack == self.base_seq_self + 1: self.state = TCP_STATE_ESTABLISHED
        else: pass # do nothing is SYN and ACK flags was not signified in tcp header of packet

    def continue_connection(self, pkt: bytes) -> None:
        if self.state == TCP_STATE_LISTEN:
            self.handle_syn(pkt)
        elif self.state == TCP_STATE_SYN_SENT:
            self.handle_synack(pkt)
        elif self.state == TCP_STATE_SYN_RECEIVED:
            self.handle_ack_after_synack(pkt)

    def send_data(self, data: bytes, flags: int=0) -> None:
        pass

    @classmethod
    def create_packet(cls, src: str, sport: int, dst: str, dport: int,
            seq: int, ack: int, flags: int, data: bytes=b'') -> bytes:
        pkt = b''
        ''' Creating IP header:
              TTL - Default value of 64
              Length - Length of IP Datagram [IP header len. + data len.]
              Protocol - Next headers' associated proto. value [next header -> UDP: 17]
              Checksum - Default value of 0
              Src addr - Source address from function arg [src]
              Dst addr - Destination address from function arg [dst]
        '''
        ip_datagram_len = IP_HEADER_LEN + len(data)
        ip_hdr_obj = IPv4Header(ip_datagram_len, 64, IPPROTO_UDP, 0, src, dst)
        ''' Creating TCP header:
              Src port - Source port from this socket [sport]]
              Dst port - Destination port from function arg [dport]
              Seq -  current seqno this packet signifies in a stream
              Flags - control bit notifying a SYN or ACK
              Checksum - default value of 0
        '''
        tcp_hdr_obj = TCPHeader(sport=sport, dport=dport, seq=seq, ack=ack, flags=flags, checksum=0)

        # Prepend the header objects in byte form to packet
        pkt +=ip_hdr_obj.to_bytes()
        pkt += tcp_hdr_obj.to_bytes()

        pkt += data # Append the data stream after headers to packet
        return pkt

    def send_packet(self, seq: int, ack: int, flags: int,
            data: bytes=b'') -> None:
        # TODO: complete for Lab 1:: Part 3

        # TODO: figure out how to get params from src to dport..
        pkt = self.create_packet(src=self._local_addr_, sport=self._local_port, dst=self._remote_addr, dport=self._remote_port, seq=seq, ack=ack, flags=flags, data=data)
        self._send_ip_packet(pkt)
      

    def handle_data(self, pkt: bytes) -> None:
        pass

    def handle_ack(self, pkt: bytes) -> None:
        pass
