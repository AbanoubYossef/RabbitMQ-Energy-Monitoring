# Generated migration for UserDeviceMapping model

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('role', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('max_consumption', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'devices',
            },
        ),
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
        migrations.CreateModel(
            name='DeviceMeasurement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_id', models.UUIDField(db_index=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('measurement_value', models.FloatField(help_text='Energy consumed in 10-minute interval (kWh)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'device_measurements',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='HourlyEnergyConsumption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_id', models.UUIDField(db_index=True)),
                ('date', models.DateField(db_index=True)),
                ('hour', models.IntegerField(help_text='Hour of day (0-23)')),
                ('total_consumption', models.FloatField(help_text='Total energy consumed in hour (kWh)')),
                ('measurement_count', models.IntegerField(default=0, help_text='Number of measurements aggregated')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'hourly_energy_consumption',
                'ordering': ['-date', '-hour'],
                'unique_together': {('device_id', 'date', 'hour')},
            },
        ),
        migrations.AddIndex(
            model_name='devicemeasurement',
            index=models.Index(fields=['device_id', 'timestamp'], name='device_meas_device__idx'),
        ),
        migrations.AddIndex(
            model_name='hourlyenergyconsumption',
            index=models.Index(fields=['device_id', 'date', 'hour'], name='hourly_ener_device__idx'),
        ),
    ]
