import warnings
from typing import Any, Dict, List, TypeVar, Union, Optional

import inspect
import numpy as np
from dm_control import suite
from dm_control.utils import containers

import gym
from gym.envs.classic_control import CartPoleEnv

from carl.envs.carl_env import CARLEnv
from carl.envs.dmc.wrappers import MujocoToGymWrapper
from carl.envs.dmc.loader import load_dmc_env
from carl.utils.trial_logger import TrialLogger
from carl.context.selection import AbstractSelector

from carl.envs.dmc.wrappers import ActType, ObsType

# ObsType = TypeVar("ObsType")
# ActType = TypeVar("ActType")


"""
Physics options (defaults for CartPole):
|           apirate = 100.0                                                │
│         collision = 0                                                    │
│              cone = 0                                                    │
│           density = 0.0                                                  │
│      disableflags = 0                                                    │
│       enableflags = 0                                                    │
│           gravity = array([ 0.  ,  0.  , -9.81])                         │
│          impratio = 1.0                                                  │
│        integrator = 0                                                    │
│        iterations = 100                                                  │
│          jacobian = 2                                                    │
│          magnetic = array([ 0. , -0.5,  0. ])                            │
│    mpr_iterations = 50                                                   │
│     mpr_tolerance = 1e-06                                                │
│ noslip_iterations = 0                                                    │
│  noslip_tolerance = 1e-06                                                │
│          o_margin = 0.0                                                  │
│          o_solimp = array([9.0e-01, 9.5e-01, 1.0e-03, 5.0e-01, 2.0e+00]) │
│          o_solref = array([0.02, 1.  ])                                  │
│            solver = 2                                                    │
│          timestep = 0.0025                                               │
│         tolerance = 1e-08                                                │
│         viscosity = 0.0                                                  │
│              wind = array([0., 0., 0.])                                  |


C++ Implementation:
https://mujoco.readthedocs.io/en/latest/APIreference.html#mjoption
struct _mjOption                    // physics options
{
    // timing parameters
    mjtNum timestep;                // timestep
    mjtNum apirate;                 // update rate for remote API (Hz)

    // solver parameters
    mjtNum impratio;                // ratio of friction-to-normal contact impedance
    mjtNum tolerance;               // main solver tolerance
    mjtNum noslip_tolerance;        // noslip solver tolerance
    mjtNum mpr_tolerance;           // MPR solver tolerance

    // physical constants
    mjtNum gravity[3];              // gravitational acceleration
    mjtNum wind[3];                 // wind (for lift, drag and viscosity)
    mjtNum magnetic[3];             // global magnetic flux
    mjtNum density;                 // density of medium
    mjtNum viscosity;               // viscosity of medium

    // override contact solver parameters (if enabled)
    mjtNum o_margin;                // margin
    mjtNum o_solref[mjNREF];        // solref
    mjtNum o_solimp[mjNIMP];        // solimp

    // discrete settings
    int integrator;                 // integration mode (mjtIntegrator)
    int collision;                  // collision mode (mjtCollision)
    int cone;                       // type of friction cone (mjtCone)
    int jacobian;                   // type of Jacobian (mjtJacobian)
    int solver;                     // solver algorithm (mjtSolver)
    int iterations;                 // maximum number of main solver iterations
    int noslip_iterations;          // maximum number of noslip solver iterations
    int mpr_iterations;             // maximum number of MPR solver iterations
    int disableflags;               // bit flags for disabling standard features
    int enableflags;                // bit flags for enabling optional features
};
typedef struct _mjOption mjOption;
"""
TIMING_PARAMETERS = [
    "timestep",  # timestep
    "apirate",  # update rate for remote API (Hz)
]
SOLVER_PARAMETERS = [
    "impratio",  # ratio of friction-to-normal contact impedance
    "tolerance",  # main solver tolerance
    "noslip_tolerance",  # noslip solver tolerance
    "mpr_tolerance",  # MPR solver tolerance
]
PHYSICAL_CONSTANTS = [
    "gravity",
    "wind",
    "magnetic",
    "density",
    "viscosity",
]
OVERRIDE_CONTACT_SOLVER_PARAMETERS = [  # (if enabled)
    "o_margin",  # margin
    "o_solref",  # solref
    "o_solimp",  # solimp
]
DISCRETE_SETTINGS = [
    "integrator",  # integration mode (mjtIntegrator)
    "collision",  # collision mode (mjtCollision)
    "cone",  # type of friction cone (mjtCone)
    "jacobian",  # type of Jacobian (mjtJacobian)
    "solver",  # solver algorithm (mjtSolver)
    "iterations",  # maximum number of main solver iterations
    "noslip_iterations",  # maximum number of noslip solver iterations
    "mpr_iterations",  # maximum number of MPR solver iterations
    "disableflags",  # bit flags for disabling standard features
    "enableflags",  # bit flags for enabling optional features
]

WORLD_PARAMETERS = (
    TIMING_PARAMETERS
    + SOLVER_PARAMETERS
    + PHYSICAL_CONSTANTS
    + OVERRIDE_CONTACT_SOLVER_PARAMETERS
    + TIMING_PARAMETERS
)

class CARLDmcEnv(CARLEnv):
    def __init__(
        self,
        env: gym.Env,
        contexts: Dict[Any, Dict[Any, Any]],
        context_mask: Optional[List[str]],
        hide_context: bool,
        add_gaussian_noise_to_context: bool,
        gaussian_noise_std_percentage: float,
        logger: Optional[TrialLogger],
        scale_context_features: str,
        default_context: Optional[Dict],
        max_episode_length: int,
        state_context_features: Optional[List[str]],
        dict_observation_space: bool,
        context_selector: Optional[Union[AbstractSelector, type(AbstractSelector)]],
        context_selector_kwargs: Optional[Dict],
    ):
        # TODO can we have more than 1 env?
        # env = MujocoToGymWrapper(env)
        self.context_mask = context_mask
        super().__init__(
            env=env,
            contexts=contexts,
            hide_context=hide_context,
            add_gaussian_noise_to_context=add_gaussian_noise_to_context,
            gaussian_noise_std_percentage=gaussian_noise_std_percentage,
            logger=logger,
            scale_context_features=scale_context_features,
            default_context=default_context,
            max_episode_length=max_episode_length,
            state_context_features=state_context_features,
            dict_observation_space=dict_observation_space,
            context_selector=context_selector,
            context_selector_kwargs=context_selector_kwargs,
        )

    def _update_context(self) -> None:
        if self.dict_observation_space:
            raise NotImplementedError
        else:
            env = load_dmc_env(domain_name=self.domain, task_name=self.task, context=self.context, context_mask=self.context_mask, environment_kwargs={"flat_observation": True})
            self.env = MujocoToGymWrapper(env)
