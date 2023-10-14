class TCPSendBuffer(object):
    def __init__(self, seq: int):
        self.buffer = b''
        self.base_seq = seq
        self.next_seq = self.base_seq
        self.last_seq = self.base_seq

    def bytes_not_yet_sent(self) -> int:
        # TODO: see if there's any edge cases to worry about
        return self.last_seq - self.next_seq

    def bytes_outstanding(self) -> int:
        # TODO: see if there's any edge cases to worry about
        return self.next_seq - self.base_seq

    def put(self, data: bytes) -> int:
        # TODO: flesh out for Part 1: TCP send buffer
        prev_last_seq = self.last_seq
        self.buffer += bytes
        self.last_seq += len(data)
        
        return prev_last_seq # TODO: determine what the return value is 


    ''' 
      Question(s):
        Q: Along with next_seq getting updated, should we be updating last_seq?
        A: 
    
    '''
    def get(self, size: int) -> tuple[bytes, int]:
        
        unsent_bytes = b''
        prev_next_seq = self.next_seq

        if size > len(self.buffer) or self.next_seq + size > self.last_seq:
          unsent_bytes = self.buffer[self.next_seq:self.last_seq]
          self.next_seq = self.last_seq
        else:
          unsent_bytes = self.buffer[self.next_seq:self.next_seq + size]
          self.next_seq += size
      
        return (unsent_bytes, prev_next_seq)
    
    


    ''' 
      Question(s):
        Q: I understand that buffer and base/next seqno remain unchanged, but would last seqno need to get updated for any reason?
        A: 
    
    '''
    def get_for_resend(self, size: int) -> tuple[bytes, int]:
        unack_bytes = b''

        if size > len(self.buffer) or self.base_seq + size > self.next_seq:
          unack_bytes = self.buffer[self.base_seq:self.next_seq]
        else:
          unack_bytes = self.buffer[self.next_seq:self.next_seq + size]
          self.next_seq += size
      
        return (unack_bytes, self.base_seq)
    

    ''' 
      Question(s):
        Q: Are we to treat cases where sequence given either extends beyond end of buffer or next_seq as their own cases?
          (ref. to two checks below)
        A:

        Q: Should we worry above sending a value other than None if sequence given does NOT allow alide? (i.e pass the 2 checks)
        A: 

        Q: Alond with updating base_seq, should we be updating next_seq and/or last_seq?
        A: 

    
    '''

    def slide(self, sequence: int) -> None:
        buff_sz = len(self.buffer)
        if sequence > self.base_seq + buff_sz:
            return 
        
        # TODO: determine if check for sequnce no going beyond next_seq is necessary (if so, uncomment line below)
        if sequence > self.next_seq: 
          self.buffer = self.buffer[self.next_seq:self.base_seq + buff_sz]
          self.base_seq = self.next_seq
          return # TODO: if this check needed, then decide if logic below belongs in else block 
     
        self.buffer = self.buffer[sequence:self.base_seq + buff_sz]
        self.base_seq = sequence


class TCPReceiveBuffer(object):
    def __init__(self, seq: int):
        self.buffer = {}
        self.base_seq = seq

    def put(self, data: bytes, sequence: int) -> None:
        pass

    def get(self) -> tuple[bytes, int]:
        pass
