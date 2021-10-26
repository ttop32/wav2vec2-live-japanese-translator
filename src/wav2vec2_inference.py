 # https://github.com/oliverguhr/wav2vec2-live/blob/main/live_vad_asr.py
# https://github.com/oliverguhr/wav2vec2-live


#usage
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


class Wave2Vec2Inference():
    def __init__(self,model_name,useCuda=False):
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name)

        if useCuda:
            self.model=self.model.to("cuda")
        self.useCuda=useCuda

    def buffer_to_text(self,audio_buffer):
        if(len(audio_buffer)==0):
            return ""

        inputs = self.processor([audio_buffer], sampling_rate=16_000, return_tensors="pt", padding=True)
        input_values=inputs.input_values
        attention_mask=inputs.attention_mask
        
        if self.useCuda:
            input_values=inputs.input_values.to("cuda")
            attention_mask=inputs.attention_mask.to("cuda")


        with torch.no_grad():
            logits = self.model(input_values, attention_mask=attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0]
        return transcription.lower()

    def file_to_text(self,filename):
        speech_array, sampling_rate = torchaudio.load(filename)
        speech = torchaudio.functional.resample(speech_array, sampling_rate, 16000)[0].numpy()
        return self.buffer_to_text(speech)


if __name__ == "__main__":
    print("Model test")
    asr = Wave2Vec2Inference("wav2vec2_large_xlsr_japanese_hiragana",useCuda=False)
    text = asr.file_to_text("test.wav")
    print(text)
