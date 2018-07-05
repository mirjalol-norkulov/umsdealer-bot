#  -*- coding: utf-8 -*-

from peewee import *

database = MySQLDatabase('umsdeale_database', host='umsdealer.uz', port=3306,
                         **{'charset': 'utf8', 'use_unicode': True, 'user': 'umsdeale_dbadmin',
                            'password': 'mirjalol24011996'
                            })


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Advertisements(BaseModel):
    created_at = DateTimeField(null=True)
    image_ru = CharField()
    image_uz = CharField()
    section = IntegerField()
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'advertisements'


class Services(BaseModel):
    created_at = DateTimeField(null=True)
    description_ru = TextField()
    description_uz = TextField()
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)
    ussd = CharField()

    class Meta:
        table_name = 'services'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz

    def description(self, language):
        return self.description_ru if language == 'ru' else self.description_uz


class Buttons(BaseModel):
    created_at = DateTimeField(null=True)
    service = ForeignKeyField(column_name='service_id', field='id', model=Services, backref='buttons')
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)
    ussd = CharField()

    class Meta:
        table_name = 'buttons'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz


class CollectionModes(BaseModel):
    button_title_ru = CharField(null=True)
    button_title_uz = CharField(null=True)
    created_at = DateTimeField(null=True)
    title_ru = CharField()
    title_uz = CharField()
    type = CharField()
    updated_at = DateTimeField(null=True)
    ussd = CharField()

    class Meta:
        table_name = 'collection_modes'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz

    def button_title(self, language):
        return self.button_title_ru if language == 'ru' else self.button_title_uz

    @staticmethod
    def get_by_title(title, language):
        try:
            if language == 'ru':
                return CollectionModes.get(CollectionModes.title_ru == title)
            else:
                return CollectionModes.get(CollectionModes.title_uz == title)
        except DoesNotExist:
            return None


class CollectionTypes(BaseModel):
    collection_mode = ForeignKeyField(column_name='collection_mode_id',
                                      field='id',
                                      model=CollectionModes,
                                      backref='collection_types')
    created_at = DateTimeField(null=True)
    description_ru = TextField()
    description_uz = TextField()
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'collection_types'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz

    def description(self, language):
        return self.description_ru if language == 'ru' else self.description_uz

    @staticmethod
    def get_by_title(title, language):
        try:
            if language == 'ru':
                return CollectionTypes.get(CollectionTypes.title_ru == title)
            else:
                return CollectionTypes.get(CollectionTypes.title_uz == title)
        except DoesNotExist:
            return None


class Collections(BaseModel):
    coast_ru = CharField()
    coast_uz = CharField()
    collection_type = ForeignKeyField(column_name='collection_type_id',
                                      field='id',
                                      model=CollectionTypes,
                                      backref='collections')
    created_at = DateTimeField(null=True)
    description_ru = TextField()
    description_uz = TextField()
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)
    ussd = CharField()

    class Meta:
        table_name = 'collections'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz

    def description(self, language):
        return self.description_ru if language == 'ru' else self.description_uz

    def coast(self, language):
        return self.coast_ru if language == 'ru' else self.coast_uz


class DeletedModels(BaseModel):
    created_at = DateTimeField(null=True)
    type = CharField()
    updated_at = DateTimeField(null=True)
    uuid = IntegerField()

    class Meta:
        table_name = 'deleted_models'


class DialogItemTypes(BaseModel):
    created_at = DateTimeField(null=True)
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'dialog_item_types'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz


class DialogItems(BaseModel):
    created_at = DateTimeField(null=True)
    dialog_item_type = ForeignKeyField(column_name='dialog_item_type_id', field='id', model=DialogItemTypes,
                                       backref='dialog_items')
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)
    ussd = CharField()

    class Meta:
        table_name = 'dialog_items'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz


class Infos(BaseModel):
    balance_ussd = CharField()
    call_center = CharField()
    created_at = DateTimeField(null=True)
    helper_title_ru = CharField()
    helper_title_uz = CharField()
    helper_url_ru = CharField()
    helper_url_uz = CharField()
    meta_title_ru = CharField()
    meta_title_uz = CharField()
    meta_url_ru = CharField()
    meta_url_uz = CharField()
    updated_at = DateTimeField(null=True)

    def meta_url(self, language):
        return self.meta_url_ru if language == 'ru' else self.meta_url_uz

    def meta_title(self, language):
        return self.meta_title_ru if language == 'ru' else self.meta_title_uz

    def helper_url(self, language):
        return self.helper_url_ru if language == 'ru' else self.helper_url_uz

    def helper_title(self, language):
        return self.helper_title_ru if language == 'ru' else self.helper_title_uz

    class Meta:
        table_name = 'infos'


class Migrations(BaseModel):
    batch = IntegerField()
    migration = CharField()

    class Meta:
        table_name = 'migrations'


class Permissions(BaseModel):
    created_at = DateTimeField(null=True)
    guard_name = CharField()
    name = CharField()
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'permissions'


class ModelHasPermissions(BaseModel):
    model = IntegerField(column_name='model_id')
    model_type = CharField()
    permission = ForeignKeyField(column_name='permission_id', field='id', model=Permissions)

    class Meta:
        table_name = 'model_has_permissions'
        indexes = (
            (('model', 'model_type'), False),
            (('permission', 'model', 'model_type'), True),
        )
        primary_key = CompositeKey('model', 'model_type', 'permission')


class Roles(BaseModel):
    created_at = DateTimeField(null=True)
    guard_name = CharField()
    name = CharField()
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'roles'


class ModelHasRoles(BaseModel):
    model = IntegerField(column_name='model_id')
    model_type = CharField()
    role = ForeignKeyField(column_name='role_id', field='id', model=Roles)

    class Meta:
        table_name = 'model_has_roles'
        indexes = (
            (('model', 'model_type'), False),
            (('role', 'model', 'model_type'), True),
        )
        primary_key = CompositeKey('model', 'model_type', 'role')


class News(BaseModel):
    created_at = DateTimeField(null=True)
    description_ru = TextField()
    description_uz = TextField()
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)
    url_ru = CharField()
    url_uz = CharField()

    class Meta:
        table_name = 'news'

    def title(self, language):
        return self.title_ru if language == 'ru' else self.title_uz

    def description(self, language):
        return self.description_ru if language == 'ru' else self.description_uz

    def url(self, language):
        return self.url_ru if language == 'ru' else self.url_uz


class PasswordResets(BaseModel):
    created_at = DateTimeField(null=True)
    email = CharField(index=True)
    token = CharField()

    class Meta:
        table_name = 'password_resets'
        primary_key = False


class Rates(BaseModel):
    content_ru = TextField()
    content_uz = TextField()
    created_at = DateTimeField(null=True)
    description_ru = TextField()
    description_uz = TextField()
    icon_url = CharField()
    super_zero_ussd = CharField(null=True)
    title_ru = CharField()
    title_uz = CharField()
    updated_at = DateTimeField(null=True)
    ussd = CharField()

    class Meta:
        table_name = 'rates'

    def title(self, language):
        if language == 'ru':
            return self.title_ru
        else:
            return self.title_uz

    def description(self, language):
        if language == 'ru':
            return self.description_ru
        else:
            return self.description_uz


class RoleHasPermissions(BaseModel):
    permission = ForeignKeyField(column_name='permission_id', field='id', model=Permissions)
    role = ForeignKeyField(column_name='role_id', field='id', model=Roles)

    class Meta:
        table_name = 'role_has_permissions'
        indexes = (
            (('permission', 'role'), True),
        )
        primary_key = CompositeKey('permission', 'role')


class TelegramChannels(BaseModel):
    created_at = DateTimeField(null=True)
    title = CharField()
    updated_at = DateTimeField(null=True)
    url = CharField()

    class Meta:
        table_name = 'telegram_channels'


class Users(BaseModel):
    created_at = DateTimeField(null=True)
    email = CharField(unique=True)
    name = CharField()
    password = CharField()
    remember_token = CharField(null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'users'


class TelegramUsers(BaseModel):
    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True)
    telegram_id = IntegerField(unique=True)
    language_code = CharField()
