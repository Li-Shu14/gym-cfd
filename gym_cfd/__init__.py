import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__) # soccer项目里有这一项，尚不清楚功用。

register(
    id='cfd_simple-v0',
    entry_point='gym_cfd.envs:CfdSimpleEnv',
)

""" soccer项目里有这一项，尚不清楚功用。
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic = True,
"""

register(
    id='cfd_complex-v0',
    entry_point='gym_cfd.envs:CfdComplexEnv',
)