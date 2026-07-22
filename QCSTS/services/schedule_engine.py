import logging
from dateutil.relativedelta import relativedelta
from django.db import transaction

from constants.stability import StudyType, ICHTimepoints
from core.exceptions import ScheduleGenerationError, InvalidStudyType

logger = logging.getLogger(__name__)


class ScheduleEngine:
    """
    Generates ICH stability test points for a batch.

    Rules:
    - Called ONLY when a batch is created — never manually
    - All test points created in one atomic transaction
    - If any point fails to create, ALL are rolled back
    - Test points cannot be created or deleted via API

    Usage:
        from services.schedule_engine import ScheduleEngine
        ScheduleEngine.generate(batch, created_by=request.user)
    """

    # Maps study type to ICH timepoints
    TIMEPOINTS_MAP = {
        StudyType.LONG_TERM: ICHTimepoints.LONG_TERM,
        StudyType.ACCELERATED: ICHTimepoints.ACCELERATED,
    }

    @classmethod
    def generate(cls, batch, created_by=None):
        """
        Generates all test points for a batch.

        Args:
            batch: Batch instance — must have incubation_date and study_type
            created_by: User who triggered this (for audit trail)

        Returns:
            List of created TestPoint instances

        Raises:
            InvalidStudyType: if study_type is not recognized
            ScheduleGenerationError: if creation fails for any reason
        """
        from apps.schedule.models import TestPoint

        # Validate study type
        months = cls.TIMEPOINTS_MAP.get(batch.study_type)
        if months is None:
            raise InvalidStudyType(f"Unknown study type: {batch.study_type}")

        try:
            with transaction.atomic():
                test_points = []

                for month in months:
                    # Calculate exact date for this timepoint
                    scheduled_date = batch.incubation_date + relativedelta(months=month)

                    tp = TestPoint.objects.create(
                        batch=batch,
                        month=month,
                        scheduled_date=scheduled_date,
                        status="pending",
                        created_by=created_by,
                    )
                    test_points.append(tp)

                logger.info(
                    "ScheduleEngine: generated %d test points for batch %s",
                    len(test_points),
                    batch.batch_number,
                )
                return test_points

        except InvalidStudyType:
            raise
        except Exception as e:
            logger.error("ScheduleEngine failed for batch %s: %s", batch.batch_number, str(e))
            raise ScheduleGenerationError(
                f"Failed to generate schedule for batch {batch.batch_number}"
            )
