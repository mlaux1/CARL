from typing import Dict, Optional

import gym
import numpy as np
from src.envs.mario.mario_env import MarioEnv
from src.envs.mario.toad_gan import generate_initial_noise, generate_level
from src.envs.meta_env import MetaEnv
from src.trial_logger import TrialLogger

INITIAL_WIDTH = 200
INITIAL_LEVEL_INDEX = 0
INITIAL_HEIGHT = 16
DEFAULT_CONTEXT = {
    "level_index": INITIAL_LEVEL_INDEX,
    "width": INITIAL_WIDTH,
    "noise": generate_initial_noise(INITIAL_WIDTH, INITIAL_HEIGHT, INITIAL_LEVEL_INDEX),
}

CONTEXT_BOUNDS = {
    "level_index": (None, None, "categorical", np.arange(0, 14)),
    "width": (16, np.inf, int),
    "noise": (-1.0, 1.0, float),
}
CATEGORICAL_CONTEXT_FEATURES = ["level_index"]


class MetaMarioEnv(MetaEnv):
    def __init__(
        self,
        env: gym.Env = MarioEnv(levels=[]),
        contexts: Dict[int, Dict] = {},
        instance_mode: str = "rr",
        hide_context: bool = False,
        add_gaussian_noise_to_context: bool = True,
        gaussian_noise_std_percentage: float = 0.01,
        logger: Optional[TrialLogger] = None,
        scale_context_features: str = "no",
        default_context: Optional[Dict] = DEFAULT_CONTEXT,
    ):
        if not contexts:
            contexts = {0: DEFAULT_CONTEXT}
        super().__init__(
            env=env,
            contexts=contexts,
            instance_mode=instance_mode,
            hide_context=True,
            add_gaussian_noise_to_context=add_gaussian_noise_to_context,
            gaussian_noise_std_percentage=gaussian_noise_std_percentage,
            logger=logger,
            scale_context_features="no",
            default_context=default_context,
        )
        self.whitelist_gaussian_noise = [k for k in DEFAULT_CONTEXT.keys() if k not in CATEGORICAL_CONTEXT_FEATURES]
        self._update_context()

    def _update_context(self):
        level = generate_level(
            width=int(self.context["width"]),
            height=16,
            level_index=int(self.context["level_index"]),
            initial_noise=self.context["noise"],
        )
        self.env.levels = [level]
