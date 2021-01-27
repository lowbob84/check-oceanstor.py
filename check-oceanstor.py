import paramiko
import sys, argparse
import re
from argparse import RawTextHelpFormatter

if __name__ == "__main__":

    # Exit code for nagios 0 -OK, 1 - Warning, 2 - Critical
    exit_code = 0
    output_info = ""
    # OceanStor failed Health and Running status
    failed_health_status = ["Offline", "Pre-fail", "Fault", "No Input", "--"]
    failed_running_status = ["Offline", "Reconstruction", "Balancing", "--"]

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
        if not any( line.split()[4] in failed_health_status for line in ssh_lines ):
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
        if not any( line.split()[1] in failed_health_status for line in ssh_lines ):
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
        if not any( line.split()[2] in failed_health_status for line in ssh_lines ):
            output_info += "OK: All DISK DOMAINs Online \n"
        else:
            output_info += "CRITICAL: check your DISK DOMAIN status \n"
            set_exit_code(2)

        # Check if there are any critical DISK DOMAINs by Running status
        if any( line.split()[3] in failed_running_status for line in ssh_lines ):
            
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
        if not any( line.split()[1] in failed_health_status for line in ssh_lines ):
            output_info += "OK: All EXPANSION MODULEs Online \n"
        else:
            output_info += "CRITICAL: check your EXPANSION MODULEs status \n"
            set_exit_code(2)

        # Check if there are any critical EXPANSION MODULEs by Running status
        if any( line.split()[2] in failed_running_status for line in ssh_lines ):

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
        if not any( line.split()[1] == "Offline" for line in ssh_lines ):
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
        if not any( line.split()[3] in failed_health_status for line in ssh_lines ):
            output_info += "OK: All STORAGE POOLs Online \n"
        else:
            output_info += "CRITICAL: Check your STORAGE POOL status \n"
            set_exit_code(2)

        # Check if there are any critical STORAGE POOLs by Running status
        if any( line.split()[4] in failed_running_status for line in ssh_lines ):
            
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

        # Check if there are any critical STORAGE POOLs
        if not any( [x for x in re.split("\s{2,}",line) if x][2] in failed_running_status for line in ssh_lines ):
            output_info += "OK: All PSU Online \n"
        else:
            output_info += "CRITICAL: Check your PSU status \n"
            set_exit_code(2)

        for line in ssh_lines:
            # split string per double spaces because of status "No Input" at 2nd column
            split_line = [x for x in re.split("\s{2,}",line) if x]

            # Assign values
            name, health_status, running_status = split_line[0], split_line[1], split_line[2]

            # Check for errors
            if running_status == "Online":
                output_info += "OK: PSU {} health status: {} running status: {}\n".format(name, health_status, running_status)
            else:
                output_info += "CRITICAL: PSU {} health status: {} running status: {}\n".format(name, health_status, running_status)

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
        lsallstatuses - show all above in one check""")
    
    useable_commands = [
        'lslun', 
        'lsdisk', 
        'lsdiskdomain', 
        'lsexpansionmodule', 
        'lsinitiator', 
        'lsstoragepool', 
        'lspsu',
        'lsallstatuses'
        ]

    parser = argparse.ArgumentParser(description=help_message, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-H', '--hostname', metavar='<HOSTNAME>', required=True)
    parser.add_argument('-u', '--username', metavar='<USERNAME>', required=True)
    parser.add_argument('-k', '--key_filename', metavar='<KEY_FILE_DESTINATION>', required=True)
    parser.add_argument('-c', '--command', metavar='<COMMAND1,COMMAND2,...,COMMANDX>', required=True)

    args = parser.parse_args()

    # Check if command exists if not throw an error
    if not any( command in useable_commands for command in args.command.split(",") ):
        parser.error("\n\nUnrecognized command: {0}\n\nCheck -h, --help for useable commands\n".format(args.command ) )
        sys.exit()
    
    # Assign parsed arguments to variables
    hostname = args.hostname
    username = args.username
    key_filename = args.key_filename
    commands = args.command

    # SSH to Oceanstor
    ssh = paramiko.SSHClient()
    # Accept the host_key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect( hostname, username=username, key_filename=key_filename )
    except:
        error = sys.exc_info()
        print("WARNING: Authentication failed with error: {}".format( error ))
        sys.exit(1)

    # Go to main switcher function
    for command in commands.split(','):
        print(switcher_function(command))

    ssh.close()
    sys.exit(exit_code)
