# Authentication guide

For Boxconnect to connect with Mofa it requires an authentication token. If you haven't created an authentication token yet, you can create one by going into a terminal and navigate to the Mofa directory in which the `up-local.yml` file is located. Run the following command, where admin is the username you use for logging into Mofa:

```bash
python manage.py drf_create_token admin
```

1. If you already have an authentication token or just created one, you can find it by logging into the Mofa server with your user credentials. 

2. After logging in you will see that one of headers is the Auth token, with under that header the option Tokens. Click on this.

3. Copy the value under the header key. This is the key that Boxconnect needs to connect with Mofa's analytics app.

4. Go to settings page for boxconnect in moodle and paste the token in the `token` field.

Boxconnect will now be able to connect with Mofa.
