class Team:
    """
        Holds team members and their common attributes
    """
    def __init__(self, grinder=None, name=None, color=None, spawn_points={}, enemy_name=None):
        self.grinder = grinder
        self.name = name
        self.color = color
        self.enemy_name = enemy_name
        self.fallback_target = None
        self.score = 0
        self.spawn_points = spawn_points
        self.members = []

    def enemy(self):
        return(self.grinder.teams.get([self.enemy_name], None))