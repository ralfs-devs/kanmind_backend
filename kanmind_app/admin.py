from django.contrib import admin
from .models import Boards, Tasks, Comments

admin.site.register([Boards, Tasks, Comments])
