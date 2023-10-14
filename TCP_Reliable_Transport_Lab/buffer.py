class TCPSendBuffer(object):
    def __init__(self, seq: int):
        self.buffer = b''
        self.base_seq = seq
        self.next_seq = self.base_seq
        self.last_seq = self.base_seq

    def bytes_not_yet_sent(self) -> int:
        return self.last_seq - self.next_seq

    def bytes_outstanding(self) -> int:
        return self.next_seq - self.base_seq

    def put(self, data: bytes) -> int:
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
          unsent_bytes = self.buffer[eqv_next_seq:eqv_last_seq]
          self.next_seq = self.last_seq       
        else:
          unsent_bytes = self.buffer[eqv_next_seq:eqv_next_seq+ size]
          self.next_seq += size
  
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
          unack_bytes = self.buffer[eqv_base_seq:eqv_next_seq]
        else:
          unack_bytes = self.buffer[eqv_base_seq:eqv_base_seq + size]

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

    '''
      Question(s):
      
        Q: Would there be a regualar case, as stated below? (i.e passed all early checks)
        A:

        Q: Would we we return from these early checks? If not, are we to enclose each in else-if logic? Now, if we 
           do that, would it be necessary to follow up the stitching after just regular case or from any?
        A: 


        Q: Regarding the higher level understand of receive buffer, when is the buffer "ready"?
           Is it when just the initial "hole" from base has been filled? OR is it when every "hole"
           is filled? 
           
           If either case, do we need update the base_seq num to comply w/ "hole" conundrum
           AND to satisfy other early checks for next data that gets processed?

           (Ref. to Case 2 (Edge) extra measure comment)
           (Ref. to )
        A: 


        Q: Wouldn't we need to check Case 3 (Edge) within case two, before we update the buffer at 
           the base seqno with data's remaining bytes? Essentially checking if data at base exist already,
           then pick the larger of the two?
           - This is assuming that we are NOT updating the base_seq, determined from question prior to this.
        A: 

    
    '''
    def put(self, data: bytes, sequence: int) -> None:
        
        # TODO: see if self.buffer is what we are to use
        data_map = {} # Key: seqno -> int | Value: data -> bytes

        eqv_base_seq = 0
        eqv_seq = abs(sequence - self.base_seq) # absolute in 
        data_sz = len(data)

        
        # Case 1: (EDGE) handle_data sending in old data to put in receive buffer
        if sequence + data_sz < self.base_seq: # 
          return
      
        # Case 2: (EDGE) handle_data sending in data where some bytes in beginning are old, remaining are new
        if sequence < self.base_seq and sequence + data_sz >= self.base_seq:
          # TODO: determine if extra measure needed if we realize that the beginning "hole" starting from base been filled
          adj_data_base = self.base_seq - sequence 
          self.buffer[self.base_seq] = data[adj_data_base:data_sz] # Store under base_seq since we trim for remaining bytes over base
          return 
        
        # Case 3: (EDGE) handle_data sends in duplicate sequence number
        if self.buffer.get(sequence) is not None:
           # Choose longer segment between existing & incoming
           existing_seg = self.buffer.get(sequence)
           self.buffer[sequence] = data if data_sz > len(existing_seg) else existing_seg
           return
        

        # Case 4: (REGULAR) handle_data sends in a new stream of data w/ non-conflicting seqno 
        self.buffer[sequence] = data

        

        buff_items = [(key, val) for key, val in self.buffer.items()] # Retrieve list of sequence<->segment pairs
        buff_items.sort(key=lambda pair: pair[0]) # Sort by sequence numbers

        for i, seg_pair in enumerate(buff_items):
          curr_seqno, curr_segment = seg_pair
          curr_sz = len(curr_segment)
          
          if i != 0: # Ensure we have a previous segment to check
            prev_seqno, prev_segment  = buff_items[i - 1]
            prev_sz = len(prev_segment)

            if prev_seqno + prev_sz >= curr_seqno: # There is at least 1 duplicate byte starting w/ current seqno & beyond

              # Case 1: prev segment engulfs the whole current (i.e all of current segment is duplicated)
              if prev_seqno + prev_sz == curr_seqno + curr_sz:
                 # TODO: figure out 1)if this check is needed and 2)how to handle it

                 return
              
              # Case 2: Regular duplicated case where NOT all of current segment's bytes are duplicated
              del self.buffer[curr_seqno] # Remove old sequence<->segment pair a
              new_seqno = prev_seqno + prev_sz
              new_eqv_seqno = new_seqno - curr_seqno # Compute updated start sequence
              new_curr_segment = curr_segment[new_eqv_seqno:curr_sz] # Trim duplicated bytes from current segment
              self.buffer[new_seqno] = new_curr_segment # Populate updated segment w/ new seqno in buffer!


    def get(self) -> tuple[bytes, int]:
        pass
