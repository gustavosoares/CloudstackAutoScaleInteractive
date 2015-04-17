#!/usr/bin/env python

__author__ = 'Cristiano Casado <co.casado@gmail.com>'
__version__ = '0.5'

from Config import Config
from prettytable import PrettyTable
import CloudStack
import sys
import argparse
import time

class Colors:
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def asyncResult(jobid):
	asyncargs = {
       'jobid': jobid
	}
 
 	async = cloudstack.queryAsyncJobResult(asyncargs)
	ready = async['jobstatus']
	while (ready == 0):
		print '\b.',
		sys.stdout.flush()
		time.sleep(5)
		async = cloudstack.queryAsyncJobResult(asyncargs)
		ready = async['jobstatus']
 	
 	result =  async['jobresult']
 	
 	return result

def listZoneId(name):
	zones = cloudstack.listZones({'name': name})
	for zone in zones:
		zoneid = zone['id']

	return zoneid

def listProjectId(name):
	projects = cloudstack.listProjects({'name': name})
	for project in projects:
		projectid = project['id']

	return projectid

def listNumVirtualMachines(projectid, name, state):
	vms = cloudstack.listVirtualMachines({'projectid': projectid, 'name': name, 'state': state})
	
	return len(vms)

def listCounters():
	counters = cloudstack.listCounters()
	table = PrettyTable(["ID", "Name", "Source"])
	table.align["Name"] = "l"
	table.align["Source"] = "l"
	for counter in counters:
		table.add_row([counter['id'], counter['name'], counter['source']])
	
	return table

def listConditions(projectid):
	conditions = cloudstack.listConditions({'projectid': projectid})
	table = PrettyTable(["ID", "Counter", "RelationalOperator", "Threshold(%)"])

	for condition in conditions:
		counters = (condition.get('counter'))
		for counter in counters:
			table.add_row([condition['id'], counter['name'], condition['relationaloperator'], condition['threshold']])
	
	return table

def listServiceOfferings():
	serviceofferings = cloudstack.listServiceOfferings()
	table = PrettyTable(["ID", "Name"])
	table.align["Name"] = "l"

	for serviceoffering in serviceofferings:
		table.add_row([serviceoffering['id'], serviceoffering['name']])
	
	return table

def listTemplates(templatefilter):
	templates = cloudstack.listTemplates({'templatefilter': templatefilter})
	table = PrettyTable(["ID", "Name"])
	table.align["Name"] = "l"

	for template in templates:
		table.add_row([template['id'], template['name']])
	
	return table

def listLoadBalancerRules(projectid):
	lbrules = cloudstack.listLoadBalancerRules({'projectid': projectid})
	table = PrettyTable(["ID", "Name"])
	table.align["Name"] = "l"

	for lbrule in lbrules:
		table.add_row([lbrule['id'], lbrule['name']])
	
	return table

def listAutoScalePolicies(projectid):
	autoscalepolicies = cloudstack.listAutoScalePolicies({'projectid': projectid})
	table = PrettyTable(["ID", "Action", "Duration", "QuietTime", "Counter", "RelationalOperator", "Threshold(%)"])

	for autoscalepolicy in autoscalepolicies['autoscalepolicy']:
		conditions = (autoscalepolicy.get('conditions'))
		for condition in conditions:
			counters = (condition.get('counter'))
			for counter in counters:
				table.add_row([autoscalepolicy['id'], autoscalepolicy['action'], autoscalepolicy['duration'], autoscalepolicy['quiettime'], counter['name'], condition['relationaloperator'], condition['threshold']])
	
	return table

def listAutoScaleVmProfiles(projectid):
	vmprofiles = cloudstack.listAutoScaleVmProfiles({'projectid': projectid})
	table = PrettyTable(["ID", "Template", "ServiceOffering"])
	table.align["Template"] = "l"
	table.align["ServiceOffering"] = "l"
	for vmprofile in vmprofiles:
		templateid = vmprofile['templateid']
		templates = cloudstack.listTemplates({'templatefilter': 'featured', 'id': templateid, 'zoneid': zoneid})
		serviceofferingid = vmprofile['serviceofferingid']
		serviceofferings = cloudstack.listServiceOfferings({'id': serviceofferingid})
		for template in templates:
			for serviceoffering in serviceofferings:
				table.add_row([vmprofile['id'], template['name'], serviceoffering['name']])
	
	return table

def listAutoScaleVmGroup(projectid):
	vmgroups = cloudstack.listAutoScaleVmGroups({'projectid': projectid})
	table = PrettyTable(["ID", "LoadBalancer", "Interval", "Max", "Min", "Running", "Action", "Counter", "Operator", "% Threshold"])
	numvmsrunning = listNumVirtualMachines(projectid, 'as-', 'Running')

	for vmgroup in vmgroups:
		lbruleid = vmgroup['lbruleid']
		lbrules = cloudstack.listLoadBalancerRules({'lbruleid': lbruleid})
		for lbrule in lbrules:
			lbname = lbrule['name']
		scaledownpolicies = (vmgroup.get('scaledownpolicies'))
		scaleuppolicies = (vmgroup.get('scaleuppolicies'))
		for scaledownpolicy in scaledownpolicies:
			conditionsd = (scaledownpolicy.get('conditions'))
			for conditiond in conditionsd:
				countersd = (conditiond.get('counter'))
				for counterd in countersd:
					table.add_row([vmgroup['id'], lbname, vmgroup['interval'], vmgroup['maxmembers'], vmgroup['minmembers'], numvmsrunning, scaledownpolicy['action'], counterd['name'], conditiond['relationaloperator'], conditiond['threshold']])
		for scaleuppolicy in scaleuppolicies:
			conditionsu = (scaleuppolicy.get('conditions'))
			for conditionu in conditionsu:
				countersu = (conditionu.get('counter'))
				for counteru in countersu:
					table.add_row([vmgroup['id'], lbname, vmgroup['interval'], vmgroup['maxmembers'], vmgroup['minmembers'], numvmsrunning, scaleuppolicy['action'], counteru['name'], conditionu['relationaloperator'], conditionu['threshold']])
	
	return table

def createCondition(counterid, operator, threshold, projectid):	
	job = cloudstack.createCondition({
		'counterid': counterid,
		'relationaloperator': operator,
		'threshold': str(threshold),
		'projectid': projectid
	})

	print "Creating condition. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['condition']['id']:
		return Colors.OKGREEN + "Condition created with id: %s" % jobresult['condition']['id'] + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def createPolicy(conditionids, action, duration):
	job = cloudstack.createAutoScalePolicy({
		'conditionids': conditionids,
		'action': action,
		'duration': str(duration)
	})

	print "Creating policy. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['autoscalepolicy']['id']:
		return Colors.OKGREEN + "Policy created with id: %s" % jobresult['autoscalepolicy']['id'] + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def createVmProfile(serviceofferingid, templateid, zoneid, projectid):
	job = cloudstack.createAutoScaleVmProfile({
		'serviceofferingid': serviceofferingid,
		'templateid': templateid,
		'zoneid': zoneid,
		'projectid': projectid
	})

	print "Creating vm profile. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['autoscalevmprofile']['id']:
		return Colors.OKGREEN + "Profile created with id: %s" % jobresult['autoscalevmprofile']['id'] + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def createVmGroup(lbruleid, minmembers, maxmembers, scaledownpolicyids, scaleuppolicyids, vmprofileid):
	job = cloudstack.createAutoScaleVmGroup({
		'lbruleid': lbruleid,
		'minmembers': str(minmembers),
		'maxmembers': str(maxmembers),
		'scaledownpolicyids': scaledownpolicyids,
		'scaleuppolicyids': scaleuppolicyids,
		'vmprofileid': vmprofileid
	})

	print "Creating vm group. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['autoscalevmgroup']['id']:
		return Colors.OKGREEN + "Vm group created with id: %s" % jobresult['autoscalevmgroup']['id'] + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def deleteVmGroup(id):
	job = cloudstack.deleteAutoScaleVmGroup({
		'id': id
	})

	print "Deleting vm group. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['success']:
		return Colors.OKGREEN + "Job executed with success." + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def deletePolicy(id):
	job = cloudstack.deleteAutoScalePolicy({
		'id': id
	})

	print "Deleting policy. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['success']:
		return Colors.OKGREEN + "Job executed with success." + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def deleteCondition(id):
	job = cloudstack.deleteCondition({
		'id': id
	})

	print "Deleting condition. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['success']:
		return Colors.OKGREEN + "Job executed with success." + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

def deleteVmProfile(id):
	job = cloudstack.deleteAutoScaleVmProfile({
		'id': id
	})

	print "Deleting vm profile. Job id = %s" % job['jobid']
	jobresult = asyncResult(job['jobid'])
	if jobresult['success']:
		return Colors.OKGREEN + "Job executed with success." + Colors.ENDC
	else:
		return Colors.FAIL + "Error during job execution." + Colors.ENDC

parser = argparse.ArgumentParser(description='Cloudstack Auto Scale script.')
parser.add_argument('-c','--command', help='counter, condition, policy, vmprofile or vmgroup',required=True)
parser.add_argument('-o','--option',help='list, create or delete', required=True)
args = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

config = Config()
api = config.ConfigSectionMap("ConfigApi")['api']
apikey = config.ConfigSectionMap("ConfigApi")['apikey']
secret = config.ConfigSectionMap("ConfigApi")['secret']

cloudstack = CloudStack.Client(api, apikey, secret)

project = config.ConfigSectionMap("Envs")['project']
zone = config.ConfigSectionMap("Envs")['zone']
projectid = listProjectId(project)
zoneid = listZoneId(zone)



if args.option == 'list':
	if args.command == 'counter':
		print Colors.BOLD + "Listing counters:" + Colors.ENDC
		print listCounters()
	elif args.command == 'condition':
		print Colors.BOLD + "Listing conditions...:" + Colors.ENDC
		print listConditions(projectid)
	elif args.command == 'policy':
		print Colors.BOLD + "Listing policies...:" + Colors.ENDC
		print listAutoScalePolicies(projectid)
	elif args.command == 'vmprofile':
		print Colors.BOLD + "Listing vm profiles...:" + Colors.ENDC
		print listAutoScaleVmProfiles(projectid)
	elif args.command == 'vmgroup':
		print Colors.BOLD + "Listing vm groups...:" + Colors.ENDC
		print listAutoScaleVmGroup(projectid)
	else:
		parser.print_help()
if args.option == 'create':
	if args.command == 'counter':
		print Colors.WARNING + "Function not implemented" + Colors.ENDC
	elif args.command == 'condition':
		print Colors.BOLD + "Creating condition...:" + Colors.ENDC
		print Colors.BOLD + "Listing counters:" + Colors.ENDC
		print listCounters()
		counterid = raw_input(Colors.BOLD + "Enter the counter id: " + Colors.ENDC)
		print Colors.BOLD + "Listing operators:" + Colors.ENDC
		print "LT = Less than\nLE = Less than or iqual to\nGT = Greater then\nGE = Greater then or iqual to"
		operator = ''
		operators=['LT', 'LE', 'GT', 'GE']
		while operator not in operators:
			operator = raw_input(Colors.BOLD + "Enter with an operator: " + Colors.ENDC)
			if operator not in operators:
				print Colors.FAIL + "Error: enter with a valid operator" + Colors.ENDC
		try:
			threshold = int(raw_input(Colors.BOLD + "Enter the value for threshold (0% a 100%): " + Colors.ENDC))
		except ValueError:
			print Colors.FAIL + "Error: this value is not integer" + Colors.ENDC
			sys.exit(1)
		print createCondition(counterid, operator, threshold, projectid)
	elif args.command == 'policy':
		print Colors.BOLD + "Creating policy...:" + Colors.ENDC
		print Colors.BOLD + "Listing conditions...:" + Colors.ENDC
		print listConditions(projectid)
		conditionids = raw_input(Colors.BOLD + "Enter the condition id: " + Colors.ENDC)
		action = ''
		actions=['scaleup', 'scaledown']
		while action not in actions:
			action = raw_input(Colors.BOLD + "Enter an action scaleup or scaledown: " + Colors.ENDC)
		try:
			duration = int(raw_input(Colors.BOLD + "Enter the duration (seconds) for which the condition have to be true before action is taken: " + Colors.ENDC))
		except ValueError:
			print Colors.FAIL + "Error: this value is not integer" + Colors.ENDC
			sys.exit(1)
		print createPolicy(conditionids, action, duration)
	elif args.command == 'vmprofile':
		print Colors.BOLD + "Creating vm profile...:" + Colors.ENDC
		print Colors.BOLD + "Listing service offerings...:" + Colors.ENDC
		print listServiceOfferings()
		serviceofferingid = raw_input(Colors.BOLD + "Enter the service offering id: " + Colors.ENDC)
		print Colors.BOLD + "Listing templates...:" + Colors.ENDC
		print listTemplates('featured')
		templateid = raw_input(Colors.BOLD + "Enter the template id: " + Colors.ENDC)
		print createVmProfile(serviceofferingid, templateid, zoneid, projectid)
	elif args.command == 'vmgroup':
		print Colors.BOLD + "Creating vm group...:" + Colors.ENDC
		print Colors.BOLD + "Listing load balancers...:" + Colors.ENDC
		print listLoadBalancerRules(projectid)
		lbruleid = raw_input(Colors.BOLD + "Enter the load balancer id: " + Colors.ENDC)
		try:
			minmembers = int(raw_input(Colors.BOLD + "Enter the minimum value of vms in group: " + Colors.ENDC))
			maxmembers = int(raw_input(Colors.BOLD + "Enter the maximum value of vms in group: " + Colors.ENDC))
		except ValueError:
			print Colors.FAIL + "Error: this value is not integer" + Colors.ENDC
			sys.exit(1)
		print Colors.BOLD + "Listing policies...:" + Colors.ENDC
		print listAutoScalePolicies(projectid)
		scaledownpolicyids = raw_input(Colors.BOLD + "Enter the policy id to scaledown: " + Colors.ENDC)
		scaleuppolicyids = raw_input(Colors.BOLD + "Enter the policy id to scaleup: " + Colors.ENDC)
		print Colors.BOLD + "Listing vm profiles...:" + Colors.ENDC
		print listAutoScaleVmProfiles(projectid)
		vmprofileid = raw_input(Colors.BOLD + "Enter the vm profile id: " + Colors.ENDC)
		print createVmGroup(lbruleid, minmembers, maxmembers, scaledownpolicyids, scaleuppolicyids, vmprofileid)
	else:
		parser.print_help()
if args.option == 'delete':
	if args.command == 'vmgroup':
		print Colors.BOLD + "Listing vm groups...:" + Colors.ENDC
		print listAutoScaleVmGroup(projectid)
		print Colors.BOLD + "Deleting vm group...:" + Colors.ENDC
		id = raw_input(Colors.BOLD + "Enter the vmgroup id: " + Colors.ENDC)
		print deleteVmGroup(id)
	elif args.command == 'policy':
		print Colors.BOLD + "Listing policies...:" + Colors.ENDC
		print listAutoScalePolicies(projectid)
		print Colors.BOLD + "Deleting policy...:" + Colors.ENDC
		id = raw_input(Colors.BOLD + "Enter the policy id: " + Colors.ENDC)
		print deletePolicy(id)
	elif args.command == 'condition':
		print Colors.BOLD + "Listing conditions...:" + Colors.ENDC
		print listConditions(projectid)
		print Colors.BOLD + "Deleting condition...:" + Colors.ENDC
		id = raw_input(Colors.BOLD + "Enter the condition id: " + Colors.ENDC)
		print deleteCondition(id)
	elif args.command == 'vmprofile':
		print Colors.BOLD + "Listing vm profiles...:" + Colors.ENDC
		print listAutoScaleVmProfiles(projectid)
		print Colors.BOLD + "Deleting vm profile...:" + Colors.ENDC
		id = raw_input(Colors.BOLD + "Enter the vm profile id: " + Colors.ENDC)
		print deleteVmProfile(id)
	elif args.command == 'counter':
		print Colors.WARNING + "Function not implemented" + Colors.ENDC
	else:
		parser.print_help()

