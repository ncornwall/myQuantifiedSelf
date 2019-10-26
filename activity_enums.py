from enum import Enum

class ActivitySource(Enum):
    STRAVA = "strava"
    NIKE = "nike"
    APPLE = "apple"

class ActivityType(Enum):
    RUN = "run"
    BIKE = "bike"
    SWIM = "swim"
    OTHER = "other"
