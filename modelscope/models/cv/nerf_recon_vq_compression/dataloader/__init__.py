from .blender import BlenderDataset
from .llff import LLFFDataset
from .nsvf import NSVF
from .ray_utils import get_rays, ndc_rays_blender
from .tankstemple import TanksTempleDataset
from .your_own_data import YourOwnDataset

dataset_dict = {
    'blender': BlenderDataset,
    'llff': LLFFDataset,
    'tankstemple': TanksTempleDataset,
    'nsvf': NSVF,
    'own_data': YourOwnDataset
}
