from enum import Enum

class Message(Enum):
    def bot_format(message):
        """
        Formats the messages
        """
        return message

    NOT_IN_CHANNEL = bot_format("I am currently not in a channel.")
    USER_NOT_IN_CHANNEL = bot_format("You are currently not in a voice channel.")
    NOT_PLAYING = bot_format("I am currently not playing anything")


