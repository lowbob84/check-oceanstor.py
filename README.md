# Check Huawei OceanStor plugin for Nagios

It serves as a hardware check of the Huawei OceanStor and was tested on OceanStor 2600V3 and OceanStor 5500v5.

## PLEASE BARE IN MIND THAT YOU STILL BETTER IMPLEMENT MAIL ALARMS ON THE STORAGE SYSTEM ITSELF

## 1. Configuration of SSH on OceanStor and nagios/monitoring server

1. Create user on the Huawei OceanStor with read-only privileges.
2. Add public ssh key through CLI to the user on OceanStor with the command: ```change user_ssh_auth_info general user_name=your_username auth_mode=publickey```
3. It will ask for the public key, copy and paste it.
4. Make sure that user which will execute script has the private key.
5. Try to execute script as user which will be checking the storage system (instructions below in Usage section)
6. Profit :)

## 2. Configuration of plugin and python environment

1. Plugin works with python 3 and 2.7
2. Install python and pip
3. You need to also install "paramiko" module with pip ```pip install paramiko```

## 2. Usage

**Check if the user which will be monitoring the storage system has the private key.**

```bash
usage: check-oceanstor.py [-h] -H <HOSTNAME> -u <USERNAME> -k <KEY_FILE_DESTINATION> -c <COMMAND1,COMMAND2,...,COMMANDX> [-C <CRITICAL_PERC>] [-W <WARNING_PERC>] [-sp <SP_NAME>]

Check Huawei Oceanstor through SSH

    Useable commands:

        lslun - show lun general status
        lsdisk - show disk general status
        lsdiskdomain - show disk_domain general status
        lsexpansionmodule - show expansion module status
        lsinitiator - show initiator status (prints alias name for initiator)
        lsstoragepool - show storage_pool general status
        lspsu - show PSU status
        capacitystoragepool - used with -W and -C arguments, checks free capacity with configured arguments
        lsalert - show ALARM status
        lscontroller - show CONTROLLERs status
        lsallstatuses - show all checks that starts with ls in one output

optional arguments:
  -h, --help            show this help message and exit
  -H <HOSTNAME>, --hostname <HOSTNAME>
  -u <USERNAME>, --username <USERNAME>
  -k <KEY_FILE_DESTINATION>, --key_filename <KEY_FILE_DESTINATION>
  -c <COMMAND1,COMMAND2,...,COMMANDX>, --command <COMMAND1,COMMAND2,...,COMMANDX>
  -C <CRITICAL_PERC>, --critical <CRITICAL_PERC>
  -W <WARNING_PERC>, --warning <WARNING_PERC>
  -sp <SP_NAME>, --storagepool <SP_NAME>
```

## 3. SAMPLE OUTPUT

Output for lsallstatuses:

```text
OK: All LUNs Online
OK: LUN NLSAS01 status: Normal
OK: LUN NLSAS02 status: Normal
OK: LUN NLSAS03 status: Normal
OK: LUN NLSAS04 status: Normal

OK: All DISKs Online and Healthy
OK: DISK CTE0.0 status: Normal
OK: DISK CTE0.1 status: Normal
OK: DISK CTE0.2 status: Normal
OK: DISK CTE0.3 status: Normal
OK: DISK CTE0.4 status: Normal
OK: DISK CTE0.5 status: Normal
OK: DISK CTE0.6 status: Normal
OK: DISK CTE0.7 status: Normal
OK: DISK CTE0.8 status: Normal
OK: DISK DAE010.0 status: Normal
OK: DISK DAE010.1 status: Normal
OK: DISK DAE010.2 status: Normal
OK: DISK DAE010.3 status: Normal

OK: All DISK DOMAINs Online
OK: DISK DOMAIN NLSASDD01 health status: Normal running status: Online

OK: All EXPANSION MODULEs Online
OK: EXPANSION MODULE DAE010.A health status: Normal running status: Running
OK: EXPANSION MODULE DAE010.B health status: Normal running status: Running

OK: All STORAGE POOLs Online
OK: STORAGE POOL NLSAS-R6-01 health status: Normal running status: Online

OK: All PSU Online
OK: PSU CTE0.PSU0 health status: Normal running status: Online
OK: PSU CTE0.PSU1 health status: Normal running status: Online
OK: PSU DAE010.PSU0 health status: Normal running status: Online
OK: PSU DAE010.PSU1 health status: Normal running status: Online
```

Ouput for capacitystoragepool:

```text
OK: STORAGE POOL SP-1-RAID-TP has 11.4% of free space left (1.027TB free of 9.008TB total pool size is left)
```

Error sample for capacitystoragepool

```text

WARNING: STORAGE POOL with name SP-1-RAID-TP was not found

Or not enough space witch -W 25 -C 20 arguments:

CRITICAL: STORAGE POOL SP-1-RAID-TP has only 11.38% of free space left (only 1.025TB free of 9.008TB total pool size is left)

```


Output for Icingaweb2

![image](https://github.com/lowbob84/check-oceanstor.py/blob/master/Icinga2_Templates/Show_checks_icingaweb2.png)

## 4. KNOWN ISSUES

1. Storage Array have active WARNING: "The number of event logs is about to reach the upper limit of 50000."\
Details: This is because all ssh logins are put into the audit log.\
Resolution: Add syslog server for log dumps on OceanStor or go to Alarm Settings and mask alarm "The Space That Stores Event Logs Is To Be Used Up" in event alarms (Alarm Type: "event").

2. Integrated Storage Manager (ISM) sends warning message "Details: The CPU usage of process *ismcli* in controller (controller enclosure CTE0, controller 0A) exceeds the threshold 50%."\
Details: ISM CLI gets to much load on CPU when you are doing concurrent querries from nagios\
Resolution: Monitor your OceanStor by using only one command such as -> ```python check-oceanstor.py -c lslun,lsdisk,lsinitiator``` or even ```python check-oceanstor.py -c lsallstatuses```

## 5. TODO List

1. Add exclude list for ISCSI LUN's
![image](https://github.com/lowbob84/check-oceanstor.py/blob/master/Icinga2_Templates/Issue_Iscsi_Initiator.png)
2. check capacitystoragepool with more than 1 Storagepool
![image](https://github.com/lowbob84/check-oceanstor.py/blob/master/Icinga2_Templates/Issue_Storagepool.png)