from django.urls import path, include
from rest_framework.routers import DefaultRouter
from videoslist_app.api import views


router = DefaultRouter()
router.register('stream/', views.StreamCompanyVS, basename='streamcompany')


urlpatterns = [
    path('', views.VideoListAV.as_view(), name='movie-list'),
    path('<int:pk>/', views.VideoListAV.as_view(), name='movie-detail'),

    path('', include(router.urls)),

    path('<int:pk>/reviews/create/', views.ReviewCreate.as_view(), name='review-create'),
    path('<int:pk>/reviews/', views.ReviewList.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),

    path('user-reviews/', views.UserReview.as_view(), name='user-review-detail'),

]
