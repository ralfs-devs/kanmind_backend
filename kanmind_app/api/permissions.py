from rest_framework import permissions

from kanmind_app.models import Boards


class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        board_id = request.data.get('board')
        if not board_id:
            return False
        try:
            board = Boards.objects.get(id=board_id)
            return board.members.filter(id=request.user.id).exists()
        except Boards.DoesNotExist:
            return True  # if board does not exist, allow permission to let the view handle the 404 response
