from rest_framework.response import Response
from rest_framework import status


class ResponseHelper:

    def get_status_404(self, msg="No data found"):
        not_found_response = {"message": msg}
        return Response(not_found_response, status=status.HTTP_404_NOT_FOUND)

    def get_status_200(self, msg="success"):
        ok_response = {"message": msg}
        return Response(ok_response, status=status.HTTP_200_OK)

    def get_status_500(self, msg="internal server error" ):
        error_message = {"message": msg}
        return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_status_400(self, msg="invalid data", data=None):
        error_message = {"message": msg, "data": data}
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    def get_status_201(self, msg="success"):
        ok_response = {"message": msg}
        return Response(ok_response, status=status.HTTP_201_CREATED)

    def get_success_with_data(self, data):
        return Response(data, status=status.HTTP_200_OK)

    def get_status_422(self, msg="UNPROCESSABLE ENTITY", data=None):
        error_message = {"message": msg, "data": data}
        return Response(error_message, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def get_status_401(self, msg="Unauthorized"):
        error_message = {"message": msg}
        return Response(error_message, status=status.HTTP_401_UNAUTHORIZED)

    def get_exception_error(self, msg):
        return Response(msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_status_409(self, msg="Conflict"):
        error_message = {"message": msg}
        return Response(error_message, status=status.HTTP_409_CONFLICT)