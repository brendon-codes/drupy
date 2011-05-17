Drupy FAQ
=========

This FAQ is no longer maintained.


1.  Why port Drupal to Python?

The primary reason is to expose PHP developers to Python in
a familiar environment.

2.  I am a PHP programmer. Why should I care about Python?

Python places an emphasis on code readability and
consistancy. Python has excellent OOP and namespace support integrated
throughout. This means your code is easier to write, and easier to debug.

3.  Does Drupy aim to provide 100% Drupal API compatibility?

Yes. If an API function is available in Drupal, it either already is
or will be available in Drupy.

4.  Will Drupal modules work out of the box with Drupy?

No. However, Drupy provides an abstraction library and some conversion
scripts to make the process very simple. It is not uncommon to port a
non-core module at about 200 lines per hour.

5.  How would Drupy implement an API call such as "node_load()"?

In Drupy, "node_load()" would be called as "plugin_node.load()".

6.  What does a Drupal module look like in Drupy?

The path of the system module (system.module) is
"plugins/system/__init__.py". The hook "system_init" is renamed
to "hook_init".

7.  Is this a fork of Drupal?

 No. This is a port to a different language.

8.  What are the primary differences between Drupal and Drupy?

*  Drupy is written in Python. Drupal is written in PHP.
*  Any reference to a "module" in Drupal is called a "plugin" in Drupy.
*  Drupal does not make use of namespaces and OOP structures. Drupy is 100% fully namespaced.

9.  Is Drupy fully PEP-8 compliant?

No.

10.  Do any other similar projects exist?

Not that I am aware of.

11.  Will Drupy run as WSGI?

That is an intended goal.


