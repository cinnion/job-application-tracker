from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class JobApplication(models.Model):
    """
    A database record for storing information about job applications.
    """
    class Meta:
        db_table = "job_applications"

    id = models.BigAutoField(
        _("id"),
        primary_key=True,
        help_text=_(
            "The primary key for the job application"
        ),
        db_comment="Primary key",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user id"),
        related_name="job_applications",
        db_comment="The user who submitted the application."
    )
    when = models.DateField(
        _("when"),
        default=localtime,
        blank=True,
        help_text=_(
            "The date when the application was submitted"
        ),
        db_comment="Date of application."
    )
    company = models.CharField(
        _("company name"),
        max_length=64,
        help_text=_(
            "The name of the company."
        ),
        db_comment="Name of company."
    )
    title = models.CharField(
        _("job title"),
        max_length=128,
        help_text=_(
            "The job title."
        ),
        db_comment="Job title."
    )
    posting = models.URLField(
        _("job posting url"),
        blank=True,
        null=True,
        help_text=_(
            "The URL for the job posting, if applicable. Use notes for other job sources"
        ),
        db_comment="URL of job posting, if applicable."
    )
    confirm = models.URLField(
        _("confirmation email url"),
        blank=True,
        null=True,
        help_text=_(
            "The URL of the confirmation email"
        ),
        db_comment="URL for application confirmation, if applicable."
    )
    notes = models.TextField(
        _("notes"),
        max_length=4096,
        blank=True,
        null=True,
        help_text=_(
            "Notes about this job, such as alternate sources, expected salary, etc."
        ),
        db_comment="Notes"
    )
    active = models.BooleanField(
        _("application still active"),
        default=True,
        help_text=_(
            "True if the job application is still potentially active"
        ),
        db_comment="Application is still outstanding."
    )
    interviews = models.PositiveSmallIntegerField(
        _("interviews"),
        default=0,
        help_text=_(
            "The number of interviews. More details like dates can go in the notes field."
        ),
        db_comment="The number of interviews for the job."
    )
    rejected = models.DateField(
        _("rejection date"),
        blank=True,
        null=True,
        help_text=(
            "When a job rejection letter was received"
        ),
        db_comment="Date of rejection notice."
    )
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
        null=True,
        help_text=_(
            "When the record was created"
        ),
        db_comment="Record created at.",
    )
    updated_at = models.DateTimeField(
        _("updated_at"),
        auto_now=True,
        help_text=_(
            "When the record was last updated",
        ),
        db_comment="Record last updated at."
    )

    @property
    def interviewed(self) -> bool:
        """
        Whether we have interviewed for the job.
        """
        if self.interviews > 0:
            return True

        return False

    def __str__(self):
        """
        Method used when converting to a string. Only return a far simpler representation
        of the record in this instance.
        """
        return f"{self.when}: {self.title} @ {self.company}".format(self.when, self.title, self.company)
