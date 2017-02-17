from .models import Article
from rest_framework import serializers


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
