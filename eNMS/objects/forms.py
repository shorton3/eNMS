from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField
)

from eNMS.base.models import MultipleObjectField, ObjectField
from eNMS.base.properties import (
    custom_properties,
    link_public_properties,
    link_subtypes,
    device_public_properties,
    device_subtypes
)


def configure_device_form(cls):
    for property in custom_properties:
        setattr(cls, property, StringField())
    return cls


def configure_pool_form(cls):
    cls.device_properties = device_public_properties
    cls.link_properties = link_public_properties
    boolean_fields = []
    for cls_name, properties in (
        ('device', device_public_properties),
        ('link', link_public_properties)
    ):
        for property in properties:
            boolean_field = f'{cls_name}_{property}_regex'
            setattr(cls, f'{cls_name}_{property}', StringField(property))
            setattr(cls, boolean_field, BooleanField('Regex'))
            boolean_fields.append(boolean_field)
    setattr(
        cls,
        'boolean_fields',
        HiddenField(default=','.join(boolean_fields))
    )
    return cls


class AddObjectForm(FlaskForm):
    id = HiddenField()
    name = StringField()
    description = StringField()
    location = StringField()
    vendor = StringField()
    model = StringField()


@configure_device_form
class AddDevice(AddObjectForm):
    device_types = [subtype for subtype in device_subtypes.items()]
    subtype = SelectField(choices=device_types)
    ip_address = StringField('IP address')
    port = IntegerField(default=22)
    operating_system = StringField()
    os_version = StringField()
    longitude = FloatField(default=0.)
    latitude = FloatField(default=0.)
    username = StringField()
    password = PasswordField()
    enable_password = PasswordField()


class AddLink(AddObjectForm):
    link_types = [subtype for subtype in link_subtypes.items()]
    subtype = SelectField(choices=link_types)
    source = ObjectField('Device')
    destination = ObjectField('Device')


@configure_pool_form
class AddPoolForm(FlaskForm):
    name = StringField()
    description = StringField()


class PoolObjectsForm(FlaskForm):
    list_fields = HiddenField(default='devices,links')
    devices = MultipleObjectField('Device')
    links = MultipleObjectField('Link')


class ImportExportForm(FlaskForm):
    boolean_fields = HiddenField(default='update_pools,replace')
    name = StringField()
    update_pools = BooleanField()
    replace = BooleanField()


class OpenNmsForm(FlaskForm):
    opennms_rest_api = StringField()
    opennms_devices = StringField()
    node_type = [subtype for subtype in device_subtypes.items()]
    subtype = SelectField(choices=node_type)
    opennms_login = StringField()
    password = PasswordField()


class NetboxForm(FlaskForm):
    netbox_address = StringField(default='http://0.0.0.0:8000')
    netbox_token = PasswordField()
    node_type = [subtype for subtype in device_subtypes.items()]
    netbox_type = SelectField(choices=node_type)


class LibreNmsForm(FlaskForm):
    librenms_address = StringField(
        default='http://librenms.example.com'
    )
    node_type = [subtype for subtype in device_subtypes.items()]
    librenms_type = SelectField(choices=node_type)
    librenms_token = PasswordField()


class DeviceAutomationForm(FlaskForm):
    list_fields = HiddenField(default='jobs')
    jobs = MultipleObjectField('Job')
