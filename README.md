# Python png2klg converter tools

`I'm fucked with C++, so I write this tool with python.`

## I'm working on ElasticFusion and Kintinuous and want to make it work on my own data.
### Requirements:
```
opencv
numpy
zlib
click
tqdm
```

Just do this:
```
pip install opencv-python numpy click tqdm
```
Maybe you will get many errors, and you need to install zlib, deal with it.


If you just want to use this tool, and the files are organized as below, use the following command:
```
||--png2klg
  ||--rgb_images
  ||--depth_images
  ||timestamps.txt
  ||main.py

python main.py
```
The number of color images and depth images need to be the same.
You can use `python main.py --help` to get help.
For example, you can provide your own image folder path instead of copying the files to this project.
The `timestamps.txt` file is not a must, because refer to https://github.com/mp3guy/ElasticFusion/issues/18, the author says "Unit-less, just make it an increasing count (so frame one has timestamp 1, etc...)."
```
python main.py --depth_path=test/depth --rgb_path=test/rgb
```

If you want to make it work simultaneously with realsense, refer to https://github.com/mp3guy/ElasticFusion/issues/164(I failed with realsense camera L515)

(New: I succeeded with realsense D534i. It works simultaneously with ElasticFusion and the result seems fine.)

## About Realsense(I believe you have already made the camera work)(My camera is L515):
You can refer to https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/align-depth2color.py to get aligned color images and depth images.
I made some changes, you can use command `python get_camera.py` to get aligned images. 

This command will make directories`rgb_images` and `depth_images` to save images and `timestamps.txt` to save timestamps.

I have upload some images in this folder, you can test it with command `python main.py` and you will get `data.klg`. 

You can also directly use the `data.klg`(only 50 frames) for test.

The most import thing when saving depth images is:

`depth_image = cv2.resize((depth_image * depth_scale).astype(np.uint16), (640, 480))`.  To convert depth from m to mm, I don't know why this, but it works(not really...).

### Update:
I have tested with this code above, but seems not work. I really don't know what 'depth scale' this algorithm uses.


You can refer to https://github.com/carlosbeltran/klgparser/issues/1 (My issue) to get more details.

## About Ros(My lab is using ros, so I also want to get .klg file from .bag file):
I didn't write the bag2klg code.
You can use rosbag(just `pip install rosbag`) to parse images from .bag file. Remember to sync the timestamp between color images and depth images.

Then use this tool.

## Ros simultaneously with Elasticfusion?(don't know)

## How to parse images from .klg file?
Please refer to https://github.com/carlosbeltran/klgparser, I learned the klg file protocol and code from this repo.
