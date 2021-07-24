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

## Wordpress and Drupal website Backups

Backup Drupal and Wordpress websites to Amazon S3. The S3 bucket name is derived from the hostname (`sitebackup-example.com`) and the bucket is created if it doesn't exist.

Commands:

```bash
# Backup Wordpress sites.
python3 run.py backup_wordpress

# Backup Drupal 8+ sites.
python3 run.py backup_drupal
```

### Required config

Each Wordpress and Drupal site config must include the `app` and `ssh` attributes, and you must provide credentials for AWS.

SSH settings:

| Name     | Required | Description                                               |
| :------- | :------- | :-------------------------------------------------------- |
| user     | Required | the SSH username                                          |
| port     | Optional | the SSH port. Defaults to port 22 if not given            |
| hostname | Optional | the SSH host. The site's hostname will be used by default |

Example:

```yaml
sites:
  drupalexample.com:
    app: drupal
    ssh:
      user: drupalexample
  wordpressexample.com:
    app: wordpress
    ssh:
      user: wordpressexample
  # Example with more SSH settings
  drupalexample2.com:
    app: drupal
    ssh:
      host: example2.com
      port: 21212
      user: drupalexample2

aws:
  aws_access_key_id: xxxxxxxxxxxxxxxxxxx
  aws_secret_access_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Optional config

If any of the SSH hosts require Juniper web authentication, you can provide the configuration and the site manager will attempt to start a web authentication session.

**This has only been tested on `webauth5.micron21.com`.**

Example:

```yaml
webauth:
  cp-kil-m-016.micron21.com:
    login_url: "https://webauth5.micron21.com"
    webauth_url: "https://webauth5.micron21.com/webauth_operation.php"
    username: xxxxxxxxxxxxxxxxxx
    password: xxxxxxxxxxxxxxxxxx
```