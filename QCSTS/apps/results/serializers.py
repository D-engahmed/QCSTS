from rest_framework import serializers
from apps.results.models import TestResult, ResultReview, ResultCorrection
from apps.schedule.models import TestPoint
from core.exceptions import ResultAlreadySubmitted
from core.serializers import TenantScopedModelSerializer
from services.outcome_evaluator import OutcomeEvaluator

class TestResultSerializer(TenantScopedModelSerializer):
    analyst_name = serializers.SerializerMethodField()
    test_name = serializers.SerializerMethodField()
    workflow_state = serializers.SerializerMethodField()

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
            "workflow_state",
            "organization"
        ]
        read_only_fields = [
            "id",
            "specification_snapshot",
            "pass_fail",
            "analyst",
            "submitted_at",
            "workflow_state",
            "organization"
        ]

    def get_analyst_name(self, obj):
        return obj.analyst.full_name if obj.analyst else None

    def get_test_name(self, obj):
        return obj.monograph_test.name

    def get_workflow_state(self, obj):
        return obj.workflow_state()

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
        from core.exceptions import EvaluationError
        
        monograph_test = validated_data["monograph_test"]
        validated_data["specification_snapshot"] = monograph_test.specification
        
        try:
            validated_data["pass_fail"] = OutcomeEvaluator.evaluate(
                validated_data["value"],
                monograph_test.specification,
            )
        except EvaluationError as e:
            # Raise a DRF ValidationError so the API returns a clean 400 error
            raise serializers.ValidationError({"value": str(e)})

        result = TestResult.objects.create(**validated_data)
        return result


class ResultReviewSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ResultReview
        fields = [
            "id",
            "result",
            "action",
            "reviewed_by",
            "reviewed_by_name",
            "comments",
            "result_snapshot",
            "reviewed_at",
            "organization",
        ]
        read_only_fields = [
            "id",
            "result",
            "action",
            "reviewed_by",
            "reviewed_by_name",
            "result_snapshot",
            "reviewed_at",
            "organization",
        ]

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.full_name if obj.reviewed_by else None

class ResultCorrectionSerializer(serializers.ModelSerializer):
    corrected_by_name = serializers.SerializerMethodField()
    original_value = serializers.SerializerMethodField()
    corrected_value = serializers.SerializerMethodField()

    class Meta:
        model = ResultCorrection
        fields = [
            "id",
            "original_result",
            "corrected_result",
            "original_value",
            "corrected_value",
            "reason",
            "corrected_by",
            "corrected_by_name",
            "created_at",
            "organization"
        ]
        read_only_fields = fields

    def get_corrected_by_name(self, obj):
        return obj.corrected_by.full_name if obj.corrected_by else None

    def get_original_value(self, obj):
        # Fetch from all_objects since the original is soft-deleted
        return TestResult.all_objects.get(id=obj.original_result_id).value

    def get_corrected_value(self, obj):
        return obj.corrected_result.value