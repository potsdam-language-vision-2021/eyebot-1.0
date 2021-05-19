import config
import requests as req

class RasaDialogueManager:
    def classify_intent(self, text):
        response = self.__ask_server(text)
        intent = self.__parse_intent(response)
        return intent
    
    def __ask_server(self, text):
        payload = '{ "text" : "' + text + '" }'
        req_url = 'http://' + config.RASA_CONFIG['host'] + (':' + str(config.RASA_CONFIG['port']) if config.RASA_CONFIG['port'] else '') + '/model/parse'
        r = req.post(req_url, data=payload)
        return r

    def __parse_intent(self, response):
        response_object = response.json()
        intent = response_object['intent']['name']
        return intent

    


