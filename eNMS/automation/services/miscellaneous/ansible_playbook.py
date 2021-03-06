from logging import info
from json import dumps, loads
from json.decoder import JSONDecodeError
from sqlalchemy import Boolean, Column, ForeignKey, Integer, PickleType, String
from sqlalchemy.ext.mutable import MutableDict
from subprocess import check_output

from eNMS.automation.helpers import substitute
from eNMS.automation.models import Service
from eNMS.base.classes import service_classes


class AnsiblePlaybookService(Service):

    __tablename__ = 'AnsiblePlaybookService'

    id = Column(Integer, ForeignKey('Service.id'), primary_key=True)
    has_targets = True
    playbook_path = Column(String)
    arguments = Column(String)
    content_match = Column(String)
    content_match_textarea = True
    content_match_regex = Column(Boolean)
    negative_logic = Column(Boolean)
    delete_spaces_before_matching = Column(Boolean)
    options = Column(MutableDict.as_mutable(PickleType), default={})
    pass_device_properties = Column(Boolean)
    inventory_from_selection = Column(Boolean)

    __mapper_args__ = {
        'polymorphic_identity': 'AnsiblePlaybookService',
    }

    def job(self, device, _):
        arguments = substitute(self.arguments, locals()).split()
        command = ['ansible-playbook']
        if self.pass_device_properties:
            properties = device.get_properties()
            properties['password'] = device.password
            command.extend(['-e', dumps(properties)])
        if self.inventory_from_selection:
            command.extend(['-i', device.ip_address + ','])
        command.append(substitute(self.playbook_path, locals()))
        info(f"Sending Ansible playbook: {' '.join(command + arguments)}")
        result = check_output(command + arguments)
        info(result)
        try:
            result = result.decode('utf-8')
        except AttributeError:
            pass
        try:
            result = loads(result)
        except JSONDecodeError:
            pass
        match = substitute(self.content_match, locals())
        return {
            'expected': match,
            'negative_logic': self.negative_logic,
            'result': result,
            'success': self.match_content(str(result), match)
        }


service_classes['AnsiblePlaybookService'] = AnsiblePlaybookService
