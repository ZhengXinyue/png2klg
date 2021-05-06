import click
import os
import numpy as np
import cv2
import zlib
from tqdm import tqdm


@click.command()
@click.option('--rgb_path', default='rgb_images', type=str, help='color image folder path.')
@click.option('--depth_path', default='depth_images', type=str, help='depth image folder path')
@click.option('--timestamp_path', default='timestamps.txt', type=str, help='timestamps file path.')
@click.option('--target_klg', default='data.klg', type=str, help='target .klg filename.')
def write_klg(rgb_path, depth_path, timestamp_path, target_klg):
    all_rgb_images = os.listdir(rgb_path)
    all_rgb_images.sort()
    all_depth_images = os.listdir(depth_path)
    all_depth_images.sort()
    n_frames = len(all_rgb_images)
    print('total frames: %d' % n_frames)
    if os.path.exists(timestamp_path):
        with open(timestamp_path, 'r') as f:
            timestamps = f.readlines()
    else:
        timestamps = range(n_frames)
    klg = open(target_klg, 'wb')
    # <number of frames encoded as 32 bit int>
    klg.write(np.uint32(n_frames))
    curr_frame = 0
    for rgb, depth, t in tqdm(zip(all_rgb_images, all_depth_images, timestamps)):
        curr_frame += 1
        # <timestamp encoded as 64 bit int>
        timestamp = np.uint64(t)

        depth_image = cv2.imread(depth_path + '/' + depth, cv2.IMREAD_UNCHANGED).byteswap()
        # <depth buffer zlib compressed in the following depth_size number of bytes>
        depth_image = zlib.compress(depth_image, 9)
        # <depth_size encoded as 32 bit int>
        depth_size = np.uint32(len(depth_image))

        rgb_image = cv2.imread(rgb_path + '/' + rgb)
        # <rgb buffer jpeg compressed in the following image_size number of bytes>
        rgb_image = cv2.imencode('.jpeg', rgb_image)[1].tostring()
        # <image_size (rgb) encoded as 32 bit int>
        rgb_size = np.uint32(len(rgb_image))

        klg.write(timestamp)
        klg.write(depth_size)
        klg.write(rgb_size)
        klg.write(depth_image)
        klg.write(rgb_image)

    klg.close()


if __name__ == '__main__':
    write_klg()
