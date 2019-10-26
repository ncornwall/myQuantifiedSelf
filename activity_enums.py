from enum import Enum

class ActivitySource(Enum):
    STRAVA = "Strava"
    NIKE = "Nike"
    APPLE = "Apple"

class ActivityType(Enum):
    RUN = "Run"
    BIKE = "Bike"
    SWIM = "Swim"
    ELLIPTICAL = "Elliptical"
    PILATES = "Pilates"
    ROWING = "Rowing"
    WALKING = "Walking"
    YOGA = "Yoga"
    OTHER = "Other"
