# ldap-bulk-change: A command-line bulk change agent for LDAP

Built to solve a specific business use for PSU, the bulk change command line tool operates by finding all users within a given base DN matching a given filter and using a regex substitution on one given attribute. This has proven exceptionally useful for situations such as where every user's email address needs to have the domain component changed when moving from the production to development environments.

## Installation

1. Clone to directory of choice.
2. 'pip install -r requirements.txt'

## Usage

```
usage: ldap-bulk-change.py [-h] [--verbose] [--nossl]
                           [--environment [ENVIRONMENT]]
                           [host] [port] [bind_dn] [password] [base_dn] filter
                           change_attr regexp replace

positional arguments:
  filter                An LDAP filter to limit the DNs operated on.
  change_attr           The attribute to be changed.
  regexp                A regexp used to determine the new value of
                        change_attr.
  replace               The value to substitute into the new value of
                        change_attr.
```

* regexp is matched against the current value of change_attr to determine if a change is needed and can have capture groups to be used in replace.
* replace is the value to replace change_attr with. Can reference capture groups from regexp with \1...\X.


## Configuration File

Commonly-used environments can be stored in a configuration file at ~/.ldap_envs which follows the Python ConfigParser/INI format. These can be referenced with the *-e* command-like argument to avoid having to input commonly-used values on the command line.

```ini
[ENVIRONMENT]
host: hostname
port: 389
bind_dn: uid=admin,ou=admins,dc=example,dc=com
password: ********
base_dn: ou=people,dc=example,dc=com
```

## Roadmap

A few obvious improvements are needed, and are documented as TODO comments in the script.