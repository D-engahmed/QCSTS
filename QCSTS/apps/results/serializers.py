from rest_framework import serializers
from apps.results.models import TestResult
from apps.schedule.models import TestPoint
from core.exceptions import ResultAlreadySubmitted
from services.outcome_evaluator import OutcomeEvaluator


class TestResultSerializer(serializers.ModelSerializer):
    analyst_name = serializers.SerializerMethodField()
    test_name = serializers.SerializerMethodField()

    class Meta:
        model = TestResult
        fields = [
            "id",
            "test_point",
            "monograph_test",
            "test_name",
            "value",
            "unit",
            "specification_snapshot",
            "pass_fail",
            "analyst",
            "analyst_name",
            "submitted_at",
            "notes",
        ]
        read_only_fields = [
            "id",
            "specification_snapshot",
            "pass_fail",
            "analyst",
            "submitted_at",
        ]

    def get_analyst_name(self, obj):
        return obj.analyst.full_name if obj.analyst else None

    def get_test_name(self, obj):
        return obj.monograph_test.name

    def validate(self, data):
        test_point = data.get("test_point")
        monograph_test = data.get("monograph_test")
        if test_point and monograph_test:
            if TestResult.objects.filter(
                test_point=test_point,
                monograph_test=monograph_test,
            ).exists():
                raise ResultAlreadySubmitted()
        return data

    def create(self, validated_data):
        monograph_test = validated_data["monograph_test"]

        validated_data["specification_snapshot"] = monograph_test.specification
        validated_data["pass_fail"] = OutcomeEvaluator.evaluate(
            validated_data["value"],
            monograph_test.specification,
        )

        # Save the result. The post_save signal in signals.py will
        # call test_point.update_status() and cascade to the batch.
        # Do NOT call update_status() here — that causes a double update.
        result = TestResult.objects.create(**validated_data)
        return result