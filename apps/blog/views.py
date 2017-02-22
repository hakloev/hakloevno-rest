from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer
# Create your views here.


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allow users to view all articles
    ReadOnly in order to ensure no unauthorized editing
    """
    queryset = Article.objects.published()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
