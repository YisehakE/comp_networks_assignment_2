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
        self.buffer += data
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

        eqv_base_seq = 0
        eqv_next_seq = self.next_seq - self.base_seq
        eqv_last_seq = self.last_seq - self.base_seq

        if size > len(self.buffer) or eqv_next_seq + size > eqv_last_seq:
          print("1st case" + "\n")

          print("Buffer: ", self.buffer)
          print("Size of request: ", size, "\n")

          print("Old base seq: ", self.base_seq)
          print("Old eqv base seq: ", eqv_base_seq, "\n")

          print("Old next seq: ", self.next_seq)
          print("Old eqv next seq: ", eqv_next_seq, "\n")
                    
          print("Old last seq: ", self.last_seq)
          print("Old eqv last seq: ", eqv_last_seq, "\n")

          print("End of unsent buffer: ", self.last_seq)
          print("End of eqv unsent buffer: ", eqv_last_seq, "\n")

          unsent_bytes = self.buffer[eqv_next_seq:eqv_last_seq]
          print("Unsent bytes: ", unsent_bytes, "\n")

          self.next_seq = self.last_seq
          print("New next seq num: ", self.next_seq)
          print("New eqv next seq num: ", eqv_last_seq, "\n")          


        else:
          print("2nd case" + "\n")

          print("Buffer: ", self.buffer)
          print("Size of request: ", size, "\n")

          print("Old base seq: ", self.base_seq)
          print("Old eqv base seq: ", eqv_base_seq, "\n")

          print("Old next seq: ", self.next_seq)
          print("Old eqv next seq: ", eqv_next_seq, "\n")
                    
          print("Old last seq: ", self.last_seq)
          print("Old eqv last seq: ", eqv_last_seq, "\n")

          print("End of unsent buffer: ", self.next_seq + size)
          print("End of eqv unsent buffer: ", eqv_next_seq + size, "\n")
          
          unsent_bytes = self.buffer[eqv_next_seq:eqv_next_seq+ size]

          print("Unsent bytes: ", unsent_bytes, "\n")

          self.next_seq += size
          print("New next seq num: ", self.next_seq)
          print("New eqv next seq num: ", eqv_next_seq , "\n")          

      
        return (unsent_bytes, prev_next_seq)
    
    


    ''' 
      Question(s):
        Q: I understand that buffer and base/next seqno remain unchanged, but would last seqno need to get updated for any reason?
        A: 
    
    '''
    def get_for_resend(self, size: int) -> tuple[bytes, int]:
        unack_bytes = b''

        eqv_base_seq = 0
        eqv_next_seq = self.next_seq - self.base_seq
        eqv_last_seq = self.last_seq - self.base_seq

        if size > len(self.buffer) or (eqv_base_seq + size) > eqv_next_seq:
          print("1st case\n")
          print("Buffer: ", self.buffer)
          print("Size of request: ", size, "\n")

          print("Old base seq: ", self.base_seq)
          print("Old eqv base seq: ", eqv_base_seq, "\n")

          print("Old next seq: ", self.next_seq)
          print("Old eqv next seq: ", eqv_next_seq, "\n")
                    

          print("End of sent&unack'ed buffer: ", self.next_seq)
          print("End of eqv sent&unack'ed buffer: ", eqv_next_seq, "\n")
          unack_bytes = self.buffer[eqv_base_seq:eqv_next_seq]

          print("Sent&Unack_bytes: ", unack_bytes, "\n")
        else:
          print("2nd case\n")

          print("Buffer: ", self.buffer)
          print("Size of request: ", size, "\n")

          print("Old base seq: ", self.base_seq)
          print("Old eqv base seq: ", eqv_base_seq, "\n")

          print("Old next seq: ", self.next_seq)
          print("Old eqv next seq: ", eqv_next_seq, "\n")
                    

          print("End of sent&unack'ed buffer: ", self.next_seq + size)
          print("End of eqv sent&unack'ed buffer: ", eqv_next_seq + size, "\n")
          unack_bytes = self.buffer[eqv_base_seq:eqv_base_seq + size]

          print("Sent&Unack_bytes: ", unack_bytes, "\n")
      
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
        
       
        eqv_base_seq = 0
        eqv_next_seq = self.next_seq - self.base_seq
        eqv_last_seq = self.last_seq - self.base_seq

        eqv_seq = sequence - self.base_seq
        buff_sz = len(self.buffer)

        # TODO: determine if this check is needed, 
        if sequence > self.base_seq + buff_sz:
            # TODO: if check needed, determine if we do nothing or we just shift to next_seq like next check
            return 
        
        # TODO: determine if check for sequnce no going beyond next_seq is necessary (if so, uncomment line below)
          # Reason Im asking is that if not checked, then there will be unsent bytes at the end of sent but unack'ed stream
        if sequence > self.next_seq: 
          self.buffer = self.buffer[eqv_next_seq:eqv_base_seq + buff_sz]
          self.base_seq = self.next_seq
          return # TODO: if this check needed, then decide if logic below belongs in else block 
     

        self.buffer = self.buffer[eqv_seq:eqv_base_seq + buff_sz]
        self.base_seq = sequence


class TCPReceiveBuffer(object):
    def __init__(self, seq: int):
        self.buffer = {}
        self.base_seq = seq

    def put(self, data: bytes, sequence: int) -> None:
        pass

    def get(self) -> tuple[bytes, int]:
        pass
