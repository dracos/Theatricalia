from django.db import migrations

from ..hashers import PBKDF2WrappedSHA1PasswordHasher


def forwards_func(apps, schema_editor):
    User = apps.get_model('profiles', 'User')
    users = User.objects.filter(password__startswith='sha1$')
    hasher = PBKDF2WrappedSHA1PasswordHasher()
    for user in users:
        print('Migrating', user.email)
        algorithm, salt, sha1_hash = user.password.split('$', 2)
        user.password = hasher.encode_sha1_hash(sha1_hash, salt)
        user.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20190310_1750'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
