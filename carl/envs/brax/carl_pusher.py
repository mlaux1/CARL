from __future__ import annotations

from carl.envs.brax.carl_brax_env import CARLBraxEnv


class CARLBraxPusher(CARLBraxEnv):
    env_name: str = "pusher"
    asset_path: str = "envs/assets/pusher.xml"
