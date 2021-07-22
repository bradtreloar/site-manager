# Site Manager

## Configuration

### Sites

```yaml
# config.yml

sites:
  # Minimal site config.
  example.com: {}
```

## Uptime monitor

Monitor site availability.

Commands:

```bash
# Update statuses for all websites.
python3 run.py update_https_status

# Show statuses for all websites.
python3 run.py update_https_status
```
