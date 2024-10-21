from enum import Enum

class MovementType(Enum):
    TYPE1 = "Type 1"
    TYPE2 = "Type 2"
    TYPE3 = "Type 3"
    TYPE4 = "Type 4"
    TYPE5 = "Type 5"
    TYPE6 = "Type 6"
    TYPE7 = "Type 7"

class MovementStatus(Enum):
    INHAND = "In Hand"
    INDECK = "In Deck"
    DISCARDED = "Discarded"

class FigureType(Enum):
    TYPE1 = "Type 1"
    TYPE2 = "Type 2"
    TYPE3 = "Type 3"
    TYPE4 = "Type 4"
    TYPE5 = "Type 5"
    TYPE6 = "Type 6"
    TYPE7 = "Type 7"
    TYPE8 = "Type 8"
    TYPE9 = "Type 9"
    TYPE10 = "Type 10"
    TYPE11 = "Type 11"
    TYPE12 = "Type 12"
    TYPE13 = "Type 13"
    TYPE14 = "Type 14"
    TYPE15 = "Type 15"
    TYPE16 = "Type 16"
    TYPE17 = "Type 17"
    TYPE18 = "Type 18"
    TYPE19 = "Type 19"
    TYPE20 = "Type 20"
    TYPE21 = "Type 21"
    TYPE22 = "Type 22"
    TYPE23 = "Type 23"
    TYPE24 = "Type 24"
    TYPE25 = "Type 25"

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