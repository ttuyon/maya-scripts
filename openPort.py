import maya.cmds as cmds

WINDOW_NAME = 'sy_OpenPortConfMenu'

def openPortConfMenu():    
    window = cmds.window(WINDOW_NAME, title='Open/Close Maya Port', w=200, h=135, minimizeButton=False, maximizeButton=False, sizeable=False)

    def openPort(*args):
        port = cmds.intField("portInput", query=True, value=True)
        language = cmds.optionMenu("language", query=True, value=True)

        if not port or not language:
            cmds.error("Please input a valid value")
            return

        try:
            cmds.commandPort(name=f"localhost:{port}", sourceType=language.lower(), echoOutput=True)
            print(f"Port {port} opened with {language} support")
            
            cmds.deleteUI(window)

        except Exception as e:
            print(f"Error opening port: {e}")

    def closePort(*args):
        port = cmds.intField("portInput", query=True, value=True)

        if not port:
            cmds.error("Please input a valid value")
            return

        try:
            cmds.commandPort(name=f"localhost:{port}", close=True)
            print(f"Port {port} closed")
            
            cmds.deleteUI(window)

        except Exception as e:
            print(f"Error closing port: {e}")

    layout = cmds.formLayout(WINDOW_NAME + "_layout", numberOfDivisions=100)

    portLabel = cmds.text("portLabel", label="Port", align="left", height=20)
    languageLabel = cmds.text("languageLabel", label="Language", align="left", height=20)

    openBtn = cmds.button(w=150, h=25, label="Open", parent=layout, command=openPort)
    closeBtn = cmds.button(w=150, h=25, label="Close", parent=layout, command=closePort)

    portInput = cmds.intField("portInput", h=20, v=7001)

    languageMenu = cmds.optionMenu("language", h=20)
    cmds.menuItem(label="MEL")
    cmds.menuItem(label="Python")

    cmds.formLayout(layout, edit=True, 
                    attachForm=[(portLabel, 'left', 15), (portLabel, 'top', 15), (portInput, 'right', 15), (portInput, 'top', 15), 
                                (languageLabel, 'left', 15), (languageMenu, 'right', 15),
                                (openBtn, 'left', 5), (openBtn, 'right', 5),
                                (closeBtn, 'left', 5), (closeBtn, 'right', 5)],
                    attachControl=[(languageLabel, 'top', 5, portLabel), (languageMenu, 'top', 5, portInput), (openBtn, 'top', 15, languageLabel), (closeBtn, 'top', 5, openBtn)],
                    attachPosition=[(portInput, 'left', 0, 40), (languageMenu, 'left', 0, 40)])
    
    cmds.showWindow(window)

openPortConfMenu()