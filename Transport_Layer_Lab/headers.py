from __future__ import annotations

import struct

from cougarnet.util import \
        ip_str_to_binary, ip_binary_to_str


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

        print("CODE:: packed length: ", str(hdr[2:4]))
        length, = struct.unpack('!H', hdr[2:4]) # 16 bits -> 2 bytes
        print("CODE:: unpack length: ", str(length))

        print("CODE:: packed ttl: ", str(hdr[8:9]))
        ttl, = struct.unpack('!B', hdr[8:9]) # 8 bits -> 1 byte
        print("CODE:: unpacked ttl: ", str(ttl))

        print("CODE:: packed protocol: ", str(hdr[9:10]))
        protocol, = struct.unpack('!B', hdr[9:10]) # 8 bits -> 1 byte
        print("CODE:: unpacked protocol: ", str(hdr[9:10]))


        print("CODE:: packed checksum: ", str(hdr[10:12]))
        checksum, = struct.unpack('!H', hdr[10:12]) # 16 bits -> 1 byte
        print("CODE:: unpacked protocol: ", str(protocol))

        #TODO: need to convert src and dest to strings in "X.X.X.X" format
        print("CODE:: packed source: ", str(hdr[12:16]))
        src, = struct.unpack('!4s', hdr[12:16])
        print("CODE:: packed source (pre-conv): ", str(src))


        src_str = bytes.fromhex(src.hex())
        print("CODE:: src str", src_str)
        
        print("CODE:: packed dest: ", str(hdr[16:20]))
        dest, = struct.unpack('!4s', hdr[16:20])
        print("CODE:: unpacked dest: ",str(dest))

        dest_str = bytes.fromhex(dest.hex())
        print("CODE:: dest str", dest_str)
        
        return cls(length, ttl, protocol, checksum, src, dest)
    
        # return cls(0, 0, 0, 0, '0.0.0.0', '0.0.0.0')

    def to_bytes(self) -> bytes:
        # TODO: 

        hdr = b''
        # TODO: pack 8 bits before "length" (4 bits for version, 4 bits for IHL, 8 bits for diff. service  = 16 total)
        hdr += struct.pack('!H', 16)

        hdr += struct.pack('!H', self.length)

        # TODO: pack 32 bits before "ttl" (16 bits for id, 3 bits for flags, 13 bits for fragment  = 32 total)
        hdr += struct.pack('!H', 32)

        hdr += struct.pack('!H', self.ttl)
        hdr += struct.pack('!H', self.protocol)
        hdr += struct.pack('!H', self.checksum)
        hdr += struct.pack('!H', self.src)
        hdr += struct.pack('!H', self.dst)

        # TODO: pack 32 bits before "ttl" (32 bits for options = 32 total)
        hdr += struct.pack('!H', 32)

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
        # TODO: Flesh out for 1) Transport Layer Lab :: part 1 :: step 1
        # TODO: figure out how to break down the bytes according to TCP diagram and python struc unpacks
        
        # src, = struct.unpack('', hdr[])
        # dst, = struct.unpack('', hdr[])
        # seq, = struct.unpack('', hdr[])

        # ack, = struct.unpack('', hdr[])
        # flags, = struct.unpack('', hdr[])
        # checksum, = struct.unpack('', hdr[])


        # return cls(src, dst, seq, ack, flags, checksum)
        pass
    
        # return cls(0, 0, 0, 0, 0, 0)

    def to_bytes(self) -> bytes:
        
        # TODO: Flesh out for 1) Transport Layer Lab :: part 1 :: step 1


        hdr = b''

        hdr += struct.pack('!H', self.sport)

        hdr += struct.pack('!H', self.dport)

        hdr += struct.pack('!H', self.seq)

        hdr += struct.pack('!H', self.flags)

        hdr += struct.pack('!H', self.checksum)
      

        return hdr
