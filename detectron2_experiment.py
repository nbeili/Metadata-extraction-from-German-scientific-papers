# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
Detection Training Script.
This scripts reads a given config file and runs the training or evaluation.
It is an entry point that is made to train standard models in detectron2.
In order to let one script support training of many models,
this script contains logic that are specific to these built-in models and therefore
may not be suitable for your own project.
For example, your research project perhaps only needs a single "evaluator".
Therefore, we recommend you to use detectron2 as an library and take
this file as an example of how to use the library.
You may want to write your own script with your datasets and other customizations.
"""

import logging
import os
import datetime
from collections import OrderedDict
import torch

import detectron2.utils.comm as comm
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultTrainer, default_argument_parser, default_setup, hooks, launch
from detectron2.evaluation import CityscapesEvaluator,
    COCOEvaluator,
    COCOPanopticEvaluator,
    DatasetEvaluators,
    LVISEvaluator,
    PascalVOCDetectionEvaluator,
    SemSegEvaluator,
    verify_results
    
from detectron2.modeling import GeneralizedRCNNWithTTA


from detectron2.data.datasets import register_coco_instances
from detectron2.utils.logger import setup_logger

logger = logging.getLogger("detectron2")


class Trainer(DefaultTrainer):
    """
    We use the "DefaultTrainer" which contains a number pre-defined logic for
    standard training workflow. They may not work for you, especially if you
    are working on a new research project. In that case you can use the cleaner
    "SimpleTrainer", or write your own training loop.
    """

    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):
        """
        Create evaluator(s) for a given dataset.
        This uses the special metadata "evaluator_type" associated with each builtin dataset.
        For your own dataset, you can simply create an evaluator manually in your
        script and do not have to worry about the hacky if-else logic here.
        """
        if output_folder is None:
            output_folder = os.path.join(cfg.OUTPUT_DIR, "inference")
        evaluator_list = []
        evaluator_type = MetadataCatalog.get(dataset_name).evaluator_type
        if evaluator_type in ["sem_seg", "coco_panoptic_seg"]:
            evaluator_list.append(
                SemSegEvaluator(
                    dataset_name,
                    distributed=False,
                    num_classes=cfg.MODEL.SEM_SEG_HEAD.NUM_CLASSES,
                    ignore_label=cfg.MODEL.SEM_SEG_HEAD.IGNORE_VALUE,
                    output_dir=output_folder,
                )
            )
        if evaluator_type in ["coco", "coco_panoptic_seg"]:
            evaluator_list.append(COCOEvaluator(dataset_name, cfg, False, output_folder))
        if len(evaluator_list) == 1:
            return evaluator_list[0]
        return DatasetEvaluators(evaluator_list)


def setup(args):
    """
    Create configs and perform basic setups.
    """
    cfg = get_cfg()
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()
    default_setup(cfg, args)
    return cfg


def main(args):
    cfg = setup(args)

    if args.eval_only:
        model = Trainer.build_model(cfg)
        DetectionCheckpointer(model, save_dir=cfg.OUTPUT_DIR).resume_or_load(
            cfg.MODEL.WEIGHTS, resume=args.resume
        )
        res = Trainer.test(cfg, model)
        if comm.is_main_process():
            verify_results(cfg, res)
        if cfg.TEST.AUG.ENABLED:
            res.update(Trainer.test_with_TTA(cfg, model))
        return res

    """
    If you'd like to do anything fancier than the standard training logic,
    consider writing your own training loop or subclassing the trainer.
    """
    trainer = Trainer(cfg)
    trainer.resume_or_load(resume=args.resume)
    if cfg.TEST.AUG.ENABLED:
        trainer.register_hooks(
            [hooks.EvalHook(0, lambda: trainer.test_with_TTA(cfg, trainer.model))]
        )
    return trainer.train()


if __name__ == "__main__":
    args = default_argument_parser().parse_args()
    output_dir = os.path.join('./output', datetime.datetime.now().strftime('%Y%m%dT%H%M'))
    os.makedirs(output_dir, exist_ok=True)
    logger = setup_logger(output=output_dir)
    logger.info("Command Line Args:", args)

    register_coco_instances(
        "dla_train",
        {},
        "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/train/images",
        "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/train/trainval.json"
    )

    register_coco_instances(
        "dla_val",
        {},
        "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/val/trainval.json",
        "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/val/images"
    )

    metadata_train = MetadataCatalog.get("dla_train")
    metadata_val = MetadataCatalog.get("dla_val")

    cfg = get_cfg()
    # mask rcnn resnet101
    # cfg.merge_from_file("configs/DLA_mask_rcnn_R_101_FPN_3x.yaml")
    # mask rcnn resnext
    cfg.merge_from_file("/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/detectron2/configs/DLA_mask_rcnn_X_101_32x8d_FPN_3x.yaml")

    cfg.OUTPUT_DIR = output_dir

    logger.info(cfg)

    # serialize the training config
    cfg_str = cfg.dump()
    with open(os.path.join(cfg.OUTPUT_DIR, "train_config.yaml"), "w") as f:
        f.write(cfg_str)
    f.close()

    trainer = Trainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()

"""
import detectron2
from detectron2.utils.logger import setup_logger
from detectron2.data.datasets import register_coco_instances
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer

from detectron2 import model_zoo

import torch, torchvision

import numpy as np 
import cv2
import random

import os
import numpy as np
import json
from detectron2.structures import BoxMode
setup_logger()

register_coco_instances("papers_train", {}, "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/train/trainval.json", "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/train")
register_coco_instances("papers_val", {}, "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/val/trainval.json", "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/all_May_2020/val")

papers_metadata = MetadataCatalog.get("papers_train")
dataset_dicts = DatasetCatalog.get("papers_train")

# look at the data

for d in random.sample(dataset_dicts, 2):
    img = cv2.imread(d["file_name"])
    visualizer = Visualizer(img[:, :, ::-1], metadata=papers_metadata, scale=0.5)
    vis = visualizer.draw_dataset_dict(d)
    cv2.imshow('ImageWindow', vis.get_image()[:, :, ::-1])
    cv2.waitKey()

#TRAIN!

cfg = get_cfg()
cfg.merge_from_file("/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/detectron2/configs/DLA_mask_rcnn_X_101_32x8d_FPN_3x.yaml")
#cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.DATASETS.TRAIN = ("papers_train",)
cfg.DATASETS.TEST = ()
cfg.DATALOADER.NUM_WORKERS = 2
cfg.MODEL.WEIGHTS = "/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/code/detectron2/model_final_trimmed.pth"  #model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # Let training initialize from model zoo
#cfg.MODEL.DEVICE='cpu'

cfg.MODEL.RETINANET.SCORE_THRESH_TEST = 0.5
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = 0.5

cfg.SOLVER.IMS_PER_BATCH = 2
cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
cfg.SOLVER.MAX_ITER = 300    # 300 iterations seems good enough for this toy dataset; you may need to train longer for a practical dataset
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # faster, and good enough for this toy dataset (default: 512)
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 9

os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()


def get_paper_dicts(img_dir):
    json_file = os.path.join(img_dir, "via_export_json.json")
    with open(json_file) as f:
        imgs_anns = json.load(f)

    dataset_dicts = []
    for idx, v in enumerate(imgs_anns.values()):
        record = {}

        filename = os.path.join(img_dir, v["filename"])
        height, width = cv2.imread(filename).shape[:2]

        record["file_name"] = filename
        record["image_id"] = idx
        record["height"] = height
        record["width"] = width

        annos = v["regions"]
        objs = []
        for _, anno in annos.items():
            assert not anno["region_attributes"]
            anno = anno["region_attributes"]
            px = anno["all_points_x"]
            py = anno["all_points_y"]
            poly = [(x + 0.5, y + 0.5) for x, y in zip(px, py)]

            obj = {
                "bbox": [np.min(px), np.min(py), np.max(px), np.max(py)],
                "bbox_mode": BoxMode.XYXY_ABS,
                "segmentation": [poly],
                "category_id": 0,
                "iscrowd": 0
            }
            objs.append(obj)
        record["annotations"] = objs
        dataset_dicts.append(record)
    return dataset_dicts


for d in ["1-German_papers_last_13", "3-German_papers(with_reference_in_footnote_and_end_of_pape"]:
    DatasetCatalog.register(d, lambda d=d: get_paper_dicts("/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/" + d))
    MetadataCatalog.get(d).set(thing_classes=["title", "author", "affiliation", "address", "email", "date", "abstract"])

paper_metadata = MetadataCatalog.get("1-German_papers_last_13")

dataset_dicts = get_paper_dicts("/media/timo/D/Dokumente/Koblenz/SoSe2020/ML_Application/annotations/JPEG/1-German_papers_last_13")
for d in random.sample(dataset_dicts, 3):
    img = cv2.imread(d["file_name"])
    visualizer = visualizer(img[:, :, ::-1], metadata=balloon_metadata, scale=0.5)
    vis = visualizer.draw_dataset_dict(d)
    cv2_imshow(vis.get_image()[:, :, ::-1])


"""