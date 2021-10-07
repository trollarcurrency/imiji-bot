from tortoise.models import Model
from tortoise import fields

class Account(Model):
    user = fields.OneToOneField('db.User', related_name='account', index=True)
    address = fields.CharField(max_length=66, unique=True, index=True)

    class Meta:
        table = 'accounts'
