from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from ads.models import Ad, AdCategory
from ads.serializers import AdSerializer
from users.models import User
from .serializers import SearchLogSerializer
from .models import SearchLog

class AdSearchView(APIView):
    """
    Advanced search engine for ads with full-text search, filters, and relevance ranking.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        location = request.query_params.get('location', None)
        sort_by = request.query_params.get('sort_by', 'relevance')  # relevance, price, created_at

        ads = Ad.objects.filter(status='active')

        # Full-text search
        if query:
            search_vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            ads = ads.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.1).order_by('-rank')

        # Category filter
        if category:
            ads = ads.filter(category__name__iexact=category)

        # Price filters
        if min_price:
            ads = ads.filter(price__gte=min_price)
        if max_price:
            ads = ads.filter(price__lte=max_price)

        # Location filter
        if location:
            ads = ads.filter(location__icontains=location)

        # Sorting
        if sort_by == 'price':
            ads = ads.order_by('price')
        elif sort_by == 'created_at':
            ads = ads.order_by('-created_at')
        elif sort_by == 'relevance' and query:
            ads = ads.order_by('-rank')
        else:
            ads = ads.order_by('-created_at')

        # Log the search
        if request.user.is_authenticated:
            log_data = {
                'user': request.user.id,
                'query': query,
                'filters': {
                    'category': category,
                    'min_price': min_price,
                    'max_price': max_price,
                    'location': location,
                    'sort_by': sort_by,
                }
            }
            serializer = SearchLogSerializer(data=log_data)
            if serializer.is_valid():
                serializer.save()

        serializer = AdSerializer(ads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)