import threading
import wave

import pyaudio

class Bell:
    def __init__(self, interface, wave_file, chunk=256):
        self.interface = interface
        self.file = wave.open(wave_file, 'rb')
        self.lock = threading.Lock()
        self.stream = self.interface.open(
                format=self.interface.get_format_from_width(self.file.getsampwidth()),
                channels=self.file.getnchannels(),
                rate=self.file.getframerate(),
                output=True)
        self.stop = False
        self.chunk = chunk

    def play(self):
        self.stop = True
        threading.Thread(target=self._process).start()

    def _process(self):
        with self.lock:
            self.stop = False
            self.file.rewind()
            data = self.file.readframes(self.chunk)
            while len(data) > 0 and (not self.stop):
                self.stream.write(data)
                data = self.file.readframes(self.chunk)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
