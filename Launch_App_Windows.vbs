' Bank Teller Chatbot - VBS Launcher (Double-click to run)
' Creates a shortcut to easily launch the app

Set objShell = CreateObject("WScript.Shell")
strProjectRoot = objShell.CurrentDirectory
strBatchFile = strProjectRoot & "\run_app.bat"

' Check if batch file exists
If Not objFSO.FileExists(strBatchFile) Then
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    strProjectRoot = objFSO.GetParentFolderName(WScript.ScriptFullName)
    strBatchFile = strProjectRoot & "\run_app.bat"
End If

' Run the batch file
objShell.Run """" & strBatchFile & """", 1, False
WScript.Quit
