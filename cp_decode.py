import array
import wave
import sys
from ctypes import *

declib = CDLL('./libs/libMsAdpcm.so')
HEADER_LEN = 32

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def decode_audio(file, wav: wave.Wave_write):
    if type(file) == str:
        with open(file, 'rb') as f:
            data = f.read()
    else:
        data = file.read()

    header = array.array('H', data[:HEADER_LEN])
    sample_rate = header[1]
    print(header)
    declib._MSAdpcm_Init(header[2])

    in_size = c_int.in_dll(declib, 'packet_size').value
    out_size = c_int.in_dll(declib, 'MS_FRMSIZE').value

    IN_TYPE = c_short * in_size
    OUT_TYPE = c_short * out_size

    payload = array.array('h', data[HEADER_LEN:])
    pad_len = in_size - (len(payload) % in_size)
 
    payload.extend([0] * pad_len)
    num_frames = len(payload) // in_size
    inmem = memoryview(payload)
    outmem = array.array('h', bytearray(num_frames * out_size * 2))
    outview = memoryview(outmem)
    outbuf = OUT_TYPE()

    for i, c in enumerate(chunks(inmem, in_size)):
        inbuf = IN_TYPE.from_buffer(c)
        outbuf = OUT_TYPE.from_buffer(outview[i * out_size: i * out_size + out_size])
        declib._MSAdpcm_DecProcessNoHeader1(inbuf, out_size, 0, outbuf)
        #hx = ' '.join(['{:2x}'.format(v) for v in outbuf])
        #print('{}: {}'.format(i, hx))

    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    wav.setnchannels(1)
    wav.setnframes(num_frames)
    wav.writeframes(outmem)
    wav.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: {} infile outfile.wav'.format(sys.argv[0]))
        exit()
    infile = sys.argv[1]
    outfile = sys.argv[2]

    wav = wave.open(outfile, 'wb')
    decode_audio(infile, wav)