# alumnos/migrations/0005_fix_matricula.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('alumnos', '0004_alter_alumno_email_institucional_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='matricula',
            field=models.CharField(default='PENDIENTE', max_length=20),
        ),
        migrations.AlterModelOptions(
            name='alumno',
            options={'ordering': ['matricula', 'apellido_paterno', 'apellido_materno', 'nombre'], 'verbose_name': 'Alumno', 'verbose_name_plural': 'Alumnos'},
        ),
    ]