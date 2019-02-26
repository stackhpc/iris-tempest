2. Edit the ``/etc/iris_tempest_plugin/iris_tempest_plugin.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://iris_tempest_plugin:IRIS_TEMPEST_PLUGIN_DBPASS@controller/iris_tempest_plugin
