from reedsolomon import ff16, ff4096, rs
import itertools
import string

# max error correction (d-1)/2 errors where d = n-k+1
# So for d = n-k+1 = 134-120+1 = 15
# We can fix (15-1)/2 = 7 errors
# So if we have 134 Z's and we have 127 correct Z's we can reconstruct the original 120 Z's.


# BARCODE error correction
# takes a 12 letter (STD DNA) barcode and returns a 16 letter barcode
# We use GF(16) since RS is limited to n<|GF|. We want n>4 so we use GF(4^2) - every pair of bases are a field element.
# Translate pairs of letters ('AA','AC',...'TG','TT') to integers (0,1,...,14,15)
ff16_trantab = {''.join(vv): i for i, vv in enumerate(itertools.product('ACGT','ACGT'))}
ff16_rev_trantab = {i: vv for vv, i in ff16_trantab.items()}

# RS coder using GF(16) with input message u is a 6 letters (12 DNA letters, every 2 letters = 1 letter for the encoding) and output codeword c is an 8 letters (16 DNA letters)
# n cannot be greter then the alphabet -> therfrore if we look at the alphabet as pairs we would have an alphabet of the size 16. (6*2=12, 8*2=16)
# This is a systematic RS encoding so c[0:6] == u (The redundancy letters are appended as a sufix to u.
barcode_rs_coder = rs.RSCoder(GFint=ff16.GFint, k=6, n=8)
# TODO: change all to parameters.

# encode!
# input = a list of 12 DNA letters we take the input and make it to be pairs [A,T,G,T...] -> [AT,GT,...] -> [0,1,2,...]
# output = a list of 16 DNA letters
# 12 DNA -> 6 pairs -> 6 int ----RS----> 8 int -> 8 pairs -> 16 DNA

def barcode_rs_encode(barcode):
    message = barcode
    # join every pair of letters and translate to int
    message_int = [ff16_trantab[''.join(message[i:i+2])] for i in range(0, len(message), 2)]
    codeword = barcode_rs_coder.encode(message_int)
    # translate every int to a pair of letters and split the pairs (flatten the list)
    coded_barcode = [vv for v in codeword for vv in ff16_rev_trantab[v]]
    return coded_barcode
    
# decode
# input = a list of 16 DNA letters
# output = a list of 12 DNA letters
def barcode_rs_decode(received_barcode, verify_only = True):
    # join every pair of letters and translate to int
    received_int = [ff16_trantab[''.join(received_barcode[i:i+2])] for i in range(0,len(received_barcode),2)]
    if barcode_rs_coder.verify(received_int):
        return received_barcode[0:12]
    if not verify_only:
        decoded_int = barcode_rs_coder.decode(received_int)
        # translate every int to a pair of letters and split the pairs (flatten the list)
        decoded_message = [vv for v in decoded_int for vv in ff16_rev_trantab[v]]
        return decoded_message
    return None


# payload error correction
# takes a 120 letter (From Sigma) message and returns a 150 letter message
# We use GF(4096) although |Sigma|=16c5=4368. Every letter Z in in Sigma is a field element.
# RS coder using GF(4096) with input message u is a 120 letters and output codeword c is a 134 letters
# This is a systematic RS encoding so c[0:120] == u (The redundancy letters are appended as a suffix to u.
# parameters: k = oligo length before RS
# n = oligo length after RS
rs4096_coder = rs.RSCoder(GFint=ff4096.GF4096int,k=120,n=134)
# TODO: change all to parameters. 
# TODO: decide on n,k.

################ Verify with Inbal ####################
alphabet4096 = ['Z{}'.format(i) for i in range(1, 4097)]
################ Verify with Inbal ####################

ff4096_trantab = {l:i for i,l in enumerate(alphabet4096)}# {Z1,Z2,..Z39...} -> {0,1,..,38..}
ff4096_rev_trantab = {i:l for l,i in ff4096_trantab.items()}

# encode!
# input = a list of 120 letters from Sigma
# output = a list of 134 letters from Sigma
def rs4096_encode(payload):
    message = payload
    message_int = [ff4096_trantab[l] for l in message]
    codeword = rs4096_coder.encode(message_int)
    coded_message = [ff4096_rev_trantab[v] for v in codeword]
    return coded_message

# decode
# input = a list of 134 letters from Sigma
# output = a list of 120 letters from Sigma
# We want verify_only = False
def rs4096_decode(received, verify_only = True):
    received_int = [ff4096_trantab[l] for l in received]
    if rs4096_coder.verify(received_int):
        return received[0:120]
    if not verify_only:
        decoded_int = rs4096_coder.decode(received_int)
        decoded_message = [ff4096_rev_trantab[v] for v in decoded_int]
        return decoded_message
    return None