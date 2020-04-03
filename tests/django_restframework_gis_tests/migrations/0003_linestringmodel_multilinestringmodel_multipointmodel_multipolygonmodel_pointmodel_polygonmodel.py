# Generated by Django 3.0.4 on 2020-04-03 06:52

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_restframework_gis_tests', '0002_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineStringModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('random_field1', models.CharField(max_length=32)),
                ('random_field2', models.IntegerField()),
                ('points', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultiLineStringModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('random_field1', models.CharField(max_length=32)),
                ('random_field2', models.IntegerField()),
                ('points', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultiPointModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('random_field1', models.CharField(max_length=32)),
                ('random_field2', models.IntegerField()),
                ('points', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultiPolygonModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('random_field1', models.CharField(max_length=32)),
                ('random_field2', models.IntegerField()),
                ('polygon', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PointModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('random_field1', models.CharField(max_length=32)),
                ('random_field2', models.IntegerField()),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PolygonModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('random_field1', models.CharField(max_length=32)),
                ('random_field2', models.IntegerField()),
                ('polygon', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]