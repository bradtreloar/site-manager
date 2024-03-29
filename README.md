# Site Manager

## Configuration

Copy `config.example.yml` and replace examples with real values.

## Uptime monitor

Monitor site availability.

### Commands

```bash
# Update statuses for all websites.
python3 run.py update_https_status

# Show statuses for all websites.
python3 run.py show_https_status
```

### Notifications

The command `update_https_status` will send a notification when a site's status changes from `UP` or `UNKNOWN` to `DOWN` or when a site's status changes from `DOWN` to `UP`. The command tests the site's status by making an HTTPS request to the site's homepage.

| From      | To     | Action       |
| --------- | ------ | ------------ |
| `UP`      | `DOWN` | Notify       |
| `DOWN`    | `UP`   | Notify       |
| `UNKNOWN` | `DOWN` | Notify       |
| `UNKNOWN` | `UP`   | Don't notify |

A site's status will only be `UNKNOWN` until the monitor makes its first attempt to connect to the site. Afterwards the status will alternate between `UP` and `DOWN`.

## App backups (Wordpress and Drupal only)

Backup Drupal and Wordpress websites to Amazon S3. The S3 bucket name is derived from the hostname (`sitebackup-example.com`) and the bucket is created if it doesn't exist.

### Commands

```bash
python3 run.py backup_apps
```

### Site requirements

#### Wordpress

This backup utility is designed to be used with Roots Bedrock Wordpress.
- The site must be installed on the server at `~/wordpress`.
- The database settings must be available in `~/wordpress/.env`, and should use the variable names used by Bedrock.
- The uploads folder must be located at `~/wordpress/web/app/uploads`.

`.env` variable names:

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

`.env` variable names:

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
