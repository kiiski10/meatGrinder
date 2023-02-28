import pygame, random, time
from machine import Machine
import utilities
from equipment import *


class Section:
    def __init__(self, tile_pos, prodLine):
        # self.image = img
        self.prodLine = prodLine
        self.tilePos = tile_pos
        self.machine = None
        self.fighters_here = []
        self.selected_input = None
        self.last_output_to_section = None
        self.output_gate_target = False
        all_directions = [
            (self.tilePos[0] - 1, self.tilePos[1]),
            (self.tilePos[0] + 1, self.tilePos[1]),
            (self.tilePos[0], self.tilePos[1] + 1),
            (self.tilePos[0], self.tilePos[1] - 1),
        ]
        # list only tiles inside of factory area
        self.available_directions = [
            x
            for x in all_directions
            if x[0] <= 9 and x[1] <= 9 and x[0] >= 0 and x[1] >= 0
        ]

    def possible_outputs(self):
        possible_outputs = []
        for pos in self.available_directions:
            key = utilities.tilePosId(pos)
            if key in self.prodLine.line:
                possible_outputs.append(self.prodLine.line[key])
        return possible_outputs

    def next_section(self):
        possible_outputs = self.possible_outputs()
        if self.selected_input in possible_outputs:
            possible_outputs.remove(self.selected_input)       
        if possible_outputs:
            section = random.choice(possible_outputs)
        else:
            section = self
        return section


class ProductionLine:
    def __init__(self, factory, inGate):
        print("production line init")
        self.inGate = inGate
        self.outGates = [(0, 0), (0, 9)]
        self.factory = factory
        self.debugLayer = pygame.Surface(self.factory.surface.get_rect().size)
        self.debugLayer.set_colorkey((255, 0, 255))
        self.debugLayer.fill((255, 0, 255))
        self.stats = {
            "step": 0,
            "last_step_time": 0,
        }

        self.line = {
            utilities.tilePosId(self.inGate): Section(self.inGate, self),
        }

        for tile_pos in self.factory.getTilesByLayer("prodLine"):
            newSection = Section(tile_pos, self)
            tile_pos_id = utilities.tilePosId(tile_pos)
            if tile_pos_id in self.factory.grinder.fighterInputs:
                output_pos = self.factory.grinder.fighterInputs[tile_pos_id]
                newSection.output_gate_target = output_pos
            self.line[utilities.tilePosId(tile_pos)] = newSection

        # debug draw connections
        for pos_id, section in self.line.items():
            pos = section.tilePos
            for possible_output in section.possible_outputs():
                pygame.draw.line(
                    self.debugLayer,
                    [242, 132, 45],
                    utilities.tilePosToScreenPos(48, section.tilePos),
                    utilities.tilePosToScreenPos(48, possible_output.tilePos),
                    5,
                )

        # add machines to random sections (not on the sides)
        for s in self.line:
            if self.line[s].tilePos[0] not in [0, 9] and self.line[s].tilePos[
                1
            ] not in [0, 9]:
                if random.randint(0, 100) < 20:
                    self.line[s].machine = Machine(self.line[s])

    def addFighter(self, newFighter):
        pos = utilities.screenPosToTilePos(48, newFighter.rect.center)
        pos_id = utilities.tilePosId(pos)
        section = self.line[pos_id]
        section.fighters_here.append(newFighter)
        self.factory.fighterSprites.add(newFighter)

    def lineAdvance(self):
        # move fighters
        for pos_id, section in self.line.items():
            output = section.next_section()
            if len(section.fighters_here) > 0 and len(output.fighters_here) == 0:
                first_obj = section.fighters_here[0]
                if not first_obj.moved_in_step == self.stats["step"]:
                    output.fighters_here.append(first_obj)
                    first_obj.rect.center = utilities.tilePosToScreenPos(
                        48, output.tilePos
                    )
                    section.fighters_here.remove(first_obj)
                    first_obj.moved_in_step = self.stats["step"]

                    if not output.selected_input:
                        output.selected_input = section

    def move_fighter_to_grinder(self, fighter, gate_section):
        fighter.rect.center = gate_section.output_gate_target
        self.factory.grinder.fighters.append(fighter)
        gate_section.fighters_here.remove(fighter)
        self.factory.fighterSprites.remove(fighter)

    def step(self):
        self.stats["step"] += 1
        if time.time() - self.stats["last_step_time"] > 0.25:
            self.stats["last_step_time"] = time.time()
            self.lineAdvance()

        for gate in self.outGates:
            gate_section = self.line[utilities.tilePosId(gate)]
            for fighter in gate_section.fighters_here:
                self.move_fighter_to_grinder(fighter, gate_section)
