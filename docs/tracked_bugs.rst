Tracked Bugs
============

The Kronos virtual system currenly some limitations which are currently tracked `here`_.  Most notably, Kronos is unable to trace/control shells. So if an application/process started in Melody under the control of Kronos spawns shells, then Kronos would be unable to control that process or its children and their behaviour is undefined.

.. _here: https://github.com/Vignesh2208/Kronos/blob/master/TODO


