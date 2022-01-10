from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from .models import Follow


User = get_user_model()


class FoodgramUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed'
            )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_is_subscribed(self, following):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        result = user.is_authenticated
        if result:
            result = Follow.objects.filter(user=user, following=following).exists()
        return result


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=None
    )

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, attrs):
        if self.context['request'].user.id == int(self._context['view'].kwargs['pk']):
            raise serializers.ValidationError('Can\'t follow self.')
        return super().validate(attrs)