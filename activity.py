class Activity():
    def __init__(self, id, start_time, distance, source, properties):
        self.id = id
        self.distance = distance
        self.start_time = start_time
        self.source = source
        self.properties = properties
    
    # def __hash__(self):
    #     return hash((self.id, self.distance, self.start_time))
    
    def isDuplicate(self, other):
        return (abs(self.distance - other.distance) < 1 and 
            abs((self.start_time - other.start_time).total_seconds()) < 600)
