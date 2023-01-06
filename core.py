# -*- coding: utf-8 -*-
"""Soft-Panoramic-Transition-Tool.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1S7aBUcfX4NVaCxdKmde-eQcWA1zdL1zW
"""

import cv2
import base64
import time
import numpy as np

from dataclasses import dataclass, astuple


Mat = np.ndarray[int, np.dtype[np.generic]]

@dataclass
class Vec2:
    x: int
    y: int

    @staticmethod
    def zero(self):
        return Vec2(0, 0)

    def __post_init__(self):
        self.x = int(self.x)
        self.y = int(self.y)


@dataclass
class Rect2:
    x1: int
    y1: int
    x2: int
    y2: int

    @staticmethod
    def zero(self):
        return Rect2(0, 0, 0, 0)

    def __init__(self, *args, **kwargs):
        self.x1 = int(kwargs.get('x1'))
        self.x2 = int(kwargs.get('x2'))
        self.y1 = int(kwargs.get('y1'))
        self.y2 = int(kwargs.get('y2'))

    def get_size(self) -> Vec2:
        return Vec2(self.x2 - self.x1, self.y2 - self.y1)

    def get_pos(self) -> Vec2:
        return Vec2(self.x1, self.y1)


class VideoProcessor:

    story_resolution = Vec2(1080, 1920)
    video_dir = '/tmp'
    video_name = f'{video_dir}/video-%s.mp4'

    def __init__(self, img, rect_start, rect_end, fps=30, video_length=10):
        self.img = img
        self.rect_start = Rect2(**rect_start)
        self.rect_end = Rect2(**rect_end)
        self.fps = fps
        self.video_length = video_length
        self.transition_speed = video_length * fps

    def readb64(self, uri):
        encoded_data = uri.split(',')[1]
        nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img


    def mov_vec2(self, start_vec: Vec2, end_vec: Vec2, transition_step: int) -> Vec2:
        return Vec2(start_vec.x + transition_step * (end_vec.x - start_vec.x) / self.transition_speed,
                    start_vec.y + transition_step * (end_vec.y - start_vec.y) / self.transition_speed)


    def crop(self, point: Vec2, crop_size: Vec2, img) -> Mat:
        return img[point.y:point.y + crop_size.y, point.x:point.x + crop_size.x]


    def produce_video(self) -> str:
        frame = self.readb64(self.img)
        height, width = frame.shape[:2]
        video_name = self.video_name % time.time()

        start_size, end_size = self.rect_start.get_size(), self.rect_end.get_size()
        start_vec, end_vec = self.rect_start.get_pos(), self.rect_end.get_pos()
        
        cropped_images = []
        for idx, img in enumerate([frame] * self.transition_speed):
            crop_size = self.mov_vec2(start_size, end_size, idx)
            crop_point = self.mov_vec2(start_vec, end_vec, idx)
            cropped_img = self.crop(crop_point, crop_size, img)
            cropped_img = cv2.resize(cropped_img, astuple(
                end_size), interpolation=cv2.INTER_CUBIC)
            cropped_images.append(cropped_img)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(video_name, fourcc, self.fps, astuple(end_size))

        for image in cropped_images:
            assert image.shape[:2] == astuple(end_size)[::-1]
            video.write(image)

        cv2.destroyAllWindows()
        video.release()

        return video_name
