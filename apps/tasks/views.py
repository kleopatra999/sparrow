# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from .serializers import TaskSerializer
from .models import Task


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
