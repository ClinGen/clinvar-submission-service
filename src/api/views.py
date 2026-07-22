from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from classification.constants.models import ClassificationStatus
from classification.models import Classification
from classification.serializers import ClassificationSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


class ClassificationCreateView(APIView):
    permission_classes = [HasAPIKey]

    def post(self, request):
        serializer = ClassificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        local_id = serializer.validated_data["local_id"]
        if Classification.objects.filter(local_id=local_id).exists():
            return Response(
                {"detail": f"Classification with local_id '{local_id}' already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        classification = serializer.save()
        return Response(
            {"local_id": str(classification.local_id), "status": "pending"},
            status=status.HTTP_201_CREATED,
        )


class ClassificationUpdateView(APIView):
    permission_classes = [HasAPIKey]

    def put(self, request, local_id):
        try:
            classification = Classification.objects.get(local_id=local_id)
        except Classification.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if classification.status != Classification.Status.PENDING:
            return Response(
                {
                    "detail": f"Classification cannot be updated in status '{ClassificationStatus(classification.status).label}'."
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ClassificationSerializer(classification, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        classification = serializer.save()
        return Response(
            {"local_id": str(classification.local_id), "status": "pending"},
            status=status.HTTP_200_OK,
        )
