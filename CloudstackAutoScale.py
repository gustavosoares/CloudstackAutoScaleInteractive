#!/usr/bin/env python

__author__ = 'Cristiano Casado <co.casado@gmail.com>'
__version__ = '0.2'

from Config import Config
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

	for counter in counters:
		print "ID = %s | Name = %s | Source = %s" % (counter['id'], counter['name'], counter['source'])

def listConditions():
	print Colors.WARNING + "Listing conditions...:" + Colors.ENDC
	conditions = cloudstack.listConditions({'projectid': projectid})

	for condition in conditions:
		print "ID = %s | Counter = %s | Operator = %s | Threshold = %s" % (condition['id'], condition['counter'], condition['relationaloperator'], condition['threshold'])

def listServiceOfferings():
	print Colors.WARNING + "Listing service offerings...:" + Colors.ENDC
	serviceofferings = cloudstack.listServiceOfferings()

	for serviceoffering in serviceofferings:
		print "ID = %s | Name = %s" % (serviceoffering['id'], serviceoffering['name'])

def listTemplates():
	print Colors.WARNING + "Listing templates...:" + Colors.ENDC
	templates = cloudstack.listTemplates({'templatefilter': 'featured'})

	for template in templates:
		print "ID = %s | Name = %s" % (template['id'], template['name'])

def listLoadBalancerRules():
	print Colors.WARNING + "Listing load balancers...:" + Colors.ENDC
	lbrules = cloudstack.listLoadBalancerRules({'projectid': projectid})

	for lbrule in lbrules:
		print "ID = %s | Name = %s" % (lbrule['id'], lbrule['name'])

def listAutoScalePolicies():
	print Colors.WARNING + "Listing policies...:" + Colors.ENDC
	autoscalepolicies = cloudstack.listAutoScalePolicies()

	for autoscalepolicy in autoscalepolicies['autoscalepolicy']:
		print "ID = %s | Action = %s | Conditions = %s" % (autoscalepolicy['id'], autoscalepolicy['action'], autoscalepolicy['conditions'])

def listAutoScaleVmProfiles():
	print Colors.WARNING + "Listing vm profiles...:" + Colors.ENDC
	vmprofiles = cloudstack.listAutoScaleVmProfiles({'projectid': projectid})

	for vmprofile in vmprofiles:
		templateid = vmprofile['templateid']
		templates = cloudstack.listTemplates({'templatefilter': 'featured', 'id': templateid, 'zoneid': zoneid})
		serviceofferingid = vmprofile['serviceofferingid']
		serviceofferings = cloudstack.listServiceOfferings({'id': serviceofferingid})
		for template in templates:
			for serviceoffering in serviceofferings:
				print "ID = %s | Template = %s | ServiceOffering = %s" % (vmprofile['id'], template['name'], serviceoffering['name'])

def listAutoScaleVmGroup():
	print Colors.WARNING + "Listing vm groups...:" + Colors.ENDC
	vmgroups = cloudstack.listAutoScaleVmGroups({'projectid': projectid})

	for vmgroup in vmgroups:
		lbruleid = vmgroup['lbruleid']
		lbrules = cloudstack.listLoadBalancerRules({'lbruleid': lbruleid})
		for lbrule in lbrules:
			print "ID = %s | LoadBalancer = %s | Interval = %s | Maxmembers = %s | Minmembers = %s | Scaledownpolicies = %s | Scaleuppolicies = %s" % (vmgroup['id'], lbrule['name'], vmgroup['interval'], vmgroup['maxmembers'], vmgroup['minmembers'], vmgroup['scaledownpolicies'], vmgroup['scaleuppolicies'])

def createCondition():
	print Colors.WARNING + "Creating condition...:" + Colors.ENDC
	listCounters()
	counterid = raw_input(Colors.WARNING + "Enter the counter id: " + Colors.ENDC)
	#TODO: validar input
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

