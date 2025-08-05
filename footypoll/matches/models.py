from django.db import models
from django.utils import timezone

class Match(models.Model):
    MATCH_DAYS = [
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    date = models.DateField()
    time = models.TimeField(default="19:00")
    max_players = models.PositiveIntegerField(default=12)
    day = models.CharField(choices=MATCH_DAYS, max_length=10)
    location_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.day} - {self.date} at {self.time}"

    @property
    def active_players(self):
        # Use related_name='players' from PlayerEntry FK
        return self.players.filter(removed=False).order_by('added_at')

from django.contrib.auth.models import User

class PlayerEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='players')
    removed = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes (e.g., 'Coming late', 'I'll bring a ball')")

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.match}"


class ActionLog(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player_name = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=[("added", "Added"), ("removed", "Removed")])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class MatchComment(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} on {self.match} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
