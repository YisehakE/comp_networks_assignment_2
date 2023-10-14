from __future__ import annotations

import struct

from cougarnet.util import \
        ip_str_to_binary, ip_binary_to_str


from ipaddress import ip_address
import socket


IP_HEADER_LEN = 20
UDP_HEADER_LEN = 8
TCP_HEADER_LEN = 20
TCPIP_HEADER_LEN = IP_HEADER_LEN + TCP_HEADER_LEN
UDPIP_HEADER_LEN = IP_HEADER_LEN + UDP_HEADER_LEN

TCP_RECEIVE_WINDOW = 64

class IPv4Header:
    def __init__(self, length: int, ttl: int, protocol: int, checksum: int,
            src: str, dst: str) -> IPv4Header:
        self.length = length
        self.ttl = ttl
        self.protocol = protocol
        self.checksum = checksum
        self.src = src
        self.dst = dst



    @classmethod
    def from_bytes(cls, hdr: bytes) -> IPv4Header:
        # TODO: Flesh out for 1) Transport Layer Lab :: part 1 :: step 1
        # TODO: figure out how to break down the bytes according to IPv4 diagram and python struc unpacks

        # hdr - the bytes that are getting streamed in
        # Python Struct functionality: https://docs.python.org/3/library/struct.html
        # H is for 2 bits
        # I is for 4 bits
        # Q is for 8 bits

        length, = struct.unpack('!H', hdr[2:4]) # 16 bits -> 2 bytes
        ttl, = struct.unpack('!B', hdr[8:9]) # 8 bits -> 1 byte
        protocol, = struct.unpack('!B', hdr[9:10]) # 8 bits -> 1 byte
        checksum, = struct.unpack('!H', hdr[10:12]) # 16 bits -> 1 byte

        src, = struct.unpack('!4s', hdr[12:16])
        src_str = str(ip_address(src))

        dst, = struct.unpack('!4s', hdr[16:20])
        dst_str = str(ip_address(dst))        
        return cls(length, ttl, protocol, checksum, src_str, dst_str)
    
    def convert_addr_to_bin(self, addr, type):
        ip_addr_values = addr.split('.')
        addr_bin_stream = b''
        for val in ip_addr_values: 
            val_int = int(val)
            val_bin = struct.pack('!B', val_int)
            addr_bin_stream += val_bin
        return addr_bin_stream
        
    def to_bytes(self) -> bytes:
        hdr = b''

        # Pack 16 bits before "length" (4 bits for version, 4 bits for IHL, 8 bits for diff. service  = 16 total)
          # To fit integers default value 4 and 5 for version and IHL respectively in one byte: 
            # 1) turn 4 & 5 into binary, in respective order 
            # 2) convert that to hex, respectively 
            # 3) convert hex to decimal 
            # 4) pack decimal in one byte
        hdr += struct.pack('!B',  69)
        hdr += struct.pack('!B', 0)
        hdr += struct.pack('!H', self.length)   # 1. Pack 1st attribute -> length (2 bytes)

        # Pack 32 bits before "ttl" (16 bits for id, 3 bits for flags, 13 bits for fragment  = 32 total)
        hdr += struct.pack('!H', 0)
        hdr += struct.pack('!H', 0)
 
        hdr += struct.pack('!B', self.ttl)      # 2. Pack 2nd attribute -> ttl (1 byte)
        hdr += struct.pack('!B', self.protocol) # 3. Pack 3rd attribute -> protocol (1 byte)
        hdr += struct.pack('!H', self.checksum) # 4. Pack 4th  attip_dstribute -> checksum (2 byte)

        src_bin = socket.inet_aton(self.src)
        hdr += src_bin

        dst_bin = socket.inet_aton(self.dst)
        hdr += dst_bin
        return hdr


class UDPHeader:
    def __init__(self, sport: int, dport: int, length: int,
            checksum: int) -> UDPHeader:
        self.sport = sport
        self.dport = dport
        self.checksum = checksum
        self.length = length

    @classmethod
    def from_bytes(cls, hdr: bytes) -> UDPHeader:
        sport, = struct.unpack('!H', hdr[:2]) # a byte is 8 bits, source takes up 2 bytes
        dport, = struct.unpack('!H', hdr[2:4])
        length, = struct.unpack('!H', hdr[4:6])
        checksum, = struct.unpack('!H', hdr[6:8])
        return cls(sport, dport, length, checksum)

    def to_bytes(self) -> bytes:
        hdr = b''
        hdr += struct.pack('!H', self.sport)
        hdr += struct.pack('!H', self.dport)
        hdr += struct.pack('!H', self.length)
        hdr += struct.pack('!H', self.checksum)
        return hdr


class TCPHeader:
    def __init__(self, sport: int, dport: int, seq: int, ack: int,
            flags: int, checksum: int) -> TCPHeader:
        self.sport = sport
        self.dport = dport
        self.seq = seq
        self.ack = ack
        self.flags = flags
        self.checksum = checksum

    @classmethod
    def from_bytes(cls, hdr: bytes) -> TCPHeader:
        src, = struct.unpack('!H', hdr[:2])
        dst, = struct.unpack('!H', hdr[2:4])
        seq, = struct.unpack('!I', hdr[4:8])
        ack, = struct.unpack('!I', hdr[8:12])
        flags, = struct.unpack('!B', hdr[13:14])        
        checksum, = struct.unpack('!H', hdr[16:18])
        return cls(src, dst, seq, ack, flags, checksum)

    def to_bytes(self) -> bytes:
        hdr = b''

        hdr += struct.pack('!H', self.sport)
        hdr += struct.pack('!H', self.dport)
        hdr += struct.pack('!I', self.seq)
        hdr += struct.pack('!I', self.ack)

        # Pack 10 bits before "flags" (4 bits for data offset + 4 bits for reserved + 2 bits ECN = 10 bits total)
          # To fit integers default value 4 and 0 for data offset and reserved respectively in one byte: 
            # 1) turn 4 & 0 into binary, in respective order 
            # 2) convert that to hex, respectively 
            # 3) convert hex to decimal 
            # 4) pack decimal in one byte
        hdr += struct.pack('!B', 80)
        hdr += struct.pack('!B', self.flags) # Since ECN is 0, doesn't need fluff before
        hdr += struct.pack('!H', 64) # Pack 16 bits before "checksum" (16 bits for window  = 16 bits total)
        hdr += struct.pack('!H', self.checksum)
        hdr += struct.pack('!H', 0) # Pack 16 bits after "checksum" (16 bits for urgent pointer  = 16 bits total)
    
        return hdr
