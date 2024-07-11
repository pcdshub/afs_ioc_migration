# {{ repo_info.name }}
This is an EPICS IOC that is used at LCLS. This repo was automatically transferred to github from an internal filesystem repository via the scripts at https://github.com/pcdshub/afs_ioc_migration.

The original filesystem location was {{ repo_info.afs_source }}.


{% if original_readme_info %}
## Original readme files
{% for fname, text in original_readme_info %}
### {{ fname }}
{{ text }}
{% endfor %}
{% endif %}
