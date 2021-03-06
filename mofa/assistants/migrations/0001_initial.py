# Generated by Django 2.2.6 on 2019-12-11 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='SendMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('http://id.tincanapi.com/verb/viewed', 'Viewed'), ('http://adlnet.gov/expapi/verbs/answered', 'Quiz Question Answered'), ('http://activitystrea.ms/schema/1.0/create', 'New Activity Created'), ('http://adlnet.gov/expapi/verbs/completed', 'Quiz Completed')], max_length=50)),
                ('destination', models.CharField(default='moodle', max_length=50)),
                ('forwarder_id', models.CharField(default=0, max_length=25)),
                ('message', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
            ],
            options={
                'verbose_name': 'send message assistant',
            },
        ),
        migrations.CreateModel(
            name='QuizQuestionFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('http://id.tincanapi.com/verb/viewed', 'Viewed'), ('http://adlnet.gov/expapi/verbs/answered', 'Quiz Question Answered'), ('http://activitystrea.ms/schema/1.0/create', 'New Activity Created'), ('http://adlnet.gov/expapi/verbs/completed', 'Quiz Completed')], max_length=50)),
                ('destination', models.CharField(default='moodle', max_length=50)),
                ('forwarder_id', models.CharField(default=0, max_length=25)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
            ],
            options={
                'verbose_name': 'quiz question feedback assistant',
            },
        ),
        migrations.CreateModel(
            name='QuizCompletedFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('http://id.tincanapi.com/verb/viewed', 'Viewed'), ('http://adlnet.gov/expapi/verbs/answered', 'Quiz Question Answered'), ('http://activitystrea.ms/schema/1.0/create', 'New Activity Created'), ('http://adlnet.gov/expapi/verbs/completed', 'Quiz Completed')], max_length=50)),
                ('destination', models.CharField(default='moodle', max_length=50)),
                ('forwarder_id', models.CharField(default=0, max_length=25)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Quiz')),
            ],
            options={
                'verbose_name': 'quiz completed feedback assistant',
            },
        ),
        migrations.CreateModel(
            name='NewActivityCreated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('http://id.tincanapi.com/verb/viewed', 'Viewed'), ('http://adlnet.gov/expapi/verbs/answered', 'Quiz Question Answered'), ('http://activitystrea.ms/schema/1.0/create', 'New Activity Created'), ('http://adlnet.gov/expapi/verbs/completed', 'Quiz Completed')], max_length=50)),
                ('destination', models.CharField(default='moodle', max_length=50)),
                ('forwarder_id', models.CharField(default=0, max_length=25)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
            ],
            options={
                'verbose_name': 'new activity assistant',
            },
        ),
    ]
