#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
#SingleInstance force
#Persistent ;Script nicht beenden nach der Auto-Execution-Section

SetWorkingDir %A_ScriptDir%
CoordMode, Mouse, Screen


Menu, tray, NoStandard
Menu, tray, add  ; Creates a separator line.
Menu, tray, add, Reload  
Menu, tray, add, Exit
Menu, Tray, Icon, icon.ico
return

!+r::  ; Press F1 to execute
	MouseGetPos, xpos, ypos  ; Get mouse position

	; Calculate centered position

	CenterX := xpos - 100  ; 100 is half the width of the GUI
	CenterY := ypos - 25  ; 25 is half the height of the GUI

	Gui, +hWndhWndIdiom +Owner -SysMenu -Caption +AlwaysOnTop
	Gui,Color, feffff 
	Gui, Add, Edit, w200 h20 vUserInput
	Gui, Show, x%CenterX% y%CenterY% w200 h50, keepass-data-retriever  ; Show centered GUI
	WinSet, TransColor, feffff,  ahk_id %hWndIdiom%
return

#IfWinActive, keepass-data-retriever  ; Make the hotkeys local to the GUI

Enter::
	Gui, Submit  ; Save the input to the UserInput variable
	RunWait, % "python main.py " UserInput,, hide  ; Replace 'main.py' with your Python script
	Gui, Destroy  ; Destroy the GUI
return

Esc::
	Gui, Destroy  ; Destroy the GUI when closed
return

#IfWinActive  ; End of local hotkeys

GuiClose:
	Gui, Destroy  ; Destroy the GUI when closed
return

Reload:
	Reload
return 

Exit:
	ExitApp
return
