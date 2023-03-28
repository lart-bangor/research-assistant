lart.appLock
============

App locking state management.

The `lart.appLock` namespace provides functionality for the management of
the app's global lock state. The lock state is used to optionally enable
or disable certain functionality in the UI, such as the user's ability to
open the right-click context menu. Generally, the functionality that is
made dependent on the lock state should only include that functionality
which may be inadvertently used by a user during a task that could corrupt
the responses collected for that task (e.g. by right clicking they could
reload, resubmit, inspect the source logic, etc.).


.. **Namespaces**


.. **Types**


**Attributes**

.. js:autoattribute:: lart.appLock.state

.. js:autoattribute:: lart.appLock.switches

**Functions**

.. js:autofunction:: lart.appLock._contextMenuHandler

.. js:autofunction:: lart.appLock._setSwitchState

.. js:autofunction:: lart.appLock.lock

.. js:autofunction:: lart.appLock.registerSwitch

.. js:autofunction:: lart.appLock.toggleState

.. js:autofunction:: lart.appLock.unlock

.. **Classes**