import subprocess, os, shutil, glob
from datetime import datetime, timedelta

''' 
Runs on the task scheduler daily.

Needs 7-Zip to run, installed location should be noted as below.

A full backup is the WTF and Interface folders.
A daily snapshot is just the WTF folder (your settings).
Daily archive of combat log.

If you place this file directly in the WoW directory, you should set the "backupLocation"
so that the zipped up files don't clutter the rest of your WoW install.

'''

# Setup
prog7Zip = 'C:\\program files\\7-Zip\\7z.exe'
backupLocation = ''
snapshotLocation = 'WTFSnapshots'
uiLocation = 'UI'
logLocation = 'Logs' # the folder in the Backups folder that 
fullBackupDate = 'Saturday' # Day of the week to take a full backup
snapshotDaysKept = 14
logDaysKept = 90
uiDaysKept = 0


# Common
currentTS = datetime.now().strftime('%Y%m%d-%H%M%S')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
wowDir = os.getcwd() #this assumes the scripts are in a folder inside the WoW directory
CREATE_NO_WINDOW = 0x08000000
currentDay = datetime.now().strftime('%A')

# If you put this file down one directory it will look up one level for WoW.
if not os.path.isfile(os.path.join(wowDir, 'WoW.exe')):
    print('Wow.exe not found. Checking up one directory.')
    wowDir = os.path.dirname(os.getcwd())

# Still not in the WoW directory? Guess I'll die then...
if not os.path.isfile(os.path.join(wowDir, 'WoW.exe')):
    print('WoW.exe not found. Exiting.')
    exit()

backupLocation = os.path.join(os.getcwd(), backupLocation)
snapshotLocation = os.path.join(backupLocation, snapshotLocation)
uiLocation = os.path.join(backupLocation, uiLocation)
logLocation = os.path.join(backupLocation, logLocation)

# File Names 
snapshotFile = os.path.join(os.getcwd(), backupLocation, snapshotLocation, 'snapshot-' + currentTS + '.7z')
uiFile = os.path.join(os.getcwd(), backupLocation, uiLocation, 'ui-' + currentTS + '7z')
logFile = os.path.join(os.getcwd(), backupLocation, logLocation, 'log-' + currentTS + '.7z')
combatLogFile = os.path.join(wowDir, 'Logs', 'WoWCombatLog.txt')
combatLogTemp = os.path.join(wowDir, 'Logs', 'WoWCombatLog-tmp.txt')

def Backup(outFile, *inFiles):
    inFiles = [ os.path.join(wowDir, f) for f in inFiles ]
    cmd = [prog7Zip, 'a', outFile] + inFiles 
    subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)

def Cleanup(location, olderThanDays):

    for file in glob.glob(os.path.join(os.getcwd(), location,  '*.7z')):
        fileName = os.path.split(file)[1]
        pastFileToRemove = (datetime.now() - timedelta(days=olderThanDays)).strftime('%Y%m%d')
        
        if os.path.isfile(file) and pastFileToRemove in fileName:
            os.remove(file)
 

if __name__ == '__main__':

    if not os.path.isfile(prog7Zip):
        print('7-Zip not found.')
        exit()

    # create folders if they don't exist
    if not os.path.isdir(backupLocation):
        os.mkdir(backupLocation)
    if not os.path.isdir(snapshotLocation):
        os.mkdir(snapshotLocation)
    if not os.path.isdir(uiLocation):
        os.mkdir(uiLocation)
    if not os.path.isdir(logLocation):
        os.mkdir(logLocation)
    
    if fullBackupDate.lower() == currentDay.lower():
        Backup(uiFile, 'WTF', 'Interface')
        if uiDaysKept > 0:
            Cleanup(uiLocation, uiDaysKept)
    else:
        Backup(snapshotFile, 'WTF')
        if snapshotDaysKept > 0:
            Cleanup(snapshotLocation, snapshotDaysKept)
    
    if os.path.isfile(combatLogFile):
        shutil.copy(combatLogFile, combatLogTemp)
        Backup(logFile, combatLogTemp)
        if logDaysKept > 0:
            Cleanup(logLocation, logDaysKept)

        try:
            os.remove(combatLogFile)
        except:
            pass