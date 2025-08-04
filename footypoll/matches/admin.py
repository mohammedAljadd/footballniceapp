from django.contrib import admin
from .models import Match, PlayerEntry, ActionLog
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('day', 'date', 'time', 'max_players')

@admin.register(PlayerEntry)
class PlayerEntryAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'match', 'added_at', 'removed')

    def player_name(self, obj):
        return obj.user.username
    player_name.admin_order_field = 'user'
    player_name.short_description = 'Player Name'

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'match', 'action', 'timestamp')

    def player_name(self, obj):
        return obj.user.username
    player_name.admin_order_field = 'user'
    player_name.short_description = 'Player Name'

@staff_member_required  # Only admins/staff can see this page
def action_log(request):
    logs = ActionLog.objects.select_related('match').order_by('-timestamp')  # latest first
    return render(request, 'matches/action_log.html', {'logs': logs})
