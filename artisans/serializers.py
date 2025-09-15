from rest_framework import serializers
from .models import Artisan
from users.models import User
from users.serializers import UserSerializer
from django.conf import settings
from rest_framework import serializers
from .models import Artisan
from users.models import User
from django.contrib.auth.hashers import make_password
# artisans/serializers.py
from rest_framework import serializers
from .models import Artisan
from users.models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            # Ne pas modifier le type d'utilisateur pour les superutilisateurs
        if not instance.is_superuser:
            instance.user_type = 'artisan'
        instance.save()
        return instance
    def update(self, instance, validated_data):
        # Ne pas permettre la modification du mot de passe ici
        validated_data.pop('password', None)
        return super().update(instance, validated_data)

# artisans/serializers.py
class ArtisanSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        fields = '__all__'
        read_only_fields = ('photo_url',)

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        user = None
        
        if user_data and isinstance(user_data, dict):
            # Création d'un nouvel utilisateur
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            user.user_type = 'artisan'
            user.save()
        elif 'user' in validated_data and validated_data['user']:
            # Utilisation d'un utilisateur existant
            user = validated_data.pop('user')
        
        if not user:
            raise serializers.ValidationError({
                "user": "Un utilisateur est requis pour créer un artisan."
            })
        
        return Artisan.objects.create(user=user, **validated_data)