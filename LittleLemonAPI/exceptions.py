from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    status_code = 400
    default_detail = 'Bad Request'
    default_code = 'bad_request'


class ConflictException(APIException):
    status_code = 409
    default_detail = 'Conflict'
    default_code = 'conflict'


class PreconditionFailedException(APIException):
    status_code = 412
    default_detail = 'Precondition Failed'
    default_code = 'precondition_failed'
