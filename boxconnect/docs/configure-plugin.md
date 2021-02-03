# Configuring the plugin settings
The plugin can be configured post-installation in Moodle by navigating to ``` Site Administration / Plugins / Local plugins / Boxconnect Django Module ```

- **Endpoint:** The endpoint should be set to the base url of the Django service. This url can be found as `Django_URL` in the `.env` file from the Mofa webservice.

- **Token:** The token is used to prevent unautorised calls to the Mofa service, a token can be created using the steps described in the Mofa Analytics [Authentication guide](../../mofa/analytics/docs/authentication.md):
