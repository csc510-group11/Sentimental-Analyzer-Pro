"""sentimental_analysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# from django.conf.urls import url

from django.conf import settings
from django.conf.urls.static import static
import realworld.views
from django.contrib.auth import views as auth_views
urlpatterns = [
    # Admin and authentication routes
    path('admin/', admin.site.urls),
    path('auth/', include('authapp.urls')),
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Landing page / index
    path('', realworld.views.index, name='index'),
    
    # Separate pages for each analysis feature
    path('text-analysis/', realworld.views.text_analysis, name='text_analysis'),
    path('image-analysis/', realworld.views.image_analysis, name='image_analysis'),
    path('document-analysis/', realworld.views.document_analysis, name='document_analysis'),
    path('audio-analysis/', realworld.views.audio_analysis, name='audio_analysis'),
    path('video-analysis/', realworld.views.video_analysis, name='video_analysis'),

    # Seprate pages for each review feature: book, movie, product and restaurant
    path('book-review/', realworld.views.book_review, name='book_review'),
    path('movie-review/', realworld.views.movie_review, name='movie_review'),
    path('product-review/', realworld.views.product_review, name='product_review'),
    path('restaurant-review/', realworld.views.restaurant_review, name='restaurant_review')
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
