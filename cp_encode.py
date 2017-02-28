import wave
import array
import sys
import subprocess
from binascii import unhexlify, hexlify
from ctypes import CDLL, c_int, c_ubyte, c_short, c_uint8

enclib = CDLL('./libs/libAudio32Encoder.so')

CHUNK_SIZE = 320
FLOATARRAY_TYPE = c_ubyte*(CHUNK_SIZE*2)

def get_file_header(sample_rate: int, frames: int, words_per_frame: int):
    a = array.array('H')
    a.append(0x5541) # 'AU'
    a.append(sample_rate)
    a.append(1600)
    a.append(1)
    a.append(frames)
    a.append(0)
    a.append(frames * words_per_frame)
    return a.tobytes() + unhexlify('0000000000000000000000001000ffffffff')

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def open_wav(filename: str) -> wave.Wave_read:
    wav = wave.open(filename, 'rb')
    wav_params = wav.getparams()
    assert wav_params.framerate == 16000
    assert wav_params.sampwidth == 2
    assert wav_params.nchannels == 1
    return wav

def iter_wav_data(wav: wave.Wave_read, chunk_size: int, min_padding=0):
    wav.rewind()
    nchunks = wav.getnframes() // chunk_size
    for n in range(0, nchunks):
        d = wav.readframes(chunk_size)
        if len(d) < chunk_size:
            d += b'\0\0' * (chunk_size - len(d))
        a =  array.array('h')
        a.frombytes(d)
        yield a
    if min_padding:
        a =  array.array('h')
        a.frombytes(b'\0\0'*min_padding)
        yield a

def encode_ogg(fd):
    with open('oggfile.ogg', 'wb') as f:
        f.write(fd.read())
    subprocess.run(['ffmpeg', '-y', '-i', 'oggfile.ogg', '-acodec', 'pcm_s16le', '-ar', '16000', 'out.wav'])
    wav = open_wav('out.wav')
    data = encode_audio(wav)
    with open('au/encoded.au', 'wb') as f:
        f.write(data)
    return 'au/encoded.au'

def encode_audio(wav: wave.Wave_read) -> bytes:
    
    print('audio_encode_init {} {}'.format(wav.getframerate(), wav.getframerate() // 50))
    enclib.audio_encode_init(c_int(wav.getframerate()))
    
    words_per_frame = c_int.in_dll(enclib, 'gl_number_of_16bit_words_per_frame').value
    in_data = FLOATARRAY_TYPE()
    data = bytearray()
    nn = 0
    #print(FLOATARRAY_TYPE.from_buffer_copy)
    for n, c in enumerate(iter_wav_data(wav, CHUNK_SIZE, CHUNK_SIZE)):
        for i, s in enumerate(c):
            in_data[i*2] = s & 0xff
            in_data[i*2+1] = s >> 8
        gl_history = (c_uint8 * 640).in_dll(enclib, 'gl_history')
        if n == 0:
            print('gl_history={}'.format(hexlify(gl_history)))
        result = enclib.audio_encode(in_data)  
        gl_out_words = (c_uint8 * (words_per_frame * 2)).in_dll(enclib, 'gl_out_words')
        gl_mlt_coefs = (c_uint8 * 640).in_dll(enclib, 'gl_mlt_coefs')
        gl_history = (c_uint8 * 640).in_dll(enclib, 'gl_history')
        gl_mag_shift = c_int.in_dll(enclib, 'gl_mag_shift').value
        #print('gl_mag_shift={}'.format(gl_mag_shift))
        #if nn < 2:
            #print('gl_mlt_coefs={}'.format(hexlify(gl_mlt_coefs)))
            #print('gl_history={}'.format(hexlify(gl_history)))
            #print("in_data: len={} {}".format(len(in_data), hexlify(in_data)))
            #print("out_data: len={} {}".format(len(gl_out_words), hexlify(gl_out_words)))
        data.extend(gl_out_words[:])
        nn += 1
    #print('nn: {}'.format(nn))
    nframes = c_int.in_dll(enclib, 'gl_frame_cnt').value
    
    print('nframes: {} words_per_frame: {}'.format(nframes, words_per_frame))
    header = get_file_header(sample_rate=wav.getframerate(), frames = nframes, words_per_frame = words_per_frame)
    print('data len: {}'.format(len(data)))
    return header + data

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: {} infile outfile.wav'.format(sys.argv[0]))
        exit()
    infile = sys.argv[1]
    outfile = sys.argv[2]

    wav = open_wav(infile)
    data = encode_audio(wav)
    with open(outfile, 'wb') as f:
        f.write(data)
