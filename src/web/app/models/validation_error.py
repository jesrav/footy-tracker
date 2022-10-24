import ast


class ValidationError(Exception):
    def __init__(self, error_msg: str, status_code: int):
        super().__init__(error_msg)

        self.status_code = status_code
        self.error_msg = self._parse_error_message(error_msg)

    @staticmethod
    def _parse_error_message(error_msg):
        error_dict = ast.literal_eval(error_msg)
        if 'detail' not in error_dict:
            return error_msg
        else:
            if isinstance(error_dict['detail'], list):
                return error_dict['detail'][0]["msg"]
            else:
                return error_dict['detail']
