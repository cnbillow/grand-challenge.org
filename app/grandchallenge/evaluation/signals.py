from typing import Union

from django.db.models.signals import post_save
from django.dispatch import receiver

from grandchallenge.core.utils import disable_for_loaddata
from grandchallenge.evaluation.emails import send_new_result_email
from grandchallenge.evaluation.models import (
    Submission,
    Job,
    Method,
    Result,
    Config,
)
from grandchallenge.evaluation.tasks import calculate_ranks


@receiver(post_save, sender=Submission)
@disable_for_loaddata
def create_evaluation_job(
    instance: Submission = None, created: bool = False, *_, **__
):
    if created:
        method = (
            Method.objects.filter(challenge=instance.challenge)
            .order_by("-created")
            .first()
        )

        if method is None:
            # TODO: Email here, do not raise
            # raise NoMethodForChallengeError
            pass
        else:
            Job.objects.create(submission=instance, method=method)


@receiver(post_save, sender=Config)
@receiver(post_save, sender=Result)
@disable_for_loaddata
def recalculate_ranks(instance: Union[Result, Config] = None, *_, **__):
    """Recalculates the ranking on a new result"""
    calculate_ranks.apply_async(kwargs={"challenge_pk": instance.challenge.pk})


@receiver(post_save, sender=Result)
@disable_for_loaddata
def cache_absolute_url(instance: Result = None, *_, **__):
    """Cache the absolute url to speed up the results page, needs the pk of
    the result so cannot so into a custom save method"""
    Result.objects.filter(pk=instance.pk).update(
        absolute_url=instance.get_absolute_url()
    )


@receiver(post_save, sender=Result)
@disable_for_loaddata
def result_created_email(instance: Result, created: bool = False, *_, **__):
    if created:
        # Only send emails on created, as EVERY result for this challenge is
        # updated when the results are recalculated
        send_new_result_email(instance)
