## White Label order management panel for Reyden-X partners

### Environment Variables

|Name|Description|Required|Possible Values|
|---|---|---|---|
|REYDEN_X_LOGIN|Reyden-X Username/Email|Required||
|REYDEN_X_PASSWORD|Reyden-X Password|Required||
|SECRET_KEY|[Secret Key](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-SECRET_KEY)|Required||
|DEBUG|[Debug Mode](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-DEBUG)|Required|True, False|
|CURRENCY|Currency Code (Default: dollar)|Required|dollar, euro, ruble|
|ALLOWED_HOST|Domain|Required||
|DB_NAME|Database Name|Optional||
|DB_USER|Database User|Optional||
|DB_PASSWORD|Database Password|Optional||
|DB_HOST|Database Host (Default: localhost)|Optional||
|DB_PORT|Database Port (Default: 5432)|Optional||

If no environment variables are set for the database connection, 'sqlite' will be used.

### Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup

#### Apply Migrations

```bash
./manage.py makemigrations
./manage.py migrate
```

#### Create Superuser

```bash
./manage.py createsuperuser
```

### CRON

#### Synchronizing your account balance in Reyden-X

```bash
./manage.py sync_balance
```

#### Synchronizing available tariffs in Reyden-X

```bash
./manage.py sync_tariffs --platform=twitch
./manage.py sync_tariffs --platform=youtube
```

#### Synchronizing orders in Reyden-X

```bash
./manage.py sync_orders --platform=twitch
./manage.py sync_orders --platform=youtube
```

#### Synchronizing tasks in Reyden-X

```bash
./manage.py sync_tasks
```

### Working with users

- Add a new user
- In Control Panel, create a new group for users
- For a new user group, select the desired rights and add users to this group

#### Basic user rights for working with data

- Core | user | Can view the cost in the tariffs
- Core | user | Can view the balance on the main balance
- Core | user | Can view Twitch orders
- Core | user | Can view YouTube orders
- Core | user | Can create Twitch orders
- Core | user | Can create YouTube orders
- Core | user | Can view other Twitch orders
- Core | user | Can view other YouTube orders
- Core | user | Can edit other Twitch orders
- Core | user | Can edit other YouTube orders

### Development

You can modify this template to suit any of your own tasks, and add your own changes to the business logic.

Useful links:

[Django Framework](https://www.djangoproject.com/)

[sneat-bootstrap-html-admin-template-free](https://github.com/themeselection/sneat-bootstrap-html-admin-template-free/)

[Reyden-X API](https://api.reyden-x.com/docs)
