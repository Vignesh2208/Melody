Tracked Bugs
============

The Kronos virtual system currenly some limitations which are currently tracked `here`_.  


.. _here: https://github.com/Vignesh2208/Kronos/blob/master/TODO

* Most notably, Kronos is unable to trace/control shells. So if an application/process started in Melody under the control of Kronos spawns shells, then Kronos would be unable to control that process or its children and their behaviour is undefined.

* Further, if a Kronos experiment is abnormally stopped/cancelled without a clean stop, then the next Kronos experiment cannot be run without a system reboot.


