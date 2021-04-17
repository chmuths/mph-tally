import time
from companion.companion_service import CompanionService, ConnectionException, ServerErrorException


class CompanionAPI:
    def __init__(self, companion_config):
        self.instance_companion = CompanionService(companion_config)

    def press_key(self, bank, btn_number, state):
        """
        This method calls the user_engine endpoint api_path to retrieve the requested object
        :param parameter: dict of parameters
        :return: request response
        """
        try:
            item = self.instance_companion.get_request(bank, btn_number, state)
        except ConnectionException as e:
            print(f"Connection Exception while GET. {str(e)}")
            return None
        except ServerErrorException as e:
            print(f"Server Error Exception while GET. {str(e)}")
            return None
        return item


if __name__ == '__main__':
    config = {
        "companion": {"ip": "192.168.0.7",
         "port": "8888"}
    }
    companion = CompanionAPI(config)

    time.sleep(1)
    print("*******************************")
    companion.press_key(1, 2, 'down')
    time.sleep(2)
    print("*******************************")
    companion.press_key(1, 2, 'up')
    time.sleep(2)
    print("*******************************")
