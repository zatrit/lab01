"""Код взят с http://www.roguebasin.com/index.php?title=A_Simple_Dungeon_Generator_for_Python_2_or_3
и переписан под данную игру"""

import random
from dataclasses import field, dataclass
from itertools import product

WALL_CELLS = "#", "G"
FLOOR_CELLS = ".", "b"


@dataclass
class RoguelikeMap:
    tiles: list[str]
    room_list: list[list[int]]
    coridor_list: list[tuple[int, int]]
    size: tuple[int, int]


@dataclass
class Generator():
    width: int = 15
    height: int = 15
    max_rooms: int = 15
    min_room_xy: int = 5
    max_room_xy: int = 10
    min_bushes_xy: int = 4
    rooms_overlap: bool = False
    random_connections: int = 1
    random_spurs: int = 4
    level: list = field(default_factory=list)
    room_list: list = field(default_factory=list)
    corridor_list: list = field(default_factory=list)

    def gen_room(self):
        w = random.randint(self.min_room_xy, self.max_room_xy)
        h = random.randint(self.min_room_xy, self.max_room_xy)
        x = random.randint(1, (self.width - w - 1))
        y = random.randint(1, (self.height - h - 1))

        return x, y, w, h

    def room_overlapping(self, room, room_list):
        x, y, w, h, *_ = room

        for current_room in room_list:
            if (x < (current_room[0] + current_room[2]) and
                    current_room[0] < (x + w) and
                    y < (current_room[1] + current_room[3]) and
                    current_room[1] < (y + h)):
                return True

        return False

    def corridor_between_points(self, x1, y1, x2, y2, join_type='either'):
        if x1 == x2 and y1 == y2 or x1 == x2 or y1 == y2:
            return [(x1, y1), (x2, y2)]
        else:
            if join_type == 'either' and {0, 1}.intersection({x1, x2, y1, y2}):

                join = 'bottom'
            elif join_type == 'either' and {self.width - 1, self.width - 2}\
                .intersection({x1, x2}) or {self.height - 1, self.height - 2}\
                    .intersection({y1, y2}):
                join = 'top'
            elif join_type == 'either':
                join = random.choice(['top', 'bottom'])
            else:
                join = join_type

            if join == 'top':
                return [(x1, y1), (x1, y2), (x2, y2)]
            elif join == 'bottom':
                return [(x1, y1), (x2, y1), (x2, y2)]

    def join_rooms(self, room_1, room_2, join_type='either'):
        sorted_room = [room_1, room_2]
        sorted_room.sort(key=lambda x_y: x_y[0])

        x1, y1, w1, h1, *_ = sorted_room[0]
        x1_2 = x1 + w1 - 1
        y1_2 = y1 + h1 - 1

        x2, y2, w2, h2, *_ = sorted_room[1]
        x2_2 = x2 + w2 - 1
        y2_2 = y2 + h2 - 1

        if x1 < (x2 + w2) and x2 < (x1 + w1):
            jx1 = random.randint(x2, x1_2)
            jx2 = jx1
            tmp_y = [y1, y2, y1_2, y2_2]
            tmp_y.sort()
            jy1 = tmp_y[1] + 1
            jy2 = tmp_y[2] - 1

            corridors = self.corridor_between_points(jx1, jy1, jx2, jy2)
            self.corridor_list.append(corridors)

        elif y1 < (y2 + h2) and y2 < (y1 + h1):
            if y2 > y1:
                jy1 = random.randint(y2, y1_2)
                jy2 = jy1
            else:
                jy1 = random.randint(y1, y2_2)
                jy2 = jy1
            tmp_x = [x1, x2, x1_2, x2_2]
            tmp_x.sort()
            jx1, jx2 = tmp_x[1] + 1, tmp_x[2] - 1

            corridors = self.corridor_between_points(jx1, jy1, jx2, jy2)
            self.corridor_list.append(corridors)

        else:
            join = random.choice(['top', 'bottom']) \
                if join_type == 'either' else join_type

            if join == 'top':
                if y2 > y1:
                    jx1 = x1_2 + 1
                    jy1 = random.randint(y1, y1_2)
                    jx2 = random.randint(x2, x2_2)
                    jy2 = y2 - 1
                    corridors = self.corridor_between_points(
                        jx1, jy1, jx2, jy2, 'bottom')
                    self.corridor_list.append(corridors)
                else:
                    jx1 = random.randint(x1, x1_2)
                    jy1 = y1 - 1
                    jx2 = x2 - 1
                    jy2 = random.randint(y2, y2_2)
                    corridors = self.corridor_between_points(
                        jx1, jy1, jx2, jy2, 'top')
                    self.corridor_list.append(corridors)

            elif join == 'bottom':
                if y2 > y1:
                    jx1 = random.randint(x1, x1_2)
                    jy1 = y1_2 + 1
                    jx2 = x2 - 1
                    jy2 = random.randint(y2, y2_2)
                    corridors = self.corridor_between_points(
                        jx1, jy1, jx2, jy2, 'top')
                    self.corridor_list.append(corridors)
                else:
                    jx1 = x1_2 + 1
                    jy1 = random.randint(y1, y1_2)
                    jx2 = random.randint(x2, x2_2)
                    jy2 = y2_2 + 1
                    corridors = self.corridor_between_points(
                        jx1, jy1, jx2, jy2, 'bottom')
                    self.corridor_list.append(corridors)

    def gen_level(self):
        # build an empty dungeon, blank the room and corridor lists
        for _ in range(self.height):
            self.level.append([' '] * self.width)

        max_iters = self.max_rooms * 5

        for a in range(max_iters):
            tmp_room = self.gen_room()

            if self.rooms_overlap or not self.room_list:
                self.room_list.append(tmp_room)
            else:
                tmp_room = self.gen_room()
                tmp_room_list = self.room_list[:]

                if self.room_overlapping(tmp_room, tmp_room_list) is False:
                    self.room_list.append(tmp_room)

            if len(self.room_list) >= self.max_rooms:
                break

        # connect the rooms
        for a in range(len(self.room_list) - 1):
            self.join_rooms(self.room_list[a], self.room_list[a + 1])

        # do the random joins
        for a in range(self.random_connections):
            room_1 = self.room_list[random.randint(0, len(self.room_list) - 1)]
            room_2 = self.room_list[random.randint(0, len(self.room_list) - 1)]
            self.join_rooms(room_1, room_2)

        # do the spurs
        for a in range(self.random_spurs):
            room_1 = [random.randint(2, self.width - 2), random.randint(
                2, self.height - 2), 1, 1]
            room_2 = self.room_list[random.randint(0, len(self.room_list) - 1)]
            self.join_rooms(room_1, room_2)

        # fill the map
        # paint rooms

        for room in self.room_list:
            for b, c in product(range(room[2]), range(room[3])):
                self.level[room[1] + c][room[0] + b] = '.'

        # paint corridors
        for corridor in self.corridor_list:
            (x1, y1), (x2, y2), *_ = corridor
            for width, height in product(range(abs(x1 - x2) + 1),
                                         range(abs(y1 - y2) + 1)):
                self.level[min(y1, y2) + height][
                    min(x1, x2) + width] = '.'

            if len(corridor) == 3:
                x3, y3 = corridor[2]

                for width, height in product(range(abs(x2 - x3) + 1),
                                             range(abs(y2 - y3) + 1)):
                    self.level[min(y2, y3) + height][
                        min(x2, x3) + width] = '.'

        # paint the walls
        for row, col in product(range(1, self.height - 1), range(1, self.width - 1)):
            if self.level[row][col] == '.':
                for x, y in product(range(row - 1, row + 2), range(col - 1, col + 2)):
                    if x or y:
                        if self.level[x][y] == ' ':
                            self.level[x][y] = '#'

        # Генерация кустов
        for x, y, *size in self.room_list:
            while random.randint(0, 4):
                pos = x2, y2 = tuple((random.randint(
                    0, n - self.min_bushes_xy)) for n in size)
                w2, h2 = (random.randint(self.min_bushes_xy, abs(b - a))
                          for a, b in zip(pos, size))
                for x3, y3 in product(range(w2), range(h2)):
                    x4, y4 = x3 + x2 + x, y3 + y2 + y
                    collides_walls = any(map(WALL_CELLS.__contains__, [
                                         self.level[y5][x5] for y5, x5 in product(range(y4-1, y4+2), range(x4-1, x4+2))]))
                    if y4 < len(self.level) and x4 < len(self.level[y4]) and not collides_walls:
                        self.level[y4][x4] = "b"

        # Генерация стекла
        for y, x in product(range(1, self.height - 1), range(1, self.width - 1)):
            if self.level[y + 1][x] in FLOOR_CELLS\
                    and self.level[y - 1][x] in FLOOR_CELLS\
                    and self.level[y][x + 1] in (WALL_CELLS)\
                    and self.level[y][x - 1] in (WALL_CELLS)\
                    and self.level[y][x] == "#":
                self.level[y][x] = "G"

        # Размещение терминалов
        for t in ("t", "T"):
            while True:
                x, y, w, *_ = random.choice(self.room_list)
                additional_x = random.randint(0, w)

                while self.level[y - 1][x + additional_x] not in WALL_CELLS:
                    y -= 1

                if self.level[y][x] != "b":
                    x += additional_x
                    break
            self.level[y][x] = t

            for x2, y2 in product(range(-1, 2), range(2)):
                if self.level[y + y2][x + x2] in FLOOR_CELLS:
                    self.level[y + y2][x + x2] = "."

    def gen_tiles_level(self) -> RoguelikeMap:
        self.gen_level()
        return RoguelikeMap(self.level, self.room_list,
                            self.corridor_list, (self.width, self.height))
