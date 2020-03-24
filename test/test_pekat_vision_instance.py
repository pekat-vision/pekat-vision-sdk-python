# WARNING
# You need a special project first. Contact developers@pekatvision.com first,

import os
from unittest import TestCase

import cv2
import requests

from PekatVisionSDK import Instance


class TestPekatVisionInstance(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestPekatVisionInstance, self).__init__(*args, **kwargs)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.pekat_dist = None
        self.project_dist = os.path.join(dir_path, 'project_template')
        self.img_nok_path = os.path.join(dir_path,'nok.png')
        self.img_nok_heatmap_path = os.path.join(dir_path,'nok_heatmap.png')
        self.img_nok_annotated_path = os.path.join(dir_path,'nok_annotated.png')

    def test_analyze(self):
        p = Instance(self.project_dist, self.pekat_dist)
        # response type
        # annotated_image
        img, _ = p.analyze(self.img_nok_path, response_type='annotated_image')
        img_template = cv2.imread(self.img_nok_annotated_path)
        if cv2.subtract(img, img_template).sum() != 0:
            self.fail()
        # heatmap
        img, _ = p.analyze(self.img_nok_path, response_type='heatmap')
        img_template = cv2.imread(self.img_nok_heatmap_path)
        if cv2.subtract(img, img_template).sum() != 0:
            self.fail()
        # context
        p.analyze(self.img_nok_path, response_type='context')
        p.analyze(self.img_nok_path)

        # data in request
        r = p.analyze(self.img_nok_path, data='test')
        self.assertTrue(r.get('dataFound'))

    def test_stop(self):
        p = Instance(self.project_dist, self.pekat_dist)
        p.analyze(self.img_nok_path)
        p.stop()
        try:
            p.analyze(self.img_nok_path, timeout=4)
        except requests.exceptions.ConnectionError:
            return
        self.fail()
