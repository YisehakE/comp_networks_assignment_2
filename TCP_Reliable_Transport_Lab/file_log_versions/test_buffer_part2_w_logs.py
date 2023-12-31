    


import binascii
import unittest

from buffer import TCPSendBuffer, TCPReceiveBuffer


class TestBuffer(unittest.TestCase):

    def test_send_buffer(self):
      buf = TCPSendBuffer(1057)

      print("---------------------------------------------------------------")
      print("                        Initial utility Tests")
      print("---------------------------------------------------------------")
      self.assertEqual(buf.buffer, b'')
      self.assertEqual(buf.base_seq, 1057)
      self.assertEqual(buf.next_seq, 1057)
      self.assertEqual(buf.last_seq, 1057)
      self.assertEqual(buf.bytes_outstanding(), 0)
      self.assertEqual(buf.bytes_not_yet_sent(), 0)
      print("---------------------------------------------------------------")
      print("                        Utility tests passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")
      

      print("---------------------------------------------------------------")
      print("                        1st set 'PUT' Tests")
      print("---------------------------------------------------------------")
      buf.put(b'abcdefg')
      self.assertEqual(buf.buffer, b'abcdefg')
      self.assertEqual(buf.base_seq, 1057)
      self.assertEqual(buf.next_seq, 1057)
      self.assertEqual(buf.last_seq, 1064)
      self.assertEqual(buf.bytes_outstanding(), 0)
      self.assertEqual(buf.bytes_not_yet_sent(), 7)

      print("---------------------------------------------------------------")
      print("                        1st set 'PUT' passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")
      

      print("---------------------------------------------------------------")
      print("                        2nd set 'PUT'Tests")
      print("---------------------------------------------------------------")
      buf.put(b'hijk')
      self.assertEqual(buf.buffer, b'abcdefghijk')
      self.assertEqual(buf.base_seq, 1057)
      self.assertEqual(buf.next_seq, 1057)
      self.assertEqual(buf.last_seq, 1068)
      self.assertEqual(buf.bytes_outstanding(), 0)
      self.assertEqual(buf.bytes_not_yet_sent(), 11)

      print("---------------------------------------------------------------")
      print("                        2nd set 'PUT' passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")



      print("---------------------------------------------------------------")
      print("                        1st set 'GET' Tests")
      print("---------------------------------------------------------------")
      data, seq = buf.get(4)
      self.assertEqual(data, b'abcd')
      self.assertEqual(seq, 1057)
      self.assertEqual(buf.buffer, b'abcdefghijk')
      self.assertEqual(buf.base_seq, 1057)
      self.assertEqual(buf.next_seq, 1061)
      self.assertEqual(buf.last_seq, 1068)
      self.assertEqual(buf.bytes_outstanding(), 4)
      self.assertEqual(buf.bytes_not_yet_sent(), 7)

      print("---------------------------------------------------------------")
      print("                        1st set 'GET' passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")

      print("---------------------------------------------------------------")
      print("                        2nd set 'GET' Tests")
      print("---------------------------------------------------------------")
      data, seq = buf.get(4)
      self.assertEqual(data, b'efgh')
      self.assertEqual(seq, 1061)
      self.assertEqual(buf.buffer, b'abcdefghijk')
      self.assertEqual(buf.base_seq, 1057)
      self.assertEqual(buf.next_seq, 1065)
      self.assertEqual(buf.last_seq, 1068)
      self.assertEqual(buf.bytes_outstanding(), 8)
      self.assertEqual(buf.bytes_not_yet_sent(), 3)

      print("---------------------------------------------------------------")
      print("                        2nd set 'GET' passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")


      print("---------------------------------------------------------------")
      print("                         'SLIDE' Testss")
      print("---------------------------------------------------------------")
      buf.slide(1061)
      self.assertEqual(buf.buffer, b'efghijk')
      self.assertEqual(buf.base_seq, 1061)
      self.assertEqual(buf.next_seq, 1065)
      self.assertEqual(buf.last_seq, 1068)
      self.assertEqual(buf.bytes_outstanding(), 4)
      self.assertEqual(buf.bytes_not_yet_sent(), 3)
      print("---------------------------------------------------------------")
      print("                         'SLIDE' tests passed!")
      print("---------------------------------------------------------------")

      print("---------------------------------------------------------------")
      print("                        'GET_RESEND' Tests")
      print("---------------------------------------------------------------")
      data, seq = buf.get_for_resend(4)
      self.assertEqual(data, b'efgh')
      self.assertEqual(seq, 1061)
      self.assertEqual(buf.buffer, b'efghijk')
      self.assertEqual(buf.base_seq, 1061)
      self.assertEqual(buf.next_seq, 1065)
      self.assertEqual(buf.last_seq, 1068)
      self.assertEqual(buf.bytes_outstanding(), 4)
      self.assertEqual(buf.bytes_not_yet_sent(), 3)
      print("---------------------------------------------------------------")
      print("                        'GET_RESEND' passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")


      print("---------------------------------------------------------------")
      print("                        Final 'GET' Tests")
      print("---------------------------------------------------------------")
      data, seq = buf.get(4)
      self.assertEqual(data, b'ijk')
      self.assertEqual(seq, 1065)
      self.assertEqual(buf.buffer, b'efghijk')
      self.assertEqual(buf.base_seq, 1061)
      self.assertEqual(buf.next_seq, 1068)
      self.assertEqual(buf.last_seq, 1068)
      self.assertEqual(buf.bytes_outstanding(), 7)
      self.assertEqual(buf.bytes_not_yet_sent(), 0)
      print("---------------------------------------------------------------")
      print("                        Final 'GET' passed!")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")

      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")
      print("---------------------------------------------------------------")
      print("                        ALL PASSED")
      print("---------------------------------------------------------------")


    def test_receive_buffer(self):
        buf = TCPReceiveBuffer(2021)

        print("---------------------------------------------------------------")
        print("                        1st set of 'PUT'\n|Ex. from 'PUT' prompt| 3 chunks(1 regular, 1 stitch, 1 regular)")
        print("---------------------------------------------------------------")
        # put three chunks in buffer
        buf.put(b'fghi', 2026)
        buf.put(b'def', 2024)
        buf.put(b'mn', 2033)
        self.assertEqual(buf.buffer,
                {2024: b'def', 2027: b'ghi', 2033: b'mn'})
        self.assertEqual(buf.base_seq, 2021)
        print("---------------------------------------------------------------")
        print("                        1st set 'PUT' passed!")
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")


        print("---------------------------------------------------------------")
        print("                        2nd set of 'PUT'\n|Ex. from 'PUT' prompt| existing sequence is longer")
        print("---------------------------------------------------------------")
        # ignore a chunk starting with the same sequence number if the existing
        # chunk is longer
        buf.put(b'm', 2033)
        self.assertEqual(buf.buffer,
                {2024: b'def', 2027: b'ghi', 2033: b'mn'})
        self.assertEqual(buf.base_seq, 2021)
        print("---------------------------------------------------------------")
        print("                        2nd set 'PUT' passed!")
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("                        3rd set of 'PUT'\n|Ex. from 'PUT' prompt| existing sequence is shorter")
        print("---------------------------------------------------------------")
        # overwrite a chunk starting with the same sequence number if the
        # existing chunk is shorter
        buf.put(b'mno', 2033)
        self.assertEqual(buf.buffer,
                {2024: b'def', 2027: b'ghi', 2033: b'mno'})
        self.assertEqual(buf.base_seq, 2021)
        print("---------------------------------------------------------------")
        print("                        3rd set 'PUT' passed!")
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("*******************************************************************************************************************")

        print("---------------------------------------------------------------")
        print("                        1st set of 'GET'\n|Ex. from 'GET' prompt| No ready segments from the jump")
        print("---------------------------------------------------------------")
        # try to get ready data; none is ready because initial bytes are
        # missing
        data, start = buf.get()
        self.assertEqual(data, b'')
        self.assertEqual(buf.base_seq, 2021)
        print("---------------------------------------------------------------")
        print("                        1st set 'GET' passed!") 
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("                        2nd set of 'GET' | 4th set of 'PUT'\n|Ex. from 'GET' prompt| Fill in inital hole")
        print("---------------------------------------------------------------")
        # add missing data
        buf.put(b'abc', 2021)
        self.assertEqual(buf.buffer,
                {2021: b'abc', 2024: b'def', 2027: b'ghi', 2033: b'mno'})
        self.assertEqual(buf.base_seq, 2021)
        print("---------------------------------------------------------------")
        print("                        2nd/4th set 'GET'/'PUT' passed!") 
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("                        3rd set of 'GET'\n|Ex. from 'GET' prompt| Retrieve ready set after initial fill")
        print("---------------------------------------------------------------")
        # get ready data
        data, start = buf.get()
        self.assertEqual(data, b'abcdefghi')
        self.assertEqual(start, 2021)
        self.assertEqual(buf.base_seq, 2030)
        self.assertEqual(buf.buffer,
                {2033: b'mno'})
        print("---------------------------------------------------------------")
        print("                        3rd set 'GET' passed!") 
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("                        4th set of 'GET' | 5th set of 'PUT'\n| Handling old data case")
        print("---------------------------------------------------------------")
        # make sure buffer does not accept data with seq number lower
        # than base seq
        buf.put(b'abc', 2021)
        self.assertEqual(buf.base_seq, 2030)
        self.assertEqual(buf.buffer,
                {2033: b'mno'})
        print("---------------------------------------------------------------")
        print("                        4th/5th set 'GET'/'PUT' passed!") 
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("                        4th set of 'GET' | 6th set of 'PUT'\n Regular addition of new data")
        print("---------------------------------------------------------------")
        # add missing data
        buf.put(b'jkl', 2030)
        self.assertEqual(buf.buffer,
                {2030: b'jkl', 2033: b'mno'})
        print("---------------------------------------------------------------")
        print("                        4th/6th set 'GET/'PUT' passed!") 
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

        print("---------------------------------------------------------------")
        print("                        5th set of 'GET' \n Retrieve ready set after multiple additions/fills/etc")
        print("---------------------------------------------------------------")
        # get ready data
        data, start = buf.get()
        self.assertEqual(data, b'jklmno')
        self.assertEqual(start, 2030)
        self.assertEqual(buf.base_seq, 2036)
        print("---------------------------------------------------------------")
        print("                        5th set 'GET' passed!") 
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")

if __name__ == '__main__':
    unittest.main()
