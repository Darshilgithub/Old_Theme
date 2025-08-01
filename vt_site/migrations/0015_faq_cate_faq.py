# Generated by Django 4.2.6 on 2023-11-25 07:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vt_site', '0014_site_detail_contact_mail'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ_cate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1000)),
                ('answer', models.CharField(max_length=5000)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vt_site.faq_cate')),
            ],
        ),
    ]
