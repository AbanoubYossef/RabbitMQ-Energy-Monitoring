# Migration to add UserDeviceMapping model

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDeviceMapping',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_assignments', to='monitoring.device')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_assignments', to='monitoring.user')),
            ],
            options={
                'db_table': 'user_device_mapping',
                'unique_together': {('user', 'device')},
            },
        ),
    ]
