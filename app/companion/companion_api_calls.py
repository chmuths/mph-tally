import time
from companion.companion_service import CompanionService, ConnectionException, ServerErrorException


class CompanionAPI:
    def __init__(self, companion_config, logger):
        self.instance_companion = CompanionService(companion_config, logger)
        self.logger = logger

    def press_key(self, bank, btn_number, state):
        """
        This method calls the user_engine endpoint api_path to retrieve the requested object
        :param parameter: dict of parameters
        :return: request response
        """
        try:
            item = self.instance_companion.get_request(bank, btn_number, state)
        except ConnectionException as e:
            self.logger.warning(f"Connection Exception while GET. {str(e)}")
            return None
        except ServerErrorException as e:
            self.logger.warning(f"Server Error Exception while GET. {str(e)}")
            return None
        return item
