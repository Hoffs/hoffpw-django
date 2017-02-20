# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitch_stats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitchprofile',
            name='access_token',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchprofile',
            name='authorization_code',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchprofile',
            name='scopes',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchprofile',
            name='twitch_display',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchprofile',
            name='twitch_id',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchprofile',
            name='twitch_name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchprofile',
            name='twitch_user_type',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchstats',
            name='channel_id',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchstats',
            name='channel_language',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchstats',
            name='channel_status',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchstats',
            name='game',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchstats',
            name='stream_id',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='twitchtrackingprofile',
            name='twitch_id',
            field=models.TextField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='twitchtrackingprofile',
            name='twitch_name',
            field=models.TextField(max_length=254),
        ),
    ]