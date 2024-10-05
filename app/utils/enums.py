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

class EasyFigureType(Enum):
    ETYPE1 = "EType 1"
    ETYPE2 = "EType 2"
    ETYPE3 = "EType 3"
    ETYPE4 = "EType 4"
    ETYPE5 = "EType 5"
    ETYPE6 = "EType 6"
    ETYPE7 = "EType 7"

class FigureStatus(Enum):
    DISCARDED = "Discarded"
    BLOCKED = "Blocked"
    INHAND = "In Hand"
    INDECK = "In Deck"

class ValidMoves(Enum):
    mov1 = { (2, -2), (-2, 2), (-2, -2), (2, 2) }
    mov2 = { (2, 0), (-2, 0), (0, 2), (0, -2) }
    mov3 = { (1, 0), (-1, 0), (0, 1), (0, -1) }
    mov4 = { (1, 1), (-1, -1), (1, -1), (-1, 1) }
    mov5 = { (-2, 1), (2, -1), (-1, -2), (1, 2) }
    mov6 = { (-2, -1), (2, 1), (-1, 2), (1, -2) }
    mov7 = { (4, 0), (-4, 0), (0, 4), (0, -4) }