from enum import Enum

class MovementType(Enum):
    TYPE1 = 1
    TYPE2 = 2
    TYPE3 = 3
    TYPE4 = 4
    TYPE5 = 5
    TYPE6 = 6
    TYPE7 = 7

class MovementStatus(Enum):
    INHAND = "In Hand"
    INDECK = "In Deck"
    DISCARDED = "Discarded"

class FigureType(Enum):
    TYPE1 = 1
    TYPE2 = 2
    TYPE3 = 3
    TYPE4 = 4
    TYPE5 = 5
    TYPE6 = 6
    TYPE7 = 7
    TYPE8 = 8
    TYPE9 = 9
    TYPE10 = 10
    TYPE11 = 11
    TYPE12 = 12
    TYPE13 = 13
    TYPE14 = 14
    TYPE15 = 15
    TYPE16 = 16
    TYPE17 = 17
    TYPE18 = 18
    TYPE19 = 19
    TYPE20 = 20
    TYPE21 = 21
    TYPE22 = 22
    TYPE23 = 23
    TYPE24 = 24
    TYPE25 = 25

class FigureStatus(Enum):
    BLOCKED = "Blocked"
    INHAND = "In Hand"
    INDECK = "In Deck"

class ValidMoves(Enum):
    TYPE1 = { (2, -2), (-2, 2), (-2, -2), (2, 2) }
    TYPE2 = { (2, 0), (-2, 0), (0, 2), (0, -2) }
    TYPE3 = { (1, 0), (-1, 0), (0, 1), (0, -1) }
    TYPE4 = { (1, 1), (-1, -1), (1, -1), (-1, 1) }
    TYPE5 = { (-2, 1), (2, -1), (-1, -2), (1, 2) }
    TYPE6 = { (-2, -1), (2, 1), (-1, 2), (1, -2) }
    TYPE7 = { (4, 0), (-4, 0), (0, 4), (0, -4) }