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

    ''''
      Question(s):
      
        Q: Would there be a regualar case, as stated below? (i.e passed all early checks)
        A: [FROM OWN] Yes, or else there would the functionality would work for stitching after otherwise.
        A: [FROM TA/PROF/PEER]

        Q: Would we we return from these early checks? If not, are we to enclose each in else-if logic? Now, if we 
           do that, would it be necessary to follow up the stitching after just regular case or from any?
        A: [FROM OWN TESTING] No, do not return, instead wrap in else-if logic with default as w/out early checks
        A: [FROM TA/PROF/PEER]  


        Q: Regarding the higher level understand of receive buffer, when is the buffer "ready"?
           Is it when just the initial "hole" from base has been filled? OR is it when every "hole"
           is filled? 
           
           If either case, do we need update the base_seq num to comply w/ "hole" conundrum
           AND to satisfy other early checks for next data that gets processed?

           (Ref. to Case 2 (Edge) extra measure comment)
        A: 

            Q: In addition to previous question, if we don't need to update the base_seq, is that b/c
              that responsibility is solely for the GET function below? Why is it split like this
              and wouldn't this allow some unintended errors
            A: 


        Q: Wouldn't we need to check Case 3 (Edge) within case two, before we update the buffer at 
           the base seqno with data's remaining bytes? Essentially checking if data at base exist already,
           then pick the larger of the two?
           - This is assuming that we are NOT updating the base_seq, determined from question prior to this.
        A: 


        Q: Would case 1 in the stitching duplicates check be necessary? What does that even mean
           in terms of processing?
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
      
        if sequence < self.base_seq and sequence + data_sz >= self.base_seq:
          # Case 2: (EDGE) handle_data sending in data where some bytes in beginning are old, remaining are new

          # TODO: determine if extra measure needed if we realize that the beginning "hole" starting from base been filled
          adj_data_base = self.base_seq - sequence 
          self.buffer[self.base_seq] = data[adj_data_base:data_sz] # Store under base_seq since we trim for remaining bytes over base
        elif self.buffer.get(sequence) is not None:
          # Case 3: (EDGE) handle_data sends in sequence number that already exists in buffer

          # Choose longer segment between existing & incoming
          print("Existing case")
          existing_seg = self.buffer.get(sequence)
          print("Existing sequence: ", existing_seg)
          temp= data if data_sz > len(existing_seg) else existing_seg
          print("Larger value: ", temp )
          self.buffer[sequence] = data if data_sz > len(existing_seg) else existing_seg
        else: 
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
              print("Duplicate bytes found!")
              print("Previous seqno, segment, sz: ", prev_seqno, prev_segment, prev_sz)
              print("Current seqno, segment, sz: ", curr_seqno, curr_segment, curr_sz)
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

            print("No duplicates bytes found!")
            print("Previous seqno, segment, sz: ", prev_seqno, prev_segment, prev_sz)
            print("Current seqno, segment, sz: ", curr_seqno, curr_segment, curr_sz)


    '''
      Question(s):
        Q:
        A: 
    
    '''
    def get(self) -> tuple[bytes, int]:
      # 0. Initialize return values
      cont_set = b''
      prev_base_seq = self.base_seq

      # Early check: from the base_seq there's already a hole
      if self.buffer.get(prev_base_seq) is None: return (cont_set, prev_base_seq) 

      # 1. Retrieve buffer items & compile into sorted list 
      buff_items = [item for item in self.buffer.items()] # Retrieve list of sequence<->segment pairs
      buff_items.sort(key=lambda pair: pair[0]) # Sort by sequence numbers

      # 2. Stitch up any duplicates throughout buffer + update continuous set until gap
      for i, seg_pair in enumerate(buff_items):
        curr_seqno, curr_segment = seg_pair
        curr_sz = len(curr_segment)
        if i != 0: # Ensure we have a previous segment to check
          prev_seqno, prev_segment  = buff_items[i - 1]
          prev_sz = len(prev_segment)

          # Case 1: (EDGE) There is a detected gap, return cont_set as is
          if prev_seqno + prev_sz < curr_seqno - 1: # If it was = curr_seqno - 1, then prev & curr segments would have been perfectly continuous
              print("Case 1 here", "\n")
              # self.base_seq = prev_seqno + prev_sz # Update base seqno to end-of-previous segment, i.e start of next "hole"
              print("New base_seq: ", self.base_seq)
              print("Buffer: ", self.buffer, "\n")
              break
          # Case 2: (EDGE) Previous segment overlaps current (i.e duplicates), switching required
          if prev_seqno + prev_sz >= curr_seqno: # Same logic as in PUT
            print("Case 2 here", "\n")
            print("Old buffer: ", self.buffer)

            # TODO: (EDGE) if case 1 check in PUT is needed, it will be needed here as well

            del self.buffer[curr_seqno] # Remove old sequence <-> segment pair for current segment
            new_seqno = prev_seqno + prev_sz # Compute upddate start seq for buffer
            new_eqv_seqno = new_seqno - curr_seqno # Compute updated start seq for array, eqvivalent to actual new sequence above
            new_curr_segment = curr_segment[new_eqv_seqno:curr_sz] # Trim duplicated bytes from current segment
            self.buffer[new_seqno] = new_curr_segment # Populate updated segment w/ new seqno in buffer!

            print("Updated current segment: ", new_curr_segment)
            print("Updated buffer: ", self.buffer)
            
            cont_set += new_curr_segment
            self.base_seq = curr_seqno + curr_sz
            print("Updated cont set: ", cont_set, "\n")
            print("New base_seq: ", self.base_seq)
            
          # Case 3: (REGULAR) Current segment has no gap & no duplicates from/with previous segment... perfectly continuous!
          elif prev_seqno + prev_sz == curr_seqno - 1:
            print("Case 3 here", "\n")
            cont_set += self.buffer[prev_seqno] # TODO: CHANGE!
            print("Buffer: ", self.buffer)
            print("Updated cont set: ", cont_set, "\n")
        else: 
            cont_set += curr_segment
            self.base_seq = curr_seqno + curr_sz
            print("New base_seq: ", self.base_seq)

        # 3. Delete all segments in contiguous set from buffer
      for item in buff_items: 
        if item[0] < self.base_seq: del self.buffer[item[0]] 

      return (cont_set, prev_base_seq)
