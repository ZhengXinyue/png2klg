# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import sys
try:
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
except:
    pass
import cv2
import time
import os
import shutil
import zlib

# Create a pipeline
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1  # 1 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

rgb_path = 'rgb_images'
depth_path = 'depth_images'


def check_path():
    if not os.path.exists(rgb_path):
        os.mkdir(rgb_path)
    else:
        shutil.rmtree(rgb_path)
        os.mkdir(rgb_path)
    if not os.path.exists(depth_path):
        os.mkdir(depth_path)
    else:
        shutil.rmtree(depth_path)
        os.mkdir(depth_path)


check_path()
# Streaming loop
try:
    count = 0
    f = open('timestamps.txt', 'w')
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data()).astype(np.float32)
        cv2.namedWindow('Depth Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Depth Image', depth_image)
        color_image = np.asanyarray(color_frame.get_data())
        cv2.namedWindow('Color Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Color Image', color_image)

        color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        color_image = cv2.resize(color_image, (640, 480))
        depth_image = cv2.resize((depth_image * depth_scale).astype(np.uint16), (640, 480))  # must be this
        cv2.imwrite(rgb_path + '/rgb_{0:010d}.png'.format(count), color_image)
        cv2.imwrite(depth_path + '/depth_{0:010d}.png'.format(count), depth_image)
        f.write(str(count) + '\n')
        count += 1

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack(
            (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        images = np.hstack((bg_removed, depth_colormap))
        cv2.namedWindow('All', cv2.WINDOW_NORMAL)
        cv2.imshow('All', images)

        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            f.close()
            cv2.destroyAllWindows()
            break
finally:
    pipeline.stop()
