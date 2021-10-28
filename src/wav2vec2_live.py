# https://github.com/oliverguhr/wav2vec2-live/blob/main/live_asr.py
# https://github.com/kakaobrain/pororo/blob/7d05a75e8062b00e6b65364b8ec6c52b6293ab07/pororo/models/wav2vec2/recognizer.py
# https://github.com/mozilla/DeepSpeech-examples/blob/r0.9/mic_vad_streaming/mic_vad_streaming.py
# https://github.com/intxcc/pyaudio_portaudio/blob/master/example/echo_python3.py


import pyaudio
import webrtcvad
from wav2vec2_inference import Wave2Vec2Inference
import numpy as np
import time
from multiprocessing import Process, Queue
from scipy import signal
import collections
audio = pyaudio.PyAudio()




class LiveWav2Vec2():
    def __init__(self, ):
        self.deviceIdDict,self.deviceNameDict=self.getDeviceIdDict()  # {deviceId: deviceName},{deviceName:deviceId}
        self.asr_output_queue = Queue()
        self.asr_input_queue = Queue()


    def start(self,model_name,device_id,useCuda=False):
        """start the asr process"""
        self.asr_process  = Process(target=LiveWav2Vec2.asr_process, args=(
                model_name, useCuda, self.asr_input_queue, self.asr_output_queue,))
        self.vad_process  = Process(target=LiveWav2Vec2.vad_process, args=(
                device_id, self.deviceIdDict, self.asr_input_queue,))
        self.asr_process.daemon=True
        self.vad_process.daemon=True
        self.asr_process.start()
        self.vad_process.start()


    def changeDevice(self,device_id):
        self.vad_process.terminate()
        self.vad_process  = Process(target=LiveWav2Vec2.vad_process, args=(
                device_id, self.deviceIdDict, self.asr_input_queue,))
        self.vad_process.daemon=True
        self.vad_process.start()


    def changeModelProcess(self,model_name,useCuda=False):
        self.asr_process.terminate()
        self.asr_process  = Process(target=LiveWav2Vec2.asr_process, args=(
                model_name, useCuda, self.asr_input_queue, self.asr_output_queue,))
        self.asr_process.daemon=True
        self.asr_process.start()





    def getDeviceIdDict(self,):
        deviceIdDict=dict()
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            apiName=audio.get_host_api_info_by_index(info["hostApi"])["name"]
            #microphone
            if "MME" in apiName and info["maxInputChannels"]>0:
                deviceIdDict[info["index"]]="MME_"+info['name']
            #speaker
            if "WASAPI" in apiName and info["maxOutputChannels"]>0:
                deviceIdDict[info["index"]]="WASAPI_"+info['name']

        deviceNameDict = dict((v,k) for k,v in deviceIdDict.items())   #swap key value
        return [deviceIdDict,deviceNameDict]

    def getDefaultDeviceId(self,):
        if len(self.deviceIdDict)==0:
            return -1

        try:
            default_device_index = audio.get_default_input_device_info()["index"]
        except IOError:
            default_device_index = -1

        #if default device is not in available device list, choose from available list
        if default_device_index not in list(self.deviceIdDict.keys()):
            default_device_index=list(self.deviceIdDict.keys())[0]

        return default_device_index












    def asr_process(model_name,useCuda, in_queue, output_queue):
        #get audio
        #get text from audio using wav2vec2 model
        #enque text on output queue
        wave2vec_asr = Wave2Vec2Inference(model_name,useCuda)

        #clear past item
        while not in_queue.empty():
            in_queue.get()

        #process enqueued voice, to enqueue its text
        print("\nlistening to your voice\n")
        output_queue.put(["model loaded",0,0])              #report model loaded
        while True:
            audio_frames = in_queue.get()  # get speech data from vad_process
            float64_buffer = np.frombuffer( audio_frames, dtype=np.int16) / 32767
            start = time.perf_counter()
            text = wave2vec_asr.buffer_to_text(float64_buffer).lower()   #recognise text using model
            inference_time = time.perf_counter()-start
            sample_length = len(float64_buffer) / 16000  # length in sec
            if text != "":
                output_queue.put([text,sample_length,inference_time])




    def vad_process(device_id, deviceIdDict, asr_input_queue):
        #get audio stream from audio device
        #detect voice activity and enque voice part

        def preprocessAudio(data, src_rate,target_rate,src_channel):
            # convert audio to mono channel and 16000 rate
            if src_channel==1 and src_rate==target_rate:
                return data
            #make mono channel
            frames = np.fromstring(string=data, dtype=np.int16)
            frames = np.reshape(frames, (-1, src_channel))   # reshape based on channel
            frames=np.mean(frames,axis=1)  #mean on channel axis
            #resample to 16000
            resample_size = int(len(frames) / src_rate * target_rate)
            frames = signal.resample(frames, resample_size)
            frames = np.array(frames, dtype=np.int16)
            return frames.tostring()

        # get audio stream and detect speech to send model
        def checkSpeech(stream,CHUNK,deviceRate,modelRate,channelcount,asr_input_queue):
            vad = webrtcvad.Vad()
            vad.set_mode(1)
            frames = b''
            while True:
                #get 30ms speech and check is speech
                frame = stream.read(CHUNK)
                frame=preprocessAudio(frame,deviceRate,modelRate,channelcount)
                is_speech = vad.is_speech(frame, modelRate)

                #if speech, record
                if is_speech:
                    frames += frame

                #if non speech, flush
                else:
                    if len(frames) > 0:
                        asr_input_queue.put(frames)
                    frames = b''

        # get audio stream and detect speech to send model with padding
        def checkSpeechWithPadding(stream,CHUNK,FRAME_DURATION,deviceRate,modelRate,channelcount,asr_input_queue):
            # https://github.com/mozilla/DeepSpeech-examples/blob/r0.9/mic_vad_streaming/mic_vad_streaming.py
            # Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            vad = webrtcvad.Vad()
            vad.set_mode(3)
            padding_ms=300
            ratio=0.75
            num_padding_frames = padding_ms // FRAME_DURATION
            ring_buffer = collections.deque(maxlen=num_padding_frames)
            triggered = False
            frames = b''
            while True:
                #get 30ms speech and check is speech
                frame = stream.read(CHUNK)
                frame=preprocessAudio(frame,deviceRate,modelRate,channelcount)
                is_speech = vad.is_speech(frame, modelRate)

                #if speech ratio over 0.75 in previouse 300ms, start record
                if not triggered:
                    ring_buffer.append((frame, is_speech))
                    num_voiced = len([f for f, speech in ring_buffer if speech])
                    if num_voiced > ratio * ring_buffer.maxlen:
                        triggered = True
                        for f, s in ring_buffer:
                            frames += frame
                        ring_buffer.clear()

                #if non speech ratio over 0.75 in previouse 300ms, stop record and flush
                else:
                    frames += frame
                    ring_buffer.append((frame, is_speech))
                    num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                    if num_unvoiced > ratio * ring_buffer.maxlen:
                        triggered = False
                        asr_input_queue.put(frames)
                        frames = b''
                        ring_buffer.clear()




        # A frame must be either 10, 20, or 30 ms in duration for webrtcvad
        FRAME_DURATION = 30
        device_info = audio.get_device_info_by_index(device_id)
        channelcount = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
        deviceRate=int(device_info["defaultSampleRate"])
        modelRate=16000
        CHUNK = int(deviceRate * FRAME_DURATION / 1000)
        useloopback=True if "WASAPI" in deviceIdDict[device_id] else False

        #get audio device stream
        stream = audio.open(input_device_index=device_id,
                            format=pyaudio.paInt16,
                            channels=channelcount,
                            rate=deviceRate,
                            input=True,
                            frames_per_buffer=CHUNK,
                            as_loopback = useloopback)



        # checkSpeech(stream,CHUNK,deviceRate,modelRate,channelcount,asr_input_queue)
        checkSpeechWithPadding(stream,CHUNK,FRAME_DURATION,deviceRate,modelRate,channelcount,asr_input_queue)









if __name__ == "__main__":
    print("Live ASR")

    asr = LiveWav2Vec2()
    deviceId=asr.getDefaultDeviceId()
    print(asr.deviceIdDict)
    print(deviceId)
    deviceId = int(input("Choose device [" +   str(deviceId) +   "]: ") or deviceId)
    print(asr.deviceIdDict[deviceId])
    asr.start("wav2vec2_large_xlsr_japanese_hiragana",deviceId,useCuda=False)

    while True:
        text,sample_length,inference_time = asr.asr_output_queue.get()
        print(f"{sample_length:.3f}s\t{inference_time:.3f}s\t{text}")
