# OpsDroid OpenProject webhook

Define a webhook for OpenProject to Mattermost

## Action type:
OpenProject define 6 action types differents:
- work_package:created
- work_package:updated
- project:created
- project:updated
- time_entry:created
- attachment:created

Only `work_package:created` action is implemented

## Skill configuration:
```
skills:
- name: openproject
  path: ./openproject/skill.py
  openproject_url: "http://localhost:8080"
```

Replace `openproject_url` by OpenProject URL