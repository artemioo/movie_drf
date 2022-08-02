from django.db import models
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Movie, Actor
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewCreateSerializer, CreateRatingSerializer, \
    ActorListSerializer, ActorDetailSerializer
from .service import get_client_ip, MovieFilter


class MovieListView(generics.ListAPIView):
    """ Вывод списка фильмов """
    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter
    permission_classes = [permissions.IsAuthenticated] # какие правда доступа должны быть, чтоб просмотреть данный url

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )

            # rating_user=models.Case( # придуманное поле, добавляется к каждому объекту Movie
            #     models.When(ratings__ip=get_client_ip(request), then=True),  # если юзер поставил оценку, будет True
            #     default=False,
            #     output_field=models.BooleanField()
        return movies


class MovieDetailView(generics.RetrieveAPIView):
    """ Вывод информации о фильме """
    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer


# class ActorListView(APIView):
#     """ Вывод информации о фильме """
#     def get(self, request):
#         actor = Actor.objects.all()
#         serializer = ActorListSerializer(actor)
#         return Response(serializer.data)


class ActorListView(generics.ListAPIView):
    """ Вывод списка Актеров и Режиссеров """
    queryset = Actor.objects.all()
    serializer_class = ActorListSerializer


class ActorDetailView(generics.RetrieveAPIView):
    """ Вывод информации об Актере или Режиссере """
    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer


class ReviewCreateView(generics.CreateAPIView):
    """ Добавление отзыва """
    serializer_class = ReviewCreateSerializer


class AddStarRatingView(generics.CreateAPIView):
    """ Добавление рейтинга к фильму """
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


