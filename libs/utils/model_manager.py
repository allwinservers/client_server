# coding:utf-8

from django.db import models


class BaseManager(models.Manager):
    def get_queryset(self):
        # table_name = self.model._meta.db_table
        return super(BaseManager, self).get_queryset().filter(is_deleted=False)
