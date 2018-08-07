from .GongZhu import *

from gym.envs.registration import register

register(
    id='GongZhu_Card_Game-v0',
    entry_point='GongZhu.GongZhu:GongZhuEnv',
    kwargs={'playersName': ['Kazuma', 'Aqua', 'Megumin', 'Darkness'], 'minScore': -1000}
)