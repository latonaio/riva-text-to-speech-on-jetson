import numpy as np
import grpc
import riva_api.riva_tts_pb2 as rtts
import riva_api.riva_tts_pb2_grpc as rtts_srv
import riva_api.riva_audio_pb2 as ra
import queue
import threading
import sounddevice as sd
import json5
import pathlib

SAMPLE_RATE = 44100             # Sampling Rate
REQUESTED_DATA_SIZE = 384       # Size of data that can be pronouned at once
text_queue = queue.Queue()      # Queue for text
buffer_queue = queue.Queue()    # Queue for buffer
event = threading.Event()

def callback(outdata, frames, time, status):
    n_samples, n_channels = outdata.shape

    # Get data from queue and play audio
    if not buffer_queue.empty():
        data = buffer_queue.get_nowait()
        for k in range(n_channels):
            outdata[:, k] = data

def get_text():
    while True:
        text = text_queue.get()

        req = rtts.SynthesizeSpeechRequest(
            text = text,
            language_code = "en-US",
            encoding = ra.AudioEncoding.LINEAR_PCM,    # Currently only LINEAR_PCM is supported
            sample_rate_hz = SAMPLE_RATE,              # Generate 44.1KHz audio
            voice_name = "English-US-Female-1"         # The name of the voice to generate
        )
        responses = riva_tts.SynthesizeOnline(req)

        for resp in responses:
            # Process data into the form of audio data
            datalen = len(resp.audio) // 2
            data16 = np.ndarray(buffer=resp.audio, dtype=np.int16, shape=(datalen, 1))
            speech = bytes(data16.data)
            data = np.frombuffer(speech, dtype=np.int16)

            # Put audio data (numpy array) into queue
            for i in range(len(data)//REQUESTED_DATA_SIZE):
                if i == len(data)//REQUESTED_DATA_SIZE:
                    break
                buffer_queue.put_nowait(data[REQUESTED_DATA_SIZE*i:REQUESTED_DATA_SIZE*(i+1)])

def play_audio():
    stream =  sd.OutputStream(
        channels=2, dtype='int16', callback=callback, finished_callback=event.set
    )

    with stream:
        event.wait()

def main():
    flag = True
    t1 = threading.Thread(target=get_text, daemon=True)     # Thread to get text
    t2 = threading.Thread(target=play_audio, daemon=True)   # Thread to play audio
    t1.start()

    while True:
        try:
            text = input(">")
            text_queue.put(text)
            if flag:    # When I get first text
                t2.start()
                flag = False
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break

if __name__ == '__main__':
    p = pathlib.Path('text-to-speech')
    jsn_path = p / 'config' / 'config.json5'
    with open(jsn_path) as f:
        jsn = json5.load(f)

    # Set config
    sd.default.device = jsn['device_id']
    channel = grpc.insecure_channel(jsn['server_address'])
    riva_tts = rtts_srv.RivaSpeechSynthesisStub(channel)

    main()
