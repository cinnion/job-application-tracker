import logging

from django.http import Http404


class Log404Mixin:
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
        try:
            # noinspection PyUnresolvedReferences
            response = super().dispatch(request, *args, **kwargs)
            if response.status_code == 404:  # pragma: no cover - The code currently only raises Http404 exceptions.
                self.__logger.warning(
                    f"404 Error in {self.__class__.__name__} at {request.path} by {request.user.username} (id={request.user.id}) on id={kwargs["appid"]}"
                )
            return response
        except Http404 as e:
            self.__logger.warning(
                f"Http404 raised in {self.__class__.__name__} by {request.user.username} (id={request.user.id}) on id={kwargs["appid"]}: {e}")
            raise  # Re-raise so Django handles the 404 response
