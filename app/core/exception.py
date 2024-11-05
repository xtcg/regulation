from utilswaves.exceptions import FastAPIBaseException


class BadRequest(FastAPIBaseException):
    CODE = 400
    STATUS_CODE = 400
    MESSAGE = "Bad Request"


class ServerException(FastAPIBaseException):
    CODE = 500
    STATUS_CODE = 500
    MESSAGE = "Internal Server Error"


class NoFound(FastAPIBaseException):
    CODE = 404
    MESSAGE = "Not Found"


class PositionNoFound(NoFound):
    CODE = 40401
    MESSAGE = "position not found"


class CharacterNoFound(NoFound):
    CODE = 40402
    MESSAGE = "character not found"


class SceneNoFound(NoFound):
    CODE = 40403
    MESSAGE = "scene not found"


class MessageNoFound(NoFound):
    CODE = 40404
    MESSAGE = "message not found"


class SessionNoFound(NoFound):
    CODE = 40405
    MESSAGE = "session not found"


class CourseNoFound(NoFound):
    CODE = 40406
    MESSAGE = "course not found"


class InvalidFile(BadRequest):
    CODE = 40407
    MESSAGE = "Invalid File Type"


class TaskNoFound(NoFound):
    CODE = 40408
    MESSAGE = "task not found"


class InsufficientDialogRounds(BadRequest):
    CODE = 40409
    MESSAGE = "Insufficient dialog rounds"


class VolcClientError(ServerException):
    CODE = 50001
