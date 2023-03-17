# `slowki.jsonnet` - Jsonnet for Ansible

A Jsonnet lookup plugin for Ansible.

## Example

**files/foo.jsonnet**

```jsonnet
local ansible_facts = import 'ansible_facts';

ansible_facts.ansible_host
```

**tasks/main.yaml**

```yaml
# Search for `foo.jsonnet` in the `files` subdirectory and return the evaluted object
- ansible.builtin.debug:
    msg: "{{ lookup('slowki.jsonnet.jsonnet', 'foo.jsonnet') }}" # => my_hostname_here
```
