from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer
# Create your views here.


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow users to view or edit articles
    """
    queryset = Article.objects.published()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
