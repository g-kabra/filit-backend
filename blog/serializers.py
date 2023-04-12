from rest_framework import serializers

from .models import blogModel


class BlogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = blogModel
        fields = ['title', 'author', 'read_time',
                  'slug', 'created_on', 'updated_on']


class BlogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = blogModel
        fields = '__all__'

    def create(self, validated_data):
        Blog = blogModel
        blog = Blog.objects.create(**validated_data)
        return blog
