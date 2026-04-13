"""
A mixin for catching and handling Http404 exceptions in a view class.
"""
import logging

from django.http import Http404


class Log404Mixin:  # pylint: disable=too-few-public-methods
    """
    A mixin to catch 404 errors and log them along with the user who tried to do something which caused it to happen.

    NOTE: Unauthenticated users will not get this far, due to the LoginRequiredMixin redirecting them to authenticate.
    """

    def __init__(self):
        """
        Create a logger instance which is specific to the module of the class using this mixin, but scoped to be for
        this mixin, so that we do not overwrite the same property in that class.
        """
        super().__init__()
        self.__logger = logging.getLogger(self.__module__)

    def dispatch(self, request, *args, **kwargs):
        """
        Our extended dispatch method, which uses a try/catch block to catch Http404 exceptions
        or inspects the return code to detect code returning a 404 error that way, and logging
        those errors.

        Args:
            request (HTTPRequest): The request object.
            *args: Any arguments passed to the method.
            **kwargs: Any keyword arguments passed to the method.

        Returns:
            The HTTPResponse

        Raises:
            Http404 if the called method raised it, after logging its occurrence.
        """
        try:
            # noinspection PyUnresolvedReferences
            response = super().dispatch(request, *args, **kwargs)
            if response.status_code == 404:  # pragma: no cover - The code currently only raises Http404 exceptions.
                self.__logger.warning(
                    "404 Error in %s at %s by %s (id=%d) on id=%s",
                    self.__class__.__name__,
                    request.path,
                    request.user.username,
                    request.user.id,
                    kwargs["appid"]
                )
            return response
        except Http404 as e:
            self.__logger.warning(
                "Http404 raised in %s by %s (id=%d) on id=%s: %s",
                self.__class__.__name__,
                request.user.username,
                request.user.id,
                kwargs["appid"],
                e
            )
            raise  # Re-raise so Django handles the 404 response
