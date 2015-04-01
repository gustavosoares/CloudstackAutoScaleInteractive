#!/usr/bin/env python

__author__ = 'Cristiano Casado <co.casado@gmail.com>'
__version__ = '0.3'

from Config import Config
from prettytable import PrettyTable
import CloudStack
import sys
import argparse
import time

class Colors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
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

def listCounters():
	print Colors.WARNING + "Listing counters:" + Colors.ENDC
	counters = cloudstack.listCounters()
	table = PrettyTable(["ID", "Name", "Source"])
	table.align["Name"] = "l"
	table.align["Source"] = "l"
	for counter in counters:
		table.add_row([counter['id'], counter['name'], counter['source']])
	print table

def listConditions():
	print Colors.WARNING + "Listing conditions...:" + Colors.ENDC
	conditions = cloudstack.listConditions({'projectid': projectid})
	table = PrettyTable(["ID", "Counter", "RelationalOperator", "Threshold(%)"])

	for condition in conditions:
		counters = (condition.get('counter'))
		for counter in counters:
			table.add_row([condition['id'], counter['name'], condition['relationaloperator'], condition['threshold']])
	print table

def listServiceOfferings():
	print Colors.WARNING + "Listing service offerings...:" + Colors.ENDC
	serviceofferings = cloudstack.listServiceOfferings()
	table = PrettyTable(["ID", "Name"])
	table.align["Name"] = "l"

	for serviceoffering in serviceofferings:
		table.add_row([serviceoffering['id'], serviceoffering['name']])
	print table

def listTemplates():
	print Colors.WARNING + "Listing templates...:" + Colors.ENDC
	templates = cloudstack.listTemplates({'templatefilter': 'featured'})
	table = PrettyTable(["ID", "Name"])
	table.align["Name"] = "l"

	for template in templates:
		table.add_row([template['id'], template['name']])
	print table

def listLoadBalancerRules():
	print Colors.WARNING + "Listing load balancers...:" + Colors.ENDC
	lbrules = cloudstack.listLoadBalancerRules({'projectid': projectid})
	table = PrettyTable(["ID", "Name"])
	table.align["Name"] = "l"

	for lbrule in lbrules:
		table.add_row([lbrule['id'], lbrule['name']])
	print table

def listAutoScalePolicies():
	print Colors.WARNING + "Listing policies...:" + Colors.ENDC
	autoscalepolicies = cloudstack.listAutoScalePolicies()
	table = PrettyTable(["ID", "Action", "Duration", "QuietTime", "Counter", "RelationalOperator", "Threshold(%)"])

	for autoscalepolicy in autoscalepolicies['autoscalepolicy']:
		conditions = (autoscalepolicy.get('conditions'))
		for condition in conditions:
			counters = (condition.get('counter'))
			for counter in counters:
				table.add_row([autoscalepolicy['id'], autoscalepolicy['action'], autoscalepolicy['duration'], autoscalepolicy['quiettime'], counter['name'], condition['relationaloperator'], condition['threshold']])
	print table

def listAutoScaleVmProfiles():
	print Colors.WARNING + "Listing vm profiles...:" + Colors.ENDC
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
	print table

def listAutoScaleVmGroup():
	print Colors.WARNING + "Listing vm groups...:" + Colors.ENDC
	vmgroups = cloudstack.listAutoScaleVmGroups({'projectid': projectid})
	table = PrettyTable(["ID", "LoadBalancer", "Interval", "Maxmembers", "Minmembers", "Action", "Counter", "RelationalOperator", "Threshold"])

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
					table.add_row([vmgroup['id'], lbname, vmgroup['interval'], vmgroup['maxmembers'], vmgroup['minmembers'], scaledownpolicy['action'], counterd['name'], conditiond['relationaloperator'], conditiond['threshold']])
		for scaleuppolicy in scaleuppolicies:
			conditionsu = (scaleuppolicy.get('conditions'))
			for conditionu in conditionsu:
				countersu = (conditionu.get('counter'))
				for counteru in countersu:
					table.add_row([vmgroup['id'], lbname, vmgroup['interval'], vmgroup['maxmembers'], vmgroup['minmembers'], scaleuppolicy['action'], counteru['name'], conditionu['relationaloperator'], conditionu['threshold']])
	print table

def createCondition():
	print Colors.WARNING + "Creating condition...:" + Colors.ENDC
	listCounters()
	counterid = raw_input(Colors.WARNING + "Enter the counter id: " + Colors.ENDC)
	print Colors.WARNING + "Listing operators:" + Colors.ENDC
	print "LT = Less than\nLE = Less than or iqual to\nGT = Greater then\nGE = Greater then or iqual to"
	operator = ''
	operators=['LT', 'LE', 'GT', 'GE']
	while operator not in operators:
		operator = raw_input(Colors.WARNING + "Enter with an operator: " + Colors.ENDC)
		if operator not in operators:
			print Colors.FAIL + "Enter with a valid operator" + Colors.ENDC
	threshold = raw_input(Colors.WARNING + "Enter the value for threshold (0% a 100%): " + Colors.ENDC)
	
	job = cloudstack.createCondition({
		'counterid': counterid,
		'relationaloperator': operator,
		'threshold': threshold,
		'projectid': projectid
	})

	print "Creating condition. Job id = %s" % job['jobid']
	print asyncResult(job['jobid'])

def createPolicy():
	print Colors.WARNING + "Creating policy...:" + Colors.ENDC
	listConditions()
	conditionids = raw_input(Colors.WARNING + "Enter the condition id: " + Colors.ENDC)
	action = ''
	actions=['scaleup', 'scaledown']
	while action not in actions:
		action = raw_input(Colors.WARNING + "Enter an action scaleup or scaledown: " + Colors.ENDC)
	duration = raw_input(Colors.WARNING + "Enter the duration (seconds) for which the condition have to be true before action is taken: " + Colors.ENDC)

	job = cloudstack.createAutoScalePolicy({
		'conditionids': conditionids,
		'action': action,
		'duration': duration
	})

	print "Creating policy. Job id = %s" % job['jobid']
	print asyncResult(job['jobid'])

def createVmProfile():
	print Colors.WARNING + "Creating vm profile...:" + Colors.ENDC
	listServiceOfferings()
	serviceofferingid = raw_input(Colors.WARNING + "Enter the service offering id: " + Colors.ENDC)
	listTemplates()
	templateid = raw_input(Colors.WARNING + "Enter the template id: " + Colors.ENDC)

	job = cloudstack.createAutoScaleVmProfile({
		'serviceofferingid': serviceofferingid,
		'templateid': templateid,
		'zoneid': zoneid,
		'projectid': projectid
	})

	print "Creating vm profile. Job id = %s" % job['jobid']
	print asyncResult(job['jobid'])

def createVmGroup():
	print Colors.WARNING + "Creating vm group...:" + Colors.ENDC
	listLoadBalancerRules()
	lbruleid = raw_input(Colors.WARNING + "Enter the load balancer id: " + Colors.ENDC)
	minmembers = raw_input(Colors.WARNING + "Enter the minimum value of vms in group: " + Colors.ENDC)
	maxmembers = raw_input(Colors.WARNING + "Enter the maximum value of vms in group: " + Colors.ENDC)
	listAutoScalePolicies()
	scaledownpolicyid = raw_input(Colors.WARNING + "Enter the policy id to scaledown: " + Colors.ENDC)
	scaleuppolicyid = raw_input(Colors.WARNING + "Enter the policy id to scaleup: " + Colors.ENDC)
	listAutoScaleVmProfiles()
	vmprofileid = raw_input(Colors.WARNING + "Enter the vm profile id: " + Colors.ENDC)

	job = cloudstack.createAutoScaleVmGroup({
		'lbruleid': lbruleid,
		'minmembers': minmembers,
		'maxmembers': maxmembers,
		'scaledownpolicyids': scaledownpolicyid,
		'scaleuppolicyids': scaleuppolicyid,
		'vmprofileid': vmprofileid
	})

	print "Creating vm group. Job id = %s" % job['jobid']
	print asyncResult(job['jobid'])

parser = argparse.ArgumentParser(description='Cloudstack Auto Scale script.')
parser.add_argument('-c','--command', help='counter, condition, policy, vmprofile or vmgroup',required=True)
parser.add_argument('-o','--option',help='list or create', required=True)
args = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

config = Config()
api = config.ConfigSectionMap("ConfigApi")['api']
apikey = config.ConfigSectionMap("ConfigApi")['apikey']
secret = config.ConfigSectionMap("ConfigApi")['secret']
projectid = config.ConfigSectionMap("Envs")['projectid']
zoneid = config.ConfigSectionMap("Envs")['zoneid']

cloudstack = CloudStack.Client(api, apikey, secret)

if args.option == 'list':
	if args.command == 'counter':
		listCounters()
	elif args.command == 'condition':
		listConditions()
	elif args.command == 'policy':
		listAutoScalePolicies()
	elif args.command == 'vmprofile':
		listAutoScaleVmProfiles()
	elif args.command == 'vmgroup':
		listAutoScaleVmGroup()
	else:
		parser.print_help()
if args.option == 'create':
	if args.command == 'counter':
		print "Function not implemented"
	elif args.command == 'condition':
		createCondition()
	elif args.command == 'policy':
		createPolicy()
	elif args.command == 'vmprofile':
		createVmProfile()
	elif args.command == 'vmgroup':
		createVmGroup()
	else:
		parser.print_help()

