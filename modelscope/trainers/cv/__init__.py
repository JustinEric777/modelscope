# Copyright (c) Alibaba, Inc. and its affiliates.
from typing import TYPE_CHECKING

from modelscope.utils.import_utils import LazyImportModule

if TYPE_CHECKING:
    from .image_instance_segmentation_trainer import \
        ImageInstanceSegmentationTrainer
    from .image_portrait_enhancement_trainer import ImagePortraitEnhancementTrainer
    from .movie_scene_segmentation_trainer import MovieSceneSegmentationTrainer
    from .image_inpainting_trainer import ImageInpaintingTrainer

else:
    _import_structure = {
        'image_instance_segmentation_trainer':
        ['ImageInstanceSegmentationTrainer'],
        'image_portrait_enhancement_trainer':
        ['ImagePortraitEnhancementTrainer'],
        'movie_scene_segmentation_trainer': ['MovieSceneSegmentationTrainer'],
        'image_inpainting_trainer': ['ImageInpaintingTrainer']
    }

    import sys

    sys.modules[__name__] = LazyImportModule(
        __name__,
        globals()['__file__'],
        _import_structure,
        module_spec=__spec__,
        extra_objects={},
    )
