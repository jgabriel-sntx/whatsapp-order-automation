from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0002_protect_e_validacoes'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='token_bot',
            field=models.CharField(blank=True, editable=False, max_length=64, null=True, unique=True),
        ),
    ]
