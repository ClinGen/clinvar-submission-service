from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from curation.constants.models import CurationStatus
from curation.models import Curation
from curation.serializers import CurationSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


class CurationCreateView(APIView):
    permission_classes = [HasAPIKey]

    def post(self, request):
        serializer = CurationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        local_id = serializer.validated_data["local_id"]
        if Curation.objects.filter(local_id=local_id).exists():
            return Response(
                {"detail": f"Curation with local_id '{local_id}' already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        curation = serializer.save()
        return Response(
            {"local_id": str(curation.local_id), "status": "pending"},
            status=status.HTTP_201_CREATED,
        )


class CurationUpdateView(APIView):
    permission_classes = [HasAPIKey]

    def put(self, request, local_id):
        try:
            curation = Curation.objects.get(local_id=local_id)
        except Curation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if curation.status != Curation.Status.PENDING:
            return Response(
                {
                    "detail": f"Curation cannot be updated in status '{CurationStatus(curation.status).label}'."
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = CurationSerializer(curation, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        curation = serializer.save()
        return Response(
            {"local_id": str(curation.local_id), "status": "pending"},
            status=status.HTTP_200_OK,
        )
