"""
Views for the DRF API for job applications.
"""
from datetime import date
from typing import List, Optional

from django.db.models.query import QuerySet
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from applications.models import JobApplication
from applications_api.serializers import JobApplicationSerializer


class JobApplications(generics.GenericAPIView):
    """
    The view for job applications presented through the DRF API.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self) -> QuerySet:
        """
        This view will return a QuerySet of all the applications made by the currently authenticated user.
        """
        user_id = self.request.user.id
        return JobApplication.objects.filter(user_id=user_id)

    @staticmethod
    def get_sort(request: Request) -> Optional[List[str]]:
        """
        Parse the request to get the ordering information and return it in a Django compliant list.
        The method returns None if there is no sorting requested.

        :param request:
        :return:
        """
        sort_order = []
        i = 0
        name = request.GET.get(f"order[{i}][name]")
        while name is not None:
            direction = request.GET.get(f"order[{i}][dir]")
            if direction == 'desc':
                sort_order.append('-' + name)
            else:
                sort_order.append(name)
            i += 1
            name = request.GET.get(f"order[{i}][name]")

        if len(sort_order) == 0:
            sort_order = None

        return sort_order

    def get(self, request: Request) -> Response:
        """
        Our GET request handler for the API.

        Args:
            request (Request): The API request.

        Returns:

        """
        draw = int(request.GET.get("draw", 1))
        start_num = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        end_num = start_num + length
        search_param = request.GET.get("search[value]")
        job_applications = self.get_queryset()
        total_applications = job_applications.count()
        total_filtered = total_applications
        sort_order = self.get_sort(request)

        if search_param:
            job_applications = job_applications.filter(company__icontains=search_param)
            total_filtered = job_applications.count()

        if sort_order:
            job_applications = job_applications.order_by(*sort_order)

        serializer = self.serializer_class(job_applications[start_num:end_num], many=True)

        return Response(
            {
                "status": "success",
                "draw": draw,
                "recordsTotal": total_applications,
                "recordsFiltered": total_filtered,
                "job_applications": serializer.data,
            }
        )

    def post(self, request: Request) -> Response:  # pragma: no cover
        """
        This method is currently not used, and is blocked from being run by the http_method_names property.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['when'] = date.today()
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "job_application": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "fail",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class JobApplicationDetail(generics.GenericAPIView):  # pragma: no cover
    """
    This class is currently not used
    """
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all()
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_application(pk: int) -> JobApplication | None:
        """
        A common method to get a job application by its primary key.

        Args:
            pk (int): The primary key

        Returns:
            A Response object containing the job application.

        """
        # noinspection PyBroadException
        try:
            return JobApplication.objects.get(pk=pk)
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get(self, request: Request, pk: int) -> Response:
        """
        A HTTP get handler to get a job application.

        Args:
            request (Request): Our request
            pk (int): The primary key

        Returns:
            The response object.

        """
        job_application = self.get_application(pk=pk)
        if job_application is None:
            return Response(
                {
                    "status": "fail",
                    "message": f"Job Application with Id: {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(job_application)
        return Response(
            {
                "status": "success",
                "job_application": serializer.data,
            }
        )

    def patch(self, request: Request, pk: int) -> Response:
        """
        The HTTP PATCH request handler.

        Args:
            request (Request): The request object.
            pk (int): The primary key.

        Returns:
            The response object.

        """
        job_application = self.get_application(pk=pk)
        if job_application is None:
            return Response(
                {
                    "status": "fail",
                    "message": f"Job Application with Id: {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "job_application": serializer.data,
                },
            )

        return Response(
            {
                "status": "fail",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request: Request, pk: int) -> Response:
        """
        The HTTP delete method handler.

        Args:
            request (Request): The request object.
            pk (int): The primary key.

        Returns:
            The reponse object.

        """
        job_application = self.get_application(pk=pk)
        if job_application is None:
            return Response(
                {
                    "status": "fail",
                    "message": f"Job Application with Id: {pk} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        job_application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
