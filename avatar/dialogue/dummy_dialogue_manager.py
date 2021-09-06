from dataclasses import dataclass


@dataclass
class RasaDialogueManager:
    endpoint: str

    def generate_action_and_response(self, message):
        # TODO: m
        return "n", "I do not know"