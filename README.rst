Lantern
===============

Lantern is an Apache2 Licensed security scan automation library, written in Python.

Lantern provides an easy way to integrate with security providers in python.

.. code-block:: pycon

    >>> l = lantern.API('username', 'password', 'app_name', 'build_name')
    >>> l.upload_file_retry('/my/usr/binaries_dir')
    <?xml version="1.0" encoding="UTF-8"?>
    <filelist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="https://analysiscenter.veracode.com/schema/2.0/filelist"
    xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/filelist
    https://analysiscenter.veracode.com/resource/2.0/filelist.xsd" 
    account_id="00001" app_id="00001" build_id="00001">
    <file file_id="21271739" file_name="TestFile01.jsp" file_status="Uploaded"/>
    <file file_id="21243504" file_name="TestFile02.jsp" file_status="Uploaded"/>
    <file file_id="21243519" file_name="TestFile03.class" file_status="Uploaded"/>
    <file file_id="21243523" file_name="TestFile04.jsp" file_status="Uploaded"/>
    <file file_id="21243525" file_name="TestFile05.htm" file_status="Uploaded"/>
    <file file_id="21243527" file_name="TestFile06.class" file_status="Uploaded"/>
    <file file_id="21265337" file_name="TestFile07.jsp" file_status="Uploaded"/>
    <file file_id="21265341" file_name="TestFile08.jspi" file_status="Uploaded"/>
    <file file_id="21265343" file_name="TestFile09.jsp" file_status="Uploaded"/>
    </filelist>'


Features
--------

- Lantern is under heavy development. Many things will change. Beware.
- API Polling with exponential backoff
- Optionally create a blacklist (for ignoring third party binaries or test binaries)
- Integration with Veracode


Installation
------------

None yet! Build from source, or wait until I build installation infrastructure. :)


Documentation
-------------

You're reading it!
Documentation will expand to a Sphinx project soon™.

Compatibility
--------------
- Python 3.2.
- Tests: nose
- Veracode: 4.0 API

Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork `the repository`_ on Github to start making your changes to the **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: http://github.com/dechols/lantern
.. _AUTHORS: https://github.com/dechols/lantern/blob/master/AUTHORS.rst