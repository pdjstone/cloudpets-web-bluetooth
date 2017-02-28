# CloudPets Web Bluetoooth Demo

So news just broke about the CloudPets server [being hacked and ransomed](https://www.troyhunt.com/data-from-connected-cloudpets-teddy-bears-leaked-and-ransomed-exposing-kids-voice-messages/). I discovered this delightful product a few months ago after detecting one with our [RaMBLE](https://play.google.com/store/apps/details?id=com.contextis.android.BLEScanner&hl=en_GB) Bluetooth LE scanner. I've been looking at the Bluetooth LE functionality of the toy. The code in this repository uses the new Web Bluetooth feature in Chrome to demonstrate various features of the toy:

1. Upload audio to the toy
2. Trigger playback of uploaded audio
3. Remotely trigger recording functionality
4. Download recorded audio

The toy has 5 audio 'slots'. Each slot can store around 40 seconds of audio. The toy itself always records to slot 1.

## Python Server
The audio encoding/decoding functionality is done using a small Python Flask server. It uses ctypes to call into two native ARM libraries taken from the CloudPets APK to compress and decompress the audio. Since the libraries are native Android ARM binaries, the best place to run the server is on an Android device. You'll need to extract the libraries youself from the CloudPets APK and place them into the libs directory. I recommend using the excellent [Termux](https://termux.com/) Android app.

Once you've installed Termux run the following commands in its terminal:

```
apt install python git
pip install flask
git clone https://github.com/pdjstone/cloudpets-web-bluetooth.git
cd cloudpets-web-ble
python cloudpets_server.python
```

Then open Chrome, and navigate to http://localhost:5000

## Bugs and Notes

The code uses Chrome's new Web Bluetooth API to communicate with the toy. I've tested the code in Chrome for Android and on a Chromebook. The audio download functionality doesn't work in Chrome due to a [bug](https://bugs.chromium.org/p/chromium/issues/detail?id=647673). 
The toy uses Bluetooth LE, not classic Bluetooth therefore the it's fairly slow to upload and download the audio (it can take up to 30-40s for longer audio clips)

