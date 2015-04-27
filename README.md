CloudStack Auto Scale Interactive
=================================

Python interactive script to perform autoscale functions with Apache Cloudstack API.

Using Python client library for the CloudStack User API v3.0.0. For older versions,
see the https://github.com/jasonhancock/cloudstack-python-client/tags.

Script Setup
--------

Create the environment and install python packages

```
$ mkvirtualenv CloudstackAutoScale
$ workon CloudstackAutoScale
$ pip install -r requirements.txt
```

You need to create the properties file to setup script with parameters to access cloudstack api and to define zone to auto scale

```
$ touch properties
```

Edit the properties file with the contents below:

```
[ConfigApi]
api: https://host:443/client/api
apikey: xxxxxx
secret: xxxxxx

[Envs]
zone: zonename
project: projectname
```

Executing Script
--------

```
$ python CloudstackAutoScale.py -h
usage: CloudstackAutoScale.py [-h] -c COMMAND -o OPTION

Cloudstack Auto Scale script.

optional arguments:
  -h, --help            show this help message and exit
  -c COMMAND, --command COMMAND
                        counter, condition, policy, vmprofile or vmgroup
  -o OPTION, --option OPTION
                        list, create or delete
```

Examples
--------

```
$ python CloudstackAutoScale.py -c vmgroup -o create

Creating vm group...:
Listing load balancers...:
+--------------------------------------+------------------------+
|                  ID                  | Name                   |
+--------------------------------------+------------------------+
| 1d28361d-137d-4e69-b8b2-4be4bae033d4 | test.com               |
+--------------------------------------+------------------------+
Enter the load balancer id: 1d28361d-137d-4e69-b8b2-4be4bae033d4
Enter the minimum value of vms in group: 2
Enter the maximum value of vms in group: 4
Listing policies...:
+--------------------------------------+-----------+----------+-----------+----------------+--------------------+--------------+
|                  ID                  |   Action  | Duration | QuietTime |     Counter    | RelationalOperator | Threshold(%) |
+--------------------------------------+-----------+----------+-----------+----------------+--------------------+--------------+
| 80df0ec2-788e-46ff-a9c1-1de2209b3dda |  scaleup  |    30    |    300    | Linux User CPU |         GT         |      80      |
| 215d61fd-ac82-4270-96ca-be660f609f19 | scaledown |    30    |    300    | Linux User CPU |         LT         |      10      |
+--------------------------------------+-----------+----------+-----------+----------------+--------------------+--------------+
Enter the policy id to scaledown: 215d61fd-ac82-4270-96ca-be660f609f19
Enter the policy id to scaleup: 80df0ec2-788e-46ff-a9c1-1de2209b3dda
Listing vm profiles...:
+--------------------------------------+-----------------------------+-----------------+
|                  ID                  | Template                    | ServiceOffering |
+--------------------------------------+-----------------------------+-----------------+
| 0dc05453-9a09-4739-8c86-ad2f5c9b3b42 | CentOS 5.10 x86_64 20140930 | Huge-NfsDsk     |
+--------------------------------------+-----------------------------+-----------------+
Enter the vm profile id: 0dc05453-9a09-4739-8c86-ad2f5c9b3b42

Creating vm group. Job id = 69b935eb-2b93-478d-b8e5-20d9f44b65f0
```

```
$ python CloudstackAutoScale.py -c vmgroup -o list

Listing vm groups...:
+--------------------------------------+------------------+----------+------------+------------+---------+-----------+-----------------------------+--------------------+-----------+
|                  ID                  |   LoadBalancer   | Interval | Maxmembers | Minmembers | Running |   Action  |           Counter           | RelationalOperator | Threshold |
+--------------------------------------+------------------+----------+------------+------------+---------+-----------+-----------------------------+--------------------+-----------+
| c0e14ee4-220c-4e7f-9729-7b4111acbd6a | test.com         |    30    |     2      |     1      |    2    | scaledown | Linux User CPU - percentage |         LE         |     10    |
| c0e14ee4-220c-4e7f-9729-7b4111acbd6a | test.com         |    30    |     2      |     1      |    2    |  scaleup  | Linux User CPU - percentage |         GT         |     90    |
+--------------------------------------+------------------+----------+------------+------------+---------+-----------+-----------------------------+--------------------+-----------+
```

TODO
--------
- [X] Display template name and serviceoffering name in vmprofile list function;
- [X] Function to list autoscale vm group;
- [X] Function to list load balancers rules;
- [X] Remove to all commands;
- [ ] Validate all inputs;
- [X] Enable to create an autoscale in projects;
- [X] Display results with tabular format;


References
--------
* https://github.com/jasonhancock/cloudstack-python-client

