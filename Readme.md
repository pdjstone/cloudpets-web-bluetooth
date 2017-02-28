# CloudPets Web Bluetoooth Demo

Blog post: [Hacking Unicorns with Web Bluetooth](https://www.contextis.com/resources/blog/hacking-unicorns-web-bluetooth/)

The code in this repository uses the new [Web Bluetooth](https://developers.google.com/web/updates/2015/07/interact-with-ble-devices-on-the-web) feature in Chrome to demonstrate various features of the toy:

1. Upload audio to the toy
2. Trigger playback of uploaded audio
3. Remotely trigger recording functionality
4. Download recorded audio
5. Make the heart LED flash

The toy has 5 audio 'slots'. Each slot can store around 40 seconds of audio. The toy itself always records to slot 1.

## Important

For the demo to work, you must be within Bluetooth range of the device (around 10m). I shouldn't have to tell you that you must only connect to a CloudPet toy that you own. Connecting to someone else's one is illegal, so don't do that.

## Live Demo
There's a cut-down [live demo](https://pdjstone.github.io/cloudpets-web-bluetooth/index.html) that can upload and play some pre-recorded audio. The demo doesn't have the server-side component to do the encoding and decoding. But it can upload a couple of pre-encoded clips. It can also trigger the recording (and play it back on the toy itself), and control the LED.
/
## Python Server
The audio encoding/decoding functionality is done using a small Python Flask server. It uses ctypes to call into two native ARM libraries taken from the CloudPets APK to compress and decompress the audio. Since the libraries are native Android ARM binaries, the best place to run the server is on an Android device. You'll need to extract the libraries youself from the CloudPets APK and place them into the libs directory. I recommend using the excellent [Termux](https://termux.com/) Android app.

Once you've installed Termux run the following commands in its terminal:

```
apt install python git
pip install flask
git clone https://github.com/pdjstone/cloudpets-web-bluetooth.git
cd cloudpets-web-bluetooth
python cloudpets_server.py
```

Then open Chrome, and navigate to http://localhost:5000

## Bugs and Notes

* The code uses Chrome's new Web Bluetooth API to communicate with the toy. I've tested the code in Chrome for Android and on a Chromebook. The audio download functionality doesn't work in Chrome for Android due to a [bug](https://bugs.chromium.org/p/chromium/issues/detail?id=647673), but it does work on Chrome OS. 
* The toy uses Bluetooth LE, not classic Bluetooth therefore the it's fairly slow to upload and download the audio (it can take up to 30-40s for longer audio clips)
* The compression/decompression libraries are compiled for 32-bit ARM. To get them working under Termux, you'll unfortunately to run them on a 32-bit Android device. I tried and failed to get a the 32-bit version of Python installed under Termux on a newer phone. If anyone knows how to make it work, please let me know.
