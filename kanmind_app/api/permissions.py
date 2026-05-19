from rest_framework import permissions

from kanmind_app.models import Boards


class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj ist eine Task; navigieren Sie zum zugehörigen Board
        # oder board.creator, je nach Ihrem Feldnamen
        return obj.board.owner == request.user


class IsBoardMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':

            board_id = request.data.get('board')
            if not board_id:
                return False
            try:
                board = Boards.objects.get(id=board_id)
                return board.members.filter(id=request.user.id).exists()
            except Boards.DoesNotExist:
                return True  # if board does not exist, allow permission to let the view handle the 404 response
        return True  # For other actions, permission will be checked at the object level

    def has_object_permission(self, request, view, obj):

        try:
            board = Boards.objects.get(id=obj.board_id)
            return board.members.filter(id=request.user.id).exists()
        except (AttributeError, Boards.DoesNotExist):
            return False
