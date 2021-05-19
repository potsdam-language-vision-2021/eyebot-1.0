from rasa_dialogue_manager import RasaDialogueManager

rdm = RasaDialogueManager()
intent = rdm.classify_intent('hello')
print(intent)
