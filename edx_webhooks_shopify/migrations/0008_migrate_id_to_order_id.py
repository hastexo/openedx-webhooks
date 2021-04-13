# Generated by Django 2.2.20 on 2021-04-13 09:28

from django.db import migrations, models
import django.db.models.deletion


def populate(apps, schema_editor):
   model = apps.get_model('edx_webhooks_shopify', 'shopifyorder')
   for index, item in enumerate(model.objects.all(), start=1):
       item.id = index
       item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('edx_webhooks_shopify', '0007_shopifyorder_action'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shopifyorder',
            old_name='id',
            new_name='order_id',
        ),
        migrations.AddConstraint(
            model_name='shopifyorder',
            constraint=models.UniqueConstraint(fields=('order_id', 'action'), name='unique_order_id_action'),
        ),
        migrations.AlterField(
            model_name='shopifyorder',
            name='order_id',
            field=models.BigIntegerField(editable=False),
        ),
        migrations.AddField(
            model_name='shopifyorder',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.RunPython(populate),
        migrations.AlterField(
            model_name='shopifyorder',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        )
    ]