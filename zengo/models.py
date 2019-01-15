# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from konst import Constant, Constants
from konst.models.fields import ConstantChoiceCharField


class ZendeskUser(models.Model):
    """
    Link between a user in Zendesk and the local system.

    Depending on how users access Zendesk services, it may sometime
    not be possible to link all Zendesk users to local users, so `user`
    can be null.
    """

    class Meta:
        app_label = "zengo"

    id = models.BigAutoField(primary_key=True)
    zendesk_id = models.BigIntegerField(unique=True)
    name = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    user = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.PROTECT
    )
    created_at = models.DateTimeField()


class Ticket(models.Model):
    class Meta:
        app_label = "zengo"

    id = models.BigAutoField(primary_key=True)
    zendesk_id = models.BigIntegerField(unique=True)
    requester = models.ForeignKey(ZendeskUser, on_delete=models.CASCADE)
    subject = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    states = Constants(
        Constant(new="new"),
        Constant(open="open"),
        Constant(pending="pending"),
        Constant(hold="hold"),
        Constant(solved="solved"),
        Constant(closed="closed"),
    )
    status = ConstantChoiceCharField(constants=states, max_length=8)
    # custom fields and tags are stored here, relatively unprocessed
    custom_fields = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=True)


class Comment(models.Model):
    class Meta:
        app_label = "zengo"

    id = models.BigAutoField(primary_key=True)
    zendesk_id = models.BigIntegerField(unique=True)
    ticket = models.ForeignKey(
        Ticket, related_name="comments", on_delete=models.CASCADE
    )
    author = models.ForeignKey(ZendeskUser, on_delete=models.CASCADE)
    body = models.TextField(null=True, blank=True)
    public = models.BooleanField()
    created_at = models.DateTimeField()


class Event(models.Model):
    class Meta:
        app_label = "zengo"

    # limit the length to limit abuse
    raw_data = models.TextField(max_length=1024)

    # the remote ticket ID extracted from the data
    remote_ticket_id = models.PositiveIntegerField(null=True, blank=True)

    # if processing failed, an error will appear here
    error = models.TextField(null=True, blank=True)

    # if processing succeeded, this will point at a local Ticket instance
    # with comments etc
    ticket = models.ForeignKey(
        Ticket, null=True, blank=True, related_name="events", on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def json(self):
        return json.loads(self.raw_data)
