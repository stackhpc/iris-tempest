Prerequisites
-------------

Before you install and configure the service-placeholder-value service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``iris_tempest_plugin`` database:

     .. code-block:: none

        CREATE DATABASE iris_tempest_plugin;

   * Grant proper access to the ``iris_tempest_plugin`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON iris_tempest_plugin.* TO 'iris_tempest_plugin'@'localhost' \
          IDENTIFIED BY 'IRIS_TEMPEST_PLUGIN_DBPASS';
        GRANT ALL PRIVILEGES ON iris_tempest_plugin.* TO 'iris_tempest_plugin'@'%' \
          IDENTIFIED BY 'IRIS_TEMPEST_PLUGIN_DBPASS';

     Replace ``IRIS_TEMPEST_PLUGIN_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``iris_tempest_plugin`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt iris_tempest_plugin

   * Add the ``admin`` role to the ``iris_tempest_plugin`` user:

     .. code-block:: console

        $ openstack role add --project service --user iris_tempest_plugin admin

   * Create the iris_tempest_plugin service entities:

     .. code-block:: console

        $ openstack service create --name iris_tempest_plugin --description "service-placeholder-value" service-placeholder-value

#. Create the service-placeholder-value service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        service-placeholder-value public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        service-placeholder-value internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        service-placeholder-value admin http://controller:XXXX/vY/%\(tenant_id\)s
