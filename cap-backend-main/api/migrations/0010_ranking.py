# Generated by Django 3.1.6 on 2021-02-18 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('course_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.course_group')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.student')),
            ],
            options={
                'unique_together': {('course_group', 'student')},
                'index_together': {('course_group', 'student')},
            },
        ),
    ]
