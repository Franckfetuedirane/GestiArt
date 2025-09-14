from rest_framework import serializers
from .models import Artisan
from users.models import User
from users.serializers import UserSerializer

class ArtisanSerializer(serializers.ModelSerializer):
    """
    Serializer for the Artisan model.
    Includes nested UserSerializer for read-only user details.
    Allows specifying user_id for admin users during creation.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True, required=False)

    class Meta:
        """
        Meta class for ArtisanSerializer.
        Defines the model and fields to be serialized.
        """
        model = Artisan
        fields = '__all__'
        read_only_fields = ('user',)
    def get_first_name(self, obj):
        return obj.user.first_name  # Accédez au prénom de l'utilisateur lié
