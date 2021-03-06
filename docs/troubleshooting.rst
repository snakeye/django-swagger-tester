.. _troubleshooting:

***************
Troubleshooting
***************

Activating logs for debugging
-----------------------------

To enable logs form the package, simply add the logger ``django_swagger_tester`` to your logging setup::

    LOGGING = {
        'loggers': {
            'django_swagger_tester': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }

This will activate full debug logging, and make it easier to track what is happening.

Run Django with warnings enabled
--------------------------------
Start ``manage.py runserver``  with the ``-Wd`` parameter to enable warnings that normally are suppressed.

.. code-block:: bash

    python -Wd manage.py runserver


Use the demo project as a reference
-----------------------------------
There is a simple demo project available in the ``demo_project`` folder. This can be considered a source of inspiration for something, though it's very minimal.


Ask for help
------------
Still no luck? Go ahead and create an `issue on GitHub <https://github.com/sondrelg/django-swagger-tester/issues>`_ and ask for help there.
