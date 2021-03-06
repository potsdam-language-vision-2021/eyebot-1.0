"""
    Avatar action routines
"""

import logging
from avatar.dialogue.dummy_dialogue_manager import DummyDialogueManager
from avatar.vqa.dummy_model import DummyVQA

from avatar.dialogue.rasa_dialogue_manager import RasaDialogueManager
from avatar.vqa.oscar_api import OscarModel

log = logging.getLogger(__name__)

DIRECTION_TO_WORD = {
    "n": "north",
    "e": "east",
    "w": "west",
    "s": "south"
}


def direction_to_word(direction: str):
    if direction in DIRECTION_TO_WORD:
        return DIRECTION_TO_WORD[direction]
    return direction


def directions_to_sent(directions: str):
    if not directions:
        return "nowhere"
    n = len(directions)
    if n == 1:
        return direction_to_word(directions[0])
    words = [direction_to_word(d) for d in directions]
    return ", ".join(words[:-1]) + " or " + words[-1]


class Avatar(object):
    """
        The avatar methods to be implemented
    """

    def step(self, observation: dict) -> dict:
        """
        The current observation for the avatar.

        For new player messages only the 'message' will be given.
        For new situations the 'image' and 'directions' will be given.

        The agent should return a dict with "move" or "response" keys.
        The response will be sent to the player.
        The move command will be executed by the game master.
        Possible move commands are: {"n": "north", "e": "east", "w": "west", "s": "south"}

        :param observation: {"image": str, "directions": [str], "message": str }
        :return: a dict with "move" and/or "response" keys; the dict could also be empty to do nothing
        """
        raise NotImplementedError("step")


class SimpleAvatar(Avatar):
    """
        The simple avatar is only repeating the observations.
    """

    def __init__(self, image_directory):
        self.image_directory = image_directory
        self.observation = None

        self.dialogue_manager = DummyDialogueManager()
        self.vqa_model = DummyVQA()

    def step(self, observation: dict) -> dict:
        log.debug("step observation: %s", observation)  # for debugging
        actions = dict()
        if observation["image"]:
            self.__update_observation(observation)
        if observation["message"]:
            self.__update_actions(actions, observation["message"])
        return actions

    def __update_observation(self, observation: dict):
        log.debug("__update_observation observation: %s", observation)
        self.observation = observation

    def __update_actions(self, actions, message):
        log.debug("__update_actions actions: %s", actions)
        log.debug("__update_actions message: %s", message)
        if "go" in message.lower():
            actions["move"] = self.__predict_move_action(message)
        else:
            actions["response"] = self.__generate_response(message)

    def __generate_response(self, message: str) -> str:
        log.debug("__generate_response message: %s", message)
        message = message.lower()

        if message.startswith("what"):
            if self.observation:
                return "I see " + self.observation["image"]
            else:
                return "I dont know"

        if message.startswith("where"):
            if self.observation:
                return "I can go " + directions_to_sent(self.observation["directions"])
            else:
                return "I dont know"

        if message.endswith("?"):
            if self.observation:
                return "It has maybe something to do with " + self.observation["image"]
            else:
                return "I dont know"

        return "I do not understand"

    def __predict_move_action(self, message: str) -> str:
        log.debug("__predict_move_action message: %s", message)
        if "north" in message:
            return "n"
        if "east" in message:
            return "e"
        if "west" in message:
            return "w"
        if "south" in message:
            return "s"
        return "nowhere"


class EyebotAvatar(Avatar):
    def __init__(self, image_directory):
        self.image_directory = image_directory
        self.image = None
        self.directions = None
        self.observation = None
        self.dialogue_manager = RasaDialogueManager.create(
            "http://localhost:5005/model/parse",
            OscarModel("http://localhost:5000")
        )

    def step(self, observation: dict) -> dict:
        log.debug("step observation: %s", observation)  # for debugging
        actions = {}

        # observation: {"image": str, "directions": [str], "message": str }

        if observation["image"]:
            self.image = observation["image"]
        if observation["directions"]:
            self.directions = observation["directions"]
        if observation["message"]:
            direction, response = self.dialogue_manager.generate_action_and_response(
                self.image,
                self.directions,
                observation["message"]
            )
            if direction is not None:
                actions["move"] = direction
            if response is not None:
                actions["response"] = response

        # move" and/or "response"
        return actions

    def __update_observation(self, observation: dict):
        log.debug("__update_observation observation: %s", observation)
        self.observation = observation