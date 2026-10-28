"""AI Engines package for sports performance, biomechanics, injury prediction,
adaptive training, game strategy, and virtual coaching.
"""

from app.ai.biomechanics import BiomechanicsEngine, calculate_angle_2d
from app.ai.injury_predictor import InjuryPredictor
from app.ai.training_engine import TrainingEngine
from app.ai.game_strategy import GameStrategyEngine
from app.ai.coaching_bot import VirtualCoachEngine

__all__ = [
    "BiomechanicsEngine",
    "calculate_angle_2d",
    "InjuryPredictor",
    "TrainingEngine",
    "GameStrategyEngine",
    "VirtualCoachEngine"
]
