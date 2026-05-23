from rest_framework import permissions
from kanmind_app.models import Boards


class IsBoardOwner(permissions.BasePermission):
    """Permission class to verify if the requesting user owns the board.

    This permission works for both the `Boards` instance itself and any child
    objects that possess a relation link named `board` (e.g., Tasks).
    """

    def has_object_permission(self, request, view, obj):
        """Check if the user is the owner of the resolved board object.

        Args:
            request (Request): The incoming DRF request object.
            view (APIView): The view instance handling the request.
            obj (models.Model): The object whose permission is being checked.

        Returns:
            bool: True if the user owns the board, False otherwise.
        """
        if isinstance(obj, Boards):
            board = obj
        elif hasattr(obj, 'board'):
            board = obj.board
        else:
            return False

        return board.owner == request.user


class IsBoardMember(permissions.BasePermission):
    """Permission class to verify if the requesting user is a member of the board.

    Handles general list/create actions by checking the incoming request data,
    as well as individual object access level permissions.
    """

    def has_permission(self, request, view):
        """Check general permission for incoming actions like 'create'.

        For creation steps, it inspects the request payload for a board ID
        and validates membership.

        Args:
            request (Request): The incoming DRF request object.
            view (APIView): The view instance handling the request.

        Returns:
            bool: True if user is a member or if the action does not require 
                payload validation. Returns True on non-existent boards to let 
                the view handle the standard 404 response.
        """
        if view.action == 'create':
            board_id = request.data.get('board')
            if not board_id:
                return False
            try:
                board = Boards.objects.get(id=board_id)
                return board.members.filter(id=request.user.id).exists()
            except Boards.DoesNotExist:
                return True
        return True

    def has_object_permission(self, request, view, obj):
        """Check if the user is a verified member of the resolved board.

        Args:
            request (Request): The incoming DRF request object.
            view (APIView): The view instance handling the request.
            obj (models.Model): The object whose permission is being checked.

        Returns:
            bool: True if the user is a registered member of the board, False otherwise.
        """
        if isinstance(obj, Boards):
            board = obj
        elif hasattr(obj, 'board'):
            board = obj.board
        else:
            return False

        return board.members.filter(id=request.user.id).exists()
