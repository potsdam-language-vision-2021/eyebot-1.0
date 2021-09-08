from dataclasses import dataclass
import logging
import urllib.parse

import requests
from avatar.vqa.oscar_api import OscarModel


log = logging.getLogger(__name__)


DIRECTION_TO_WORD = {
    "n": "north",
    "e": "east",
    "w": "west",
    "s": "south"
}


@dataclass
class RasaDialogueManager:
    endpoint: str
    session: requests.Session
    oscar_api: OscarModel

    @classmethod
    def create(cls, endpoint, oscar_api):
        return cls(endpoint, requests.Session(), oscar_api)

    def generate_action_and_response(self, image, directions, message):
        # TODO: make request to rasa NLU endpoint

        # curl -s -XPOST http://localhost:5005/model/parse -d '{"text": "can i go north","message_id": "b2831e73-1407-4ba0-a861-0f30a42a2a5a"}'| jq

        # look at keys "intent" and "entities"
        # if intent == go or inquire_direction, then there should be an entity with key "entity": "direction"; get its key "value"

        req = self.session.post(self.endpoint, json={"text": message, "message_id": "b2831e73-1407-4ba0-a861-0f30a42a2a5a"})
        res = req.json()

        intent = res["intent"]["name"]
        entities = res["entities"]
        direction_entities = [e for e in entities if e["entity"] == "direction"]
        has_direction_entity = len(direction_entities) == 1
        direction_entity = direction_entities[0]["value"] if has_direction_entity else None

        if intent == "ask_general":
            # request to caption api
            direction = None
            image_as_id = urllib.parse.unquote(image).split("/")[-1].split(".")[0]
            oscar_api_caption = self.oscar_api.get_caption(image_as_id)
            message = oscar_api_caption.json()
        elif intent == "ask_specific":
            # request to vqa api
            direction = None
            image_as_id = urllib.parse.unquote(image).split("/")[-1].split(".")[0]
            oscar_api_answer = self.oscar_api.answer_question(image_as_id, message)
            message = oscar_api_answer.json()
        elif intent == "inquire_direction":
            if direction_entity is None:
                direction = None
                message = f"I can go {','.join(DIRECTION_TO_WORD[d] for d in directions)}."
            elif direction_entity not in ["north", "south", "east", "west"]:
                log.warning("Get unknown direction %s from rasa with message %s", repr(direction_entity), repr(message))
                direction = None
                message = f"I'm not sure I understand you. I can go {','.join(DIRECTION_TO_WORD[d] for d in directions)}."
            else:
                can_go = direction_entity[0] in directions
                direction = None
                message = f"I can go {direction_entity}" if can_go else f"I cannot go {direction_entity}"
        elif intent == "go":
            can_go = direction_entity[0] in directions
            if can_go:
                direction = direction_entity[0]
                message = f"Ok, going {direction_entity}"
            else:
                direction = None
                message = f"I cannot go {direction_entity}"
        else:
            log.warning("Get unknown intent %s from rasa with message %s", repr(intent), repr(message))
            direction = None
            message = "Something went wrong. Can you rephrase that?"

        return direction, message
