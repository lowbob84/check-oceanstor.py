import paramiko
import sys
import argparse
import re
from argparse import RawTextHelpFormatter


if __name__ == "__main__":

    # Exit code for nagios 0 -OK, 1 - Warning, 2 - Critical
    exit_code = 0
    output_info = ""
    # OceanStor failed Health and Running status
    failed_health_status = ["Offline", "Pre-fail", "Fault", "No Input", "--"]
    failed_running_status = ["Offline", "Reconstruction", "Balancing", "--"]

    space_bytes_dict = {"GB": 1024*1024*1024, "TB": 1024*1024*1024*1024, "PB": 1024*1024*1024*1024*1024}


    def check_empty_respone():
        pass


    def set_exit_code(code):
        # If code is more critical than actual level set it
        global exit_code
        if code > exit_code:
            exit_code = code


    def lslun():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show lun general')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no LUNs defined\n"

        # Check if there are any critical LUNs
        if not any(line.split()[4] in failed_health_status for line in ssh_lines):
            output_info += "OK: All LUNs Online \n"
        else:
            output_info += "CRITICAL: check your LUN status below \n"
            set_exit_code(2)

        for line in ssh_lines:
            # Assign values
            name, status = line.split()[1], line.split()[4]

            # Check for errors
            if status == "Normal":
                output_info += "OK: LUN {} status: {}\n".format(name, status)
            else:
                output_info += "CRITICAL: LUN {} status: {}\n".format(name, status)

        return output_info


    def lsdisk():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show disk general')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no DISKs defined\n"

        # Check if there are any critical DISKs
        if not any(line.split()[1] in failed_health_status for line in ssh_lines):
            output_info += "OK: All DISKs Online and Healthy \n"
        else:
            output_info += "CRITICAL: check your DISK status below \n"
            set_exit_code(2)

        for line in ssh_lines:
            # Assign values
            slot, status, disk_type, capacity, role = line.split()[0], line.split()[1], line.split()[3], line.split()[4], line.split()[5]

            # Check for errors
            if status == "Normal":
                output_info += "OK: DISK {} status: {}\n".format(slot, status)
            else:
                output_info += "CRITICAL: DISK {} status: {}\n role: {}\n type: {}\n capacity: {}\n".format(slot, status, role, disk_type, capacity)

        return output_info


    def lsdiskdomain():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show disk_domain general')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no DISK DOMAINs defined\n"

        # Check if there are any critical DISK DOMAINs by Health status
        if not any(line.split()[2] in failed_health_status for line in ssh_lines):
            output_info += "OK: All DISK DOMAINs Online \n"
        else:
            output_info += "CRITICAL: check your DISK DOMAIN status \n"
            set_exit_code(2)

        # Check if there are any critical DISK DOMAINs by Running status
        if any(line.split()[3] in failed_running_status for line in ssh_lines):

            # Clear OK/Critical message set by Health Status, because Running is Critical
            output_info = ""
            output_info += "CRITICAL: Check your DISK DOMAIN status \n"
            set_exit_code(2)

        for line in ssh_lines:
            # Assign values
            name, health_status, running_status = line.split()[1], line.split()[2], line.split()[3]

            # Check for errors in health status
            if health_status == "Normal":
                # Check for errors in running status
                if running_status in failed_running_status:
                    output_info += "CRITICAL: DISK DOMAIN {} health status: {} running status: {}\n".format(name, health_status, running_status)
                else:
                    output_info += "OK: DISK DOMAIN {} health status: {} running status: {}\n".format(name, health_status, running_status)
            else:
                output_info += "CRITICAL: DISK DOMAIN {} health status: {} running status: {}\n".format(name, health_status, running_status)

        return output_info


    def lsexpansionmodule():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show expansion_module')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no EXPANSION MODULEs defined\n"

        # Check if there are any critical EXPANSION MODULEs by Health status
        if not any(line.split()[1] in failed_health_status for line in ssh_lines):
            output_info += "OK: All EXPANSION MODULEs Online \n"
        else:
            output_info += "CRITICAL: check your EXPANSION MODULEs status \n"
            set_exit_code(2)

        # Check if there are any critical EXPANSION MODULEs by Running status
        if any(line.split()[2] in failed_running_status for line in ssh_lines):

            # Clear OK/Critical message set by Health Status, because Running is Critical
            output_info = ""
            output_info += "CRITICAL: Check your EXPANSION MODULEs status \n"
            set_exit_code(2)

        for line in ssh_lines:
            # Assign values
            expansion_id, health_status, running_status = line.split()[0], line.split()[1], line.split()[2]

            # Check for errors in health status
            if health_status == "Normal":
                # Check for errors in running status
                if running_status in failed_running_status:
                    output_info += "CRITICAL: EXPANSION MODULE {} health status: {} running status: {}\n".format(expansion_id, health_status, running_status)
                else:
                    output_info += "OK: EXPANSION MODULE {} health status: {} running status: {}\n".format(expansion_id, health_status, running_status)
            else:
                output_info += "CRITICAL: EXPANSION MODULE {} health status: {} running status: {}\n".format(expansion_id, health_status, running_status)

        return output_info


    def lsinitiator():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show initiator')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no INITIATORs defined\n"

        # Check if there are any critical INITIATORs
        if not any(line.split()[1] == "Offline" for line in ssh_lines):
            output_info += "OK: All INITIATORs Online \n"
        else:
            output_info += "WARNING: INITIATOR OFFLINE \n"
            set_exit_code(1)

        for line in ssh_lines:
            # Assign values
            name, status = line.split()[0], line.split()[1]

            # Check for errors
            if status == "Online":
                output_info += "OK: INITIATOR {} status: {}\n".format(name, status)
            else:
                output_info += "WARNING: INITIATOR {} status: {}\n".format(name, status)

        return output_info


    def lsstoragepool():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show storage_pool general')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no STORAGE POOLs defined\n"

        # Check if there are any critical STORAGE POOLs by Health status
        if not any(line.split()[3] in failed_health_status for line in ssh_lines):
            output_info += "OK: All STORAGE POOLs Online \n"
        else:
            output_info += "CRITICAL: Check your STORAGE POOL status \n"
            set_exit_code(2)

        # Check if there are any critical STORAGE POOLs by Running status
        if any(line.split()[4] in failed_running_status for line in ssh_lines):

            # Clear OK/Critical message set by Health Status, because Running is Critical
            output_info = ""
            output_info += "CRITICAL: Check your STORAGE POOL status \n"
            set_exit_code(2)

        for line in ssh_lines:
            # Assign values
            name, health_status, running_status = line.split()[1], line.split()[3], line.split()[4]

            # Check for errors
            if running_status == "Online":
                output_info += "OK: STORAGE POOL {} health status: {} running status: {}\n".format(name, health_status, running_status)
            else:
                output_info += "CRITICAL: STORAGE POOL {} health status: {} running status: {}\n".format(name, health_status, running_status)

        return output_info


    def lspsu():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show power_supply')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            output_info += "CRITICAL: No PSUs were found \n"
            set_exit_code(2)

        # Check if there are any critical PSUs
        # split string per double spaces because of status "No Input" at Health status column
        if not any([x for x in re.split(r"\s{2,}", line) if x][2] in failed_running_status for line in ssh_lines):
            output_info += "OK: All PSU Online \n"
        else:
            output_info += "CRITICAL: Check your PSU status \n"
            set_exit_code(2)

        for line in ssh_lines:
            # split string per double spaces because of status "No Input" at Health status column
            split_line = [x for x in re.split(r"\s{2,}", line) if x]

            # Assign values
            name, health_status, running_status = split_line[0], split_line[1], split_line[2]

            # Check for errors
            if running_status == "Online":
                output_info += "OK: PSU {} health status: {} running status: {}\n".format(name, health_status, running_status)
            else:
                output_info += "CRITICAL: PSU {} health status: {} running status: {}\n".format(name, health_status, running_status)

        return output_info


    def capacitystoragepool():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show storage_pool general')
        ssh_lines = ssh_stdout.readlines()[4:]
        output_info = ""

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no STORAGE POOLs defined\n"

        try:
            # check if warning isn't lower than critical
            if warning <= critical:
                output_info += "WARNING: --warning cannot be lesser or equal --critical"
                set_exit_code(1)
                return output_info

            # If argument --storagepool was specified than check this pool else go with all storage pools check
            if "storage_pool_name" in globals():

                # Initialize variable which checks if storage pool with specified name exists
                sp_was_found = False

                for line in ssh_lines:
                    # Assign values
                    name, total_space, free_space = line.split()[1], line.split()[5], line.split()[6]

                    # If there is storage pool with specified name
                    if name == storage_pool_name:
                        # Set variable to check if storage pool with specified name exists
                        sp_was_found = True

                        # Set variables for storage checks
                        total_space_bytes = float(total_space[:-2]) * space_bytes_dict[total_space[-2:]]
                        free_space_bytes = float(free_space[:-2]) * space_bytes_dict[free_space[-2:]]

                        # Check free space percentage
                        free_space_perc = free_space_bytes / total_space_bytes * 100

                        if free_space_perc <= critical:
                            output_info += "CRITICAL: STORAGE POOL {} has only {}% of free space left (only {} free of {} total pool size is left)\n".format(name, round(free_space_perc, 2), free_space, total_space)
                            set_exit_code(2)
                        elif free_space_perc <= warning:
                            output_info += "WARNING: STORAGE POOL {} has only {}% of free space left (only {} free of {} total pool size is left)\n".format(name, round(free_space_perc, 2), free_space, total_space)
                            set_exit_code(1)
                        else:
                            output_info += "OK: STORAGE POOL {} has {}% of free space left ({} free of {} total pool size is left)\n".format(name, round(free_space_perc, 2), free_space, total_space)

                    # If storage pool with specified name was not found than show warning message
                    if not sp_was_found:
                        output_info += "WARNING: STORAGE POOL with name {} was not found\n".format(storage_pool_name)
                        set_exit_code(1)

            else:

                for line in ssh_lines:
                    # Assign values
                    name, total_space, free_space = line.split()[1], line.split()[5], line.split()[6]

                    # Set variables for storage checks
                    total_space_bytes = float(total_space[:-2]) * space_bytes_dict[total_space[-2:]]
                    free_space_bytes = float(free_space[:-2]) * space_bytes_dict[free_space[-2:]]

                    # Check free space percentage
                    free_space_perc = free_space_bytes / total_space_bytes * 100

                    if free_space_perc <= critical:
                        output_info += "CRITICAL: STORAGE POOL {} has only {}% of free space left (only {} free of {} total pool size is left)\n".format(name, round(free_space_perc, 2), free_space, total_space)
                        set_exit_code(2)
                    elif free_space_perc <= warning:
                        output_info += "WARNING: STORAGE POOL {} has only {}% of free space left (only {} free of {} total pool size is left)\n".format(name, round(free_space_perc, 2), free_space, total_space)
                        set_exit_code(1)
                    else:
                        output_info += "OK: STORAGE POOL {} has {}% of free space left ({} free of {} total pool size is left)\n".format(name, round(free_space_perc, 2), free_space, total_space)

        except Exception as e:
            # Catch an exception and print it
            output_info += str(e) + "\n"
            output_info += "WARNING: There was an error, check the message above. Check also if arguments -W (--warning) or -C (--critical) are set."
            set_exit_code(1)
            return output_info

        return output_info


    def lsalert():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show alarm')
        ssh_lines = ssh_stdout.readlines()[3:]
        output_info = ""
        problem = False

        # return if there are no entries on storage system
        if len(ssh_lines) == 0:
            return "OK: There are no new alerts\n"
        else:
            for line in ssh_lines:
                status = line.split()[1]
                if status in ["Critical", "Major"]: problem = True

            if problem:
                output_info +=  "CRITICAL: There are new alerts:\n"
                for line in ssh_lines:
                    name, status = " ".join(line.split()[4:-2]), line.split()[1]
                    if status == "Critical":
                        output_info += "CRITICAL: Status: {} name: {}\n".format(status, name)
                    elif status == "Major":
                        output_info += "CRITICAL: Status: {} name: {}\n".format(status, name)
                set_exit_code(2)
            else:
                return "OK: There are no new CRITCAL/MAJOR alerts\n"

        return output_info


    def lscontroller():
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show controller general')
        ssh_lines = ssh_stdout.readlines()[2:]
        output_info = ""

        # return if there are no entries on system
        if len(ssh_lines) == 0:
            return "OK: There are no CONTROLLERs defined\n"

        names = ["Controller", "Health", "Running"]
        info = ""
        for line in ssh_lines:
            if len(line) > 10:

                if line.split()[0] in names:
                    newline = line.split(":")
                    info += str(newline[1]) + " "

        for item in range(0, len(info.split()), 3):
            split_line = info.split()[item:item + 3]

            # Assign values
            name, health_status, running_status = split_line[0], split_line[1], split_line[2]

            # Check for errors
            if running_status == "Online":
                output_info += "OK: CONTROLLERs {} health status: {} running status: {}\n".format(name, health_status,
                                                                                                 running_status)
            else:
                output_info += "CRITICAL: CONTROLLERs {} health status: {} running status: {}\n".format(name,
                                                                                                       health_status,
                                                                                                       running_status)

        return output_info


    def lsallstatuses():
        global output_info
        output_info += lslun() + "\n"
        output_info += lsdisk() + "\n"
        output_info += lsdiskdomain() + "\n"
        output_info += lsexpansionmodule() + "\n"
        output_info += lsinitiator() + "\n"
        output_info += lsstoragepool() + "\n"
        output_info += lspsu() + "\n"
        output_info += lsalert() + "\n"
        output_info += lscontroller() + "\n"

        return output_info


    def switcher_function(command):
        """Function returns output information for nagios."""
        switcher = {
            "lslun": lslun,
            "lsdisk": lsdisk,
            "lsdiskdomain": lsdiskdomain,
            "lsexpansionmodule": lsexpansionmodule,
            "lsinitiator": lsinitiator,
            "lsstoragepool": lsstoragepool,
            "lspsu": lspsu,
            "capacitystoragepool": capacitystoragepool,
            "lsalert": lsalert,
            "lscontroller": lscontroller,
            "lsallstatuses": lsallstatuses,
        }

        return switcher.get(command)()

    help_message = ("""Check Huawei Oceanstor through SSH

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
        lsallstatuses - show all checks that starts with ls in one output""")

    useable_commands = [
        'lslun',
        'lsdisk',
        'lsdiskdomain',
        'lsexpansionmodule',
        'lsinitiator',
        'lsstoragepool',
        'lspsu',
        'capacitystoragepool',
        'lsalert',
        'lscontroller',
        'lsallstatuses'
        ]

    parser = argparse.ArgumentParser(description=help_message, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-H', '--hostname',
                        metavar='<HOSTNAME>',
                        required=True)
    parser.add_argument('-u', '--username',
                        metavar='<USERNAME>',
                        required=True)
    parser.add_argument('-k', '--key_filename',
                        metavar='<KEY_FILE_DESTINATION>',
                        required=True)
    parser.add_argument('-c', '--command',
                        metavar='<COMMAND1,COMMAND2,...,COMMANDX>',
                        required=True)
    parser.add_argument('-C', '--critical',
                        metavar='<CRITICAL_PERC>',
                        required=False)
    parser.add_argument('-W', '--warning',
                        metavar='<WARNING_PERC>',
                        required=False)
    parser.add_argument('-sp', '--storagepool',
                        metavar='<SP_NAME>',
                        required=False)

    args = parser.parse_args()

    # Check if command exists if not throw an error
    if not any(command in useable_commands for command in args.command.split(",")):
        parser.error("\n\nUnrecognized command: {0}\n\n\
                     Check -h, --help for useable commands\n".format(args.command))
        sys.exit()

    # Assign parsed arguments to variables
    hostname = args.hostname
    username = args.username
    key_filename = args.key_filename
    commands = args.command

    # Check if variables are set in args
    if args.critical:
        critical = int(args.critical)

    if args.warning:
        warning = int(args.warning)

    if args.storagepool:
        storage_pool_name = args.storagepool

    # SSH to Oceanstor
    ssh = paramiko.SSHClient()
    # Accept the host_key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, key_filename=key_filename)
    except paramiko.SSHException as error:
        print("WARNING: Authentication failed with error: {}".format(error))
        sys.exit(1)

    # Go to main switcher function
    for command in commands.split(','):
        print(switcher_function(command))

    ssh.close()
    sys.exit(exit_code)
