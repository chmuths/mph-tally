import requests


class CompanionService:

    def __init__(self, config, logger):
        self._url = f"http://{config['ip']}:{config['port']}/press/bank"
        self.logger = logger

    def update_server(self, config):
        self._url = f"http://{config['ip']}:{config['port']}/press/bank"

    def get_request(self, bank=None, number=None, state=None):
        """
        Call the user engine api GET and return the response
        :param bank: Bank number of button. First bank is 1
        :param number: Number in bank of button. First button is 1
        :param state: If not None, value 'up' pr 'down' to send to companion
        :return: Http Response of the call
        """
        url = self._url
        if state:
            full_url = f"{url}/{bank}/{number}/{state}"
        else:
            full_url = f"{url}/{bank}/{number}"
        self.logger.info(f"Companion API GET to {full_url}")
        try:
            response = requests.get(url=full_url, timeout=10)
        except requests.exceptions.RequestException as e:
            raise ConnectionException(str(e))

        if response.status_code >= 500:
            raise ServerErrorException(code=response.status_code)

        return response


class CompanionException(Exception):
    code = None
    description = None

    def __init__(self, description=None, code=None):
        Exception.__init__(self)
        if description is not None:
            self.description = description
        if code is not None:
            self.code = code

    def __str__(self):
        code = self.code if self.code is not None else '???'
        return f"Companion API Exception ({self.__class__.__name__}) code {code}: {self.description}"


class ConnectionException(CompanionException):
    ...


class ServerErrorException(CompanionException):
    description = "Companion API server error"
