from enum import Enum

class Message(Enum):
    NOT_IN_CHANNEL = "I am currently not in a channel."
    USER_NOT_IN_CHANNEL = "You are currently not in a voice channel."