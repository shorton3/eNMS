from xlrd import open_workbook
from xlrd.biffh import XLRDError

from eNMS import db
from eNMS.base.classes import classes
from eNMS.base.helpers import factory, integrity_rollback, fetch


def create_default_users():
    factory('User', **{
        'name': 'admin',
        'email': 'admin@admin.com',
        'password': 'admin',
        'permissions': ['Admin']
    })


def create_default_pools():
    for pool in (
        {
            'name': 'All objects',
            'description': 'All objects'
        },
        {
            'name': 'Devices only',
            'description': 'Devices only',
            'link_name': '^$',
            'link_name_regex': 'y'
        },
        {
            'name': 'Links only',
            'description': 'Links only',
            'device_name': '^$',
            'device_name_regex': 'y'
        }
    ):
        factory('Pool', **pool)


@integrity_rollback
def create_default_parameters():
    parameters = classes['Parameters']()
    db.session.add(parameters)
    db.session.commit()


@integrity_rollback
def create_default_network_topology(app):
    with open(app.path / 'projects' / 'usa.xls', 'rb') as f:
        book = open_workbook(file_contents=f.read())
        for object_type in ('Device', 'Link'):
            try:
                sheet = book.sheet_by_name(object_type)
            except XLRDError:
                continue
            properties = sheet.row_values(0)
            for row_index in range(1, sheet.nrows):
                values = dict(zip(properties, sheet.row_values(row_index)))
                factory(object_type, **values)
            db.session.commit()


@integrity_rollback
def create_default_services():
    admin = fetch('User', name='admin').id
    for service in (
        {
            'type': 'SwissArmyKnifeService',
            'name': 'Start',
            'description': 'Start point of a workflow',
            'creator': admin,
            'hidden': True
        },
        {
            'type': 'SwissArmyKnifeService',
            'name': 'End',
            'description': 'End point of a workflow',
            'creator': admin,
            'hidden': True
        },
        {
            'type': 'SwissArmyKnifeService',
            'name': 'mail_feedback_notification',
            'description': 'Mail notification (service logs)',
            'creator': admin
        },
        {
            'type': 'SwissArmyKnifeService',
            'name': 'slack_feedback_notification',
            'description': 'Slack notification (service logs)',
            'creator': admin
        },
        {
            'type': 'SwissArmyKnifeService',
            'name': 'mattermost_feedback_notification',
            'description': 'Mattermost notification (service logs)',
            'creator': admin
        }
    ):
        factory(service.pop('type'), **service)


@integrity_rollback
def create_example_services():
    admin = fetch('User', name='admin').id
    for service in (
        {
            'type': 'ConfigureBgpService',
            'name': 'napalm_configure_bgp_1',
            'description': 'Configure BGP Peering with Napalm',
            'devices': [fetch('Device', name='Washington').id],
            'creator': admin,
            'local_as': 100,
            'loopback': 'Lo100',
            'loopback_ip': '100.1.1.1',
            'neighbor_ip': '100.1.2.1',
            'remote_as': 200,
            'vrf_name': 'configure_BGP_test',
            'waiting_time': 0
        },
        {
            'type': 'GenericFileTransferService',
            'name': 'test_file_transfer_service',
            'description': 'Test the file transfer service',
            'devices': [fetch('Device', name='Aserver').id],
            'creator': admin,
            'direction': 'get',
            'protocol': 'scp',
            'source_file': '/media/sf_VM/eNMS/tests/file_transfer/a.bin',
            'destination_file': '/media/sf_VM/eNMS/tests/file_transfer/b.bin',
            'missing_host_key_policy': True
        },
        {
            'type': 'LogBackupService',
            'name': 'test_log_backup_service',
            'description': 'Test the log backup service',
            'devices': [fetch('Device', name='Aserver').id],
            'creator': admin,
            'protocol': 'scp',
            'destination_ip_address': '127.0.0.1',
            'destination_path': '/media/sf_VM/eNMS/tests/file_transfer',
            'delete_archive': True,
            'delete_folder': True
        },
        {
            'type': 'DatabaseBackupService',
            'name': 'test_database_backup_service',
            'description': 'Test the log backup service',
            'devices': [fetch('Device', name='Aserver').id],
            'creator': admin,
            'protocol': 'scp',
            'destination_ip_address': '127.0.0.1',
            'destination_path': '/media/sf_VM/eNMS/tests/file_transfer',
            'delete_archive': True,
            'delete_folder': True
        }
    ):
        factory(service.pop('type'), **service)


@integrity_rollback
def create_netmiko_workflow():
    services, admin = [], fetch('User', name='admin').id
    devices = [
        fetch('Device', name='Washington').id,
        fetch('Device', name='Austin').id
    ]
    for service in (
        {
            'type': 'NetmikoConfigurationService',
            'name': 'netmiko_create_vrf_test',
            'description': 'Create a VRF "test" with Netmiko',
            'waiting_time': 0,
            'devices': devices,
            'creator': admin,
            'vendor': 'Arista',
            'operating_system': 'eos',
            'driver': 'arista_eos',
            'global_delay_factor': '1.0',
            'content': 'vrf definition test',
            'enable_mode': 'y',
            'fast_cli': 'y',
            'timeout': 3
        },
        {
            'type': 'NetmikoValidationService',
            'name': 'netmiko_check_vrf_test',
            'description': 'Check that the vrf "test" is configured',
            'waiting_time': 0,
            'devices': devices,
            'creator': admin,
            'vendor': 'Arista',
            'operating_system': 'eos',
            'driver': 'arista_eos',
            'command': 'show vrf',
            'content_match': 'test',
            'fast_cli': 'y',
            'timeout': 3
        },
        {
            'type': 'NetmikoConfigurationService',
            'name': 'netmiko_delete_vrf_test',
            'description': 'Delete VRF "test"',
            'waiting_time': 1,
            'devices': devices,
            'creator': admin,
            'vendor': 'Arista',
            'operating_system': 'eos',
            'driver': 'arista_eos',
            'global_delay_factor': '1.0',
            'content': 'no vrf definition test',
            'enable_mode': 'y',
            'fast_cli': 'y',
            'timeout': 3
        },
        {
            'type': 'NetmikoValidationService',
            'name': 'netmiko_check_no_vrf_test',
            'description': 'Check that the vrf "test" is NOT configured',
            'waiting_time': 0,
            'devices': devices,
            'creator': admin,
            'vendor': 'Arista',
            'operating_system': 'eos',
            'driver': 'arista_eos',
            'command': 'show vrf',
            'content_match': '^((?!test)[\s\S])*$',
            'content_match_regex': 'y',
            'fast_cli': 'y',
            'timeout': 3,
            'number_of_retries': 2,
            'time_between_retries': 1
        },
    ):
        instance = factory(service.pop('type'), **service)
        services.append(instance)
    workflow = factory('Workflow', **{
        'name': 'Netmiko_VRF_workflow',
        'description': 'Create and delete a VRF with Netmiko',
        'creator': admin,
        'vendor': 'Arista',
        'operating_system': 'eos'
    })
    workflow.jobs.extend(services)
    edges = [(0, 2), (2, 3), (3, 4), (4, 5), (5, 1)]
    for x, y in edges:
        factory('WorkflowEdge', **{
            'name': f'{workflow.name} {x} -> {y}',
            'workflow': workflow.id,
            'subtype': True,
            'source': workflow.jobs[x].id,
            'destination': workflow.jobs[y].id
        })
    positions = [(-20, 0), (20, 0), (0, -15), (0, -5), (0, 5), (0, 15)]
    for index, (x, y) in enumerate(positions):
        workflow.jobs[index].positions['Netmiko_VRF_workflow'] = x * 10, y * 10


@integrity_rollback
def create_napalm_workflow():
    services, admin = [], fetch('User', name='admin').id
    devices = [
        fetch('Device', name='Washington').id,
        fetch('Device', name='Austin').id
    ]
    for service in (
        {
            'type': 'NapalmConfigurationService',
            'name': 'napalm_create_vrf_test',
            'description': 'Create a VRF "test" with Napalm',
            'waiting_time': 0,
            'devices': devices,
            'creator': admin,
            'driver': 'eos',
            'vendor': 'Arista',
            'operating_system': 'eos',
            'content_type': 'simple',
            'action': 'load_merge_candidate',
            'content': 'vrf definition test\n'
        },
        {
            'type': 'NapalmRollbackService',
            'name': 'Napalm eos Rollback',
            'driver': 'eos',
            'description': 'Rollback a configuration with Napalm eos',
            'devices': devices,
            'creator': admin,
            'waiting_time': 0
        }
    ):
        instance = factory(service.pop('type'), **service)
        services.append(instance)
    services.insert(1, fetch('Job', name='netmiko_check_vrf_test'))
    services.append(fetch('Job', name=f'netmiko_check_no_vrf_test'))
    workflow = factory('Workflow', **{
        'name': 'Napalm_VRF_workflow',
        'description': 'Create and delete a VRF with Napalm',
        'creator': admin,
        'vendor': 'Arista',
        'operating_system': 'eos'
    })
    workflow.jobs.extend(services)
    edges = [(0, 2), (2, 3), (3, 4), (4, 5), (5, 1)]
    for x, y in edges:
        factory('WorkflowEdge', **{
            'name': f'{workflow.name} {x} -> {y}',
            'workflow': workflow.id,
            'subtype': True,
            'source': workflow.jobs[x].id,
            'destination': workflow.jobs[y].id
        })
    positions = [(-20, 0), (20, 0), (0, -15), (0, -5), (0, 5), (0, 15)]
    for index, (x, y) in enumerate(positions):
        workflow.jobs[index].positions['Napalm_VRF_workflow'] = x * 10, y * 10


def create_payload_transfer_workflow():
    services, admin = [], fetch('User', name='admin').id
    devices = [
        fetch('Device', name='Washington').id,
        fetch('Device', name='Austin').id
    ]
    for service in [{
        'name': 'GET_device',
        'type': 'RestCallService',
        'description': 'Use GET ReST call on eNMS ReST API',
        'username': 'admin',
        'password': 'admin',
        'waiting_time': 0,
        'devices': devices,
        'creator': admin,
        'content_match': '',
        'call_type': 'GET',
        'url': 'http://127.0.0.1:5000/rest/object/device/{{device.name}}',
        'payload': '',
        'multiprocessing': 'y'
    }] + [{
        'name': f'{getter}',
        'type': 'NapalmGettersService',
        'description': f'Getter: {getter}',
        'waiting_time': 0,
        'devices': devices,
        'creator': admin,
        'driver': 'eos',
        'content_match': '',
        'getters': [getter]
    } for getter in (
        'get_facts',
        'get_interfaces',
        'get_interfaces_ip',
        'get_config'
    )] + [{
        'name': 'process_payload1',
        'type': 'SwissArmyKnifeService',
        'description': 'Process Payload in example workflow',
        'waiting_time': 0,
        'devices': devices,
        'creator': admin
    }]:
        instance = factory(service.pop('type'), **service)
        services.append(instance)
    workflow = factory('Workflow', **{
        'name': 'payload_transfer_workflow',
        'description': 'ReST call, Napalm getters, etc',
        'creator': admin,
        'vendor': 'Arista',
        'operating_system': 'eos'
    })
    workflow.jobs.extend(services)

    # create workflow edges with following schema:
    positions = [
        (-20, 0),
        (50, 0),
        (-5, 0),
        (-5, -10),
        (15, 10),
        (15, -10),
        (30, -10),
        (30, 0)
    ]
    for index, (x, y) in enumerate(positions):
        job = workflow.jobs[index]
        job.positions['payload_transfer_workflow'] = x * 10, y * 10
    edges = [(0, 2), (2, 3), (2, 4), (3, 5), (5, 6), (6, 7), (4, 7), (7, 1)]
    for x, y in edges:
        factory('WorkflowEdge', **{
            'name': f'{workflow.name} {x} -> {y}',
            'workflow': workflow.id,
            'subtype': True,
            'source': workflow.jobs[x].id,
            'destination': workflow.jobs[y].id
        })


def create_default_examples(app):
    create_default_network_topology(app),
    create_example_services()
    create_netmiko_workflow()
    create_napalm_workflow()
    create_payload_transfer_workflow()
