from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='followers')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(following=models.F('user')),
                name='self_following_disallowed'
            ),
            models.UniqueConstraint(
                fields=['following', 'user'], name='unique_following'),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.following}'
