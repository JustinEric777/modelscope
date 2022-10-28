# Copyright (c) Alibaba, Inc. and its affiliates.
import os
import unittest
from os import path as osp

import cv2
from PIL import Image

from modelscope.models import Model
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.utils.cv.image_utils import created_boxed_image
from modelscope.utils.demo_utils import DemoCompatibilityCheck
from modelscope.utils.test_utils import test_level


class OfaTasksTest(unittest.TestCase, DemoCompatibilityCheck):

    def setUp(self) -> None:
        self.output_dir = 'unittest_output'
        os.makedirs(self.output_dir, exist_ok=True)

    def save_img(self, image_in, box, image_out):
        cv2.imwrite(
            osp.join(self.output_dir, image_out),
            created_boxed_image(image_in, box))

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_image_captioning_with_model(self):
        model = Model.from_pretrained('damo/ofa_image-caption_coco_large_en')
        img_captioning = pipeline(
            task=Tasks.image_captioning,
            model=model,
        )
        image = 'data/test/images/image_captioning.png'
        result = img_captioning(image)
        print(result[OutputKeys.CAPTION])

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_image_captioning_with_name(self):
        img_captioning = pipeline(
            Tasks.image_captioning,
            model='damo/ofa_image-caption_coco_large_en')
        result = img_captioning('data/test/images/image_captioning.png')
        print(result[OutputKeys.CAPTION])

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_ocr_recognize_with_name(self):
        ocr_recognize = pipeline(
            Tasks.ocr_recognition,
            model='damo/ofa_ocr-recognition_scene_base_zh')
        result = ocr_recognize('data/test/images/image_ocr_recognition.jpg')
        print(result[OutputKeys.TEXT])

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_image_classification_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_image-classification_imagenet_large_en')
        ofa_pipe = pipeline(Tasks.image_classification, model=model)
        image = 'data/test/images/image_classification.png'
        result = ofa_pipe(image)
        print(result)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_image_classification_with_name(self):
        ofa_pipe = pipeline(
            Tasks.image_classification,
            model='damo/ofa_image-classification_imagenet_large_en')
        image = 'data/test/images/image_classification.png'
        result = ofa_pipe(image)
        print(result)

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_summarization_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_summarization_gigaword_large_en')
        ofa_pipe = pipeline(Tasks.text_summarization, model=model)
        text = 'five-time world champion michelle kwan withdrew' + \
               'from the #### us figure skating championships on wednesday ,' + \
               ' but will petition us skating officials for the chance to ' + \
               'compete at the #### turin olympics .'
        input = {'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_summarization_with_name(self):
        ofa_pipe = pipeline(
            Tasks.text_summarization,
            model='damo/ofa_summarization_gigaword_large_en')
        text = 'five-time world champion michelle kwan withdrew' + \
               'from the #### us figure skating championships on wednesday ,' + \
               ' but will petition us skating officials for the chance to ' +\
               'compete at the #### turin olympics .'
        input = {'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_text_classification_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_text-classification_mnli_large_en')
        ofa_pipe = pipeline(Tasks.text_classification, model=model)
        text = 'One of our number will carry out your instructions minutely.'
        text2 = 'A member of my team will execute your orders with immense precision.'
        result = ofa_pipe((text, text2))
        result = ofa_pipe({'text': text, 'text2': text2})
        print(result)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_text_classification_with_name(self):
        ofa_pipe = pipeline(
            Tasks.text_classification,
            model='damo/ofa_text-classification_mnli_large_en')
        text = 'One of our number will carry out your instructions minutely.'
        text2 = 'A member of my team will execute your orders with immense precision.'
        result = ofa_pipe((text, text2))
        print(result)

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_visual_entailment_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_visual-entailment_snli-ve_large_en')
        ofa_pipe = pipeline(Tasks.visual_entailment, model=model)
        image = 'data/test/images/dogs.jpg'
        text = 'there are two birds.'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_visual_entailment_with_name(self):
        ofa_pipe = pipeline(
            Tasks.visual_entailment,
            model='damo/ofa_visual-entailment_snli-ve_large_en')
        image = 'data/test/images/dogs.jpg'
        text = 'there are two birds.'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_visual_grounding_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_visual-grounding_refcoco_large_en')
        ofa_pipe = pipeline(Tasks.visual_grounding, model=model)
        image = 'data/test/images/visual_grounding.png'
        text = 'a blue turtle-like pokemon with round head'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)
        image_name = image.split('/')[-2]
        self.save_img(
            image,
            result[OutputKeys.BOXES][0],  # just one box
            osp.join('large_en_model_' + image_name + '.png'))

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_visual_grounding_with_name(self):
        ofa_pipe = pipeline(
            Tasks.visual_grounding,
            model='damo/ofa_visual-grounding_refcoco_large_en')
        image = 'data/test/images/visual_grounding.png'
        text = 'a blue turtle-like pokemon with round head'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)
        image_name = image.split('/')[-2]
        self.save_img(image, result[OutputKeys.BOXES][0],
                      osp.join('large_en_name_' + image_name + '.png'))

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_visual_grounding_zh_with_name(self):
        model = 'damo/ofa_visual-grounding_refcoco_large_zh'
        ofa_pipe = pipeline(Tasks.visual_grounding, model=model)
        image = 'data/test/images/visual_grounding.png'
        text = '一个圆头的蓝色宝可梦'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)
        image_name = image.split('/')[-1]
        self.save_img(image, result[OutputKeys.BOXES][0],
                      osp.join('large_zh_name_' + image_name))

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_visual_question_answering_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_visual-question-answering_pretrain_large_en')
        ofa_pipe = pipeline(Tasks.visual_question_answering, model=model)
        image = 'data/test/images/visual_question_answering.png'
        text = 'what is grown on the plant?'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_visual_question_answering_with_name(self):
        model = 'damo/ofa_visual-question-answering_pretrain_large_en'
        ofa_pipe = pipeline(Tasks.visual_question_answering, model=model)
        image = 'data/test/images/visual_question_answering.png'
        text = 'what is grown on the plant?'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_image_captioning_distilled_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_image-caption_coco_distilled_en')
        img_captioning = pipeline(
            task=Tasks.image_captioning,
            model=model,
        )
        image_path = 'data/test/images/image_captioning.png'
        image = Image.open(image_path)
        result = img_captioning(image)
        print(result[OutputKeys.CAPTION])

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_visual_entailment_distilled_model_with_name(self):
        ofa_pipe = pipeline(
            Tasks.visual_entailment,
            model='damo/ofa_visual-entailment_snli-ve_distilled_v2_en')
        image = 'data/test/images/dogs.jpg'
        text = 'there are two birds.'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_visual_grounding_distilled_model_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_visual-grounding_refcoco_distilled_en')
        ofa_pipe = pipeline(Tasks.visual_grounding, model=model)
        image = 'data/test/images/visual_grounding.png'
        text = 'a blue turtle-like pokemon with round head'
        input = {'image': image, 'text': text}
        result = ofa_pipe(input)
        print(result)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_run_with_text_to_image_synthesis_with_name(self):
        model = 'damo/ofa_text-to-image-synthesis_coco_large_en'
        ofa_pipe = pipeline(Tasks.text_to_image_synthesis, model=model)
        ofa_pipe.model.generator.beam_size = 2
        example = {'text': 'a bear in the water.'}
        result = ofa_pipe(example)
        result[OutputKeys.OUTPUT_IMG].save('result.png')
        print(f'Output written to {osp.abspath("result.png")}')

    @unittest.skipUnless(test_level() >= 1, 'skip test in current test level')
    def test_run_with_text_to_image_synthesis_with_model(self):
        model = Model.from_pretrained(
            'damo/ofa_text-to-image-synthesis_coco_large_en')
        ofa_pipe = pipeline(Tasks.text_to_image_synthesis, model=model)
        ofa_pipe.model.generator.beam_size = 2
        example = {'text': 'a bear in the water.'}
        result = ofa_pipe(example)
        result[OutputKeys.OUTPUT_IMG].save('result.png')
        print(f'Output written to {osp.abspath("result.png")}')

    @unittest.skip('demo compatibility test is only enabled on a needed-basis')
    def test_demo_compatibility(self):
        self.compatibility_check()


if __name__ == '__main__':
    unittest.main()
