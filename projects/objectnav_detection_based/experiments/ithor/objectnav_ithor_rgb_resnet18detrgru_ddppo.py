from typing import Sequence, Union

import torch.nn as nn

from allenact.base_abstractions.preprocessor import Preprocessor
from allenact.utils.experiment_utils import Builder, TrainingPipeline
from allenact_plugins.ithor_plugin.ithor_sensors import (
    GoalObjectTypeThorSensor,
    RGBSensorThor,
)
from projects.objectnav_baselines.experiments.ithor.objectnav_ithor_base import (
    ObjectNaviThorBaseConfig,
)
from projects.objectnav_baselines.mixins import ObjectNavPPOMixin
from projects.objectnav_detection_based.mixins import (
    ResNetDETRPreprocessGRUActorCriticMixin,
)


class ObjectNaviThorRGBPPOExperimentConfig(ObjectNaviThorBaseConfig):
    """An Object Navigation experiment configuration in iThor with RGB
    input."""

    SENSORS = [
        RGBSensorThor(
            height=ObjectNaviThorBaseConfig.SCREEN_SIZE,
            width=ObjectNaviThorBaseConfig.SCREEN_SIZE,
            use_resnet_normalization=True,
            uuid="rgb_lowres",
        ),
        GoalObjectTypeThorSensor(
            object_types=ObjectNaviThorBaseConfig.TARGET_TYPES,
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.preprocessing_and_model = ResNetDETRPreprocessGRUActorCriticMixin(
            sensors=self.SENSORS,
            resnet_type="RN18",
            screen_size=self.SCREEN_SIZE,
            goal_sensor_type=GoalObjectTypeThorSensor,
        )

        self.n_encoder_layers: int = (
            int(kwargs["n_encoder_layers"]) if "n_encoder_layers" in kwargs else 1
        )
        self.n_decoder_layers: int = (
            int(kwargs["n_encoder_layers"]) if "n_decoder_layers" in kwargs else 1
        )

    def training_pipeline(self, **kwargs) -> TrainingPipeline:
        return ObjectNavPPOMixin.training_pipeline(
            auxiliary_uuids=[],
            multiple_beliefs=False,
            advance_scene_rollout_period=self.ADVANCE_SCENE_ROLLOUT_PERIOD,
        )

    def preprocessors(self) -> Sequence[Union[Preprocessor, Builder[Preprocessor]]]:
        return self.preprocessing_and_model.preprocessors()

    def create_model(self, **kwargs) -> nn.Module:
        return self.preprocessing_and_model.create_model(
            num_actions=self.ACTION_SPACE.n,
            n_encoder_layers=self.n_encoder_layers,
            n_decoder_layers=self.n_decoder_layers,
            **kwargs
        )

    @classmethod
    def tag(cls):
        return "ObjectNav-iTHOR-RGB-ResNet18DETRGRU-DDPPO"
