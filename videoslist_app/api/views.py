from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from videoslist_app.api  import pagination, permissions, serializers, throttling
from videoslist_app.models import Review, StreamCompany, VideosList


class UserReview(generics.ListAPIView):
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        return Review.objects.filter(review_user__username=username)


class ReviewCreate(generics.CreateAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [throttling.ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        videosList = VideosList.objects.get(pk=pk)

        review_user = self.request.user
        review_queryset = Review.objects.filter(
            videosList=videosList, review_user=review_user)

        if review_queryset.exists():
            raise ValidationError("You have already reviewed this video!")

        if videosList.number_rating == 0:
            videosList.avg_rating = serializer.validated_data['rating']
        else:
            videosList.avg_rating = (
                videosList.avg_rating + serializer.validated_data['rating'])/2

        videolist.number_rating = videolist.number_rating + 1
        videolist.save()

        serializer.save(videolist=videolist, review_user=review_user)


class ReviewList(generics.ListAPIView):
    serializer_class = serializers.ReviewSerializer
    throttle_classes = [throttling.ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(videolist=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle, AnonRateThrottle]
    throttle_scope = 'review-detail'


class StreamCompanyVS(viewsets.ModelViewSet):
    queryset = StreamCompany.objects.all()
    serializer_class = serializers.StreamCompanySerializer
    permission_classes = [permissions.IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]


class VideoListAV(APIView):
    permission_classes = [permissions.IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        movies = VideosList.objects.all()
        serializer = serializers.VideosListSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.VideosListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class WatchDetailAV(APIView):
    permission_classes = [permissions.IsAdminOrReadOnly]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, pk):
        try:
            movie = VideosList.objects.get(pk=pk)
        except VideosList.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.VideosListSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = VideosList.objects.get(pk=pk)
        serializer = serializers.VideosListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = VideosList.objects.get(pk=pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)