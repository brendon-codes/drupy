from django.db import models
from django.contrib.auth.models import User as DjangoUser
from drupy.plugins.filter.models import FilterFormat



class NodeType(models.Model):
    node_type = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    base = models.CharField(max_length=255)
    description = models.TextField()
    help = models.TextField()
    has_title = models.BooleanField()
    title_label = models.CharField(max_length=255)
    has_body = models.BooleanField()
    min_word_count = models.IntegerField()
    custom = models.BooleanField()
    modified = models.BooleanField()
    locked = models.BooleanField()



class NodeRevision(models.Model):
    user = models.ForeignKey(DjangoUser)
    title = models.CharField(max_length=255)
    body = models.TextField()
    teaser = models.TextField()
    log = models.TextField()
    time = models.DateTimeField()
    format = models.ForeignKey(FilterFormat)


class Node(models.Model):
    revision = models.ForeignKey(NodeRevision)
    node_type = models.ForeignKey(NodeType)
    #language = models.ForeignKey(DrupyLanguage)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(DjangoUser)
    status = models.BooleanField()
    created = models.DateTimeField()
    changed = models.DateTimeField()
    comment = models.BooleanField()
    promote = models.BooleanField()
    moderate = models.BooleanField()
    sticky = models.BooleanField()


class NodeAccess(models.Model):
    node = models.ForeignKey(Node)
    grant_view = models.BooleanField()
    grant_update = models.BooleanField()
    grant_delete = models.BooleanField()


class NodeCommentStatistics(models.Model):
    node = models.ForeignKey(Node)
    last_comment_timestamp = models.DateTimeField()
    last_comment_name = models.CharField(max_length=255)
    last_comment_user = models.ForeignKey(DjangoUser)
    comment_count = models.IntegerField()


class NodeCounter(models.Model):
    node = models.ForeignKey(Node)
    totalcount = models.IntegerField()
    daycount = models.IntegerField()
    time = models.DateTimeField()

