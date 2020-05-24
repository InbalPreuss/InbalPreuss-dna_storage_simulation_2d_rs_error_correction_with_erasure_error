import itertools

import numpy as np
from unireedsolomon import rs


class RSBarcodeAdapter:
    def __init__(self, bits_per_z, barcode_len, barcode_rs_len):
        self.bits_per_z = bits_per_z
        self._barcode_len = barcode_len
        alphabet = list(itertools.product('ACGT', 'ACGT'))
        n = int((barcode_len + barcode_rs_len) / 2)
        k = int(barcode_len / 2)
        c_exp = int(np.log2(len(alphabet)))
        prim = 2 ** c_exp
        self._barcode_coder = rs.RSCoder(n=n, k=k, prim=prim, c_exp=c_exp)
        self._barcode_pair_to_int = {''.join(vv): i for i, vv in enumerate(alphabet)}
        self._int_to_barcode_pairs = {i: vv for vv, i in self._barcode_pair_to_int.items()}

    def encode(self, barcode):
        barcode_as_int = [self._barcode_pair_to_int[''.join(barcode[i:i + 2])] for i in range(0, len(barcode), 2)]
        barcode_encoded_as_polynomial = self._barcode_coder.encode(barcode_as_int, return_string=False)
        barcode_encoded = ''.join([self._int_to_barcode_pairs[z] for z in barcode_encoded_as_polynomial])
        return barcode_encoded

    def decode(self, barcode_encoded):
        barcode_encoded_as_int = [self._int_to_barcode_pairs[''.join(barcode_encoded[i:i + 2])] for i in range(0, len(barcode_encoded), 2)]
        if self._barcode_coder.check_fast(barcode_encoded_as_int):
            return barcode_encoded[0:self._barcode_len]
        else:
            barcode = self._barcode_coder.decode_fast(barcode_encoded_as_int)
            return barcode


class RSPayloadAdapter:
    def __init__(self, bits_per_z, payload_len, payload_rs_len):
        self.bits_per_z = bits_per_z
        self.payload_len = payload_len
        alphabet = ['Z{}'.format(i) for i in range(1, 2**bits_per_z+1)]
        n = payload_len + payload_rs_len
        k = payload_len
        c_exp = bits_per_z
        prim = 2 ** c_exp
        self._payload_coder = rs.RSCoder(n=n, k=k, prim=prim, c_exp=c_exp)
        self._payload_to_int = {''.join(vv): i for i, vv in enumerate(alphabet)}
        self._int_to_payload = {i: vv for vv, i in self._payload_to_int.items()}

    def encode(self, payload):
        payload_as_int = [self._payload_to_int[z] for z in payload]
        payload_encoded_as_polynomial = self._payload_coder.encode_fast(payload_as_int, return_string=False)
        payload_encoded = [self._int_to_payload[z] for z in payload_encoded_as_polynomial]
        return payload_encoded

    def decode(self, payload_encoded):
        payload_as_int = [self._payload_to_int[z] for z in payload_encoded]
        if self._payload_coder.check_fast(payload_as_int):
            return payload_encoded[0:self.payload_len]
        else:
            payload = self._payload_coder.decode_fast(payload_as_int)
            return payload


RSWideAdapter = RSPayloadAdapter
