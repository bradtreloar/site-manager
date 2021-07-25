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

### Site requirements

#### Wordpress

This backup utility is designed to be used with Roots Bedrock Wordpress.
- The site must be installed on the server at `~/wordpress`.
- The database settings must be available in `~/wordpress/.env`, and should use the variable names used by Bedrock.
- The uploads folder must be located at `~/wordpress/web/app/uploads`.

.env variable names:

| Variable name | Required | Description                                     |
| :------------ | :------- | :---------------------------------------------- |
| `DB_NAME`     | Required | The database name.                              |
| `DB_USER`     | Required | The database username.                          |
| `DB_PASSWORD` | Required | The database password.                          |
| `DB_HOST`     | Optional | The database hostname. Defaults to `localhost`. |
| `DB_PORT`     | Optional | The database port. Defaults to `3306`           |

#### Drupal

This backup utility is designed to be used with Drupal sites created using the same structure as `drupal-composer/drupal-project`.
- The site must be installed on the server at `~/drupal` and the web root must be located at `~/drupal/web`.
- The database settings must be available in `~/drupal/.env`, and should use the variable names listed below.
- The sites folder must be located at `~/drupal/web/sites`.

.env variable names:

| Variable name    | Required | Description                                     |
| :--------------- | :------- | :---------------------------------------------- |
| `DEFAULT_DBNAME` | Required | The database name.                              |
| `DEFAULT_DBUSER` | Required | The database username.                          |
| `DEFAULT_DBPASS` | Required | The database password.                          |
| `DEFAULT_DBHOST` | Optional | The database hostname. Defaults to `localhost`. |
| `DEFAULT_DBPORT` | Optional | The database port. Defaults to `3306`.          |

For multisite installations, replace `DEFAULT` with the site name, in all caps, and replace periods with underscores.

Examples:
- A site called `shop` in sites.php will use `SHOP_DBNAME`.
- A site called 'shop.example.com' in sites.php will use `SHOP_EXAMPLE_COM_DBNAME`.

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