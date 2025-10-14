"""
UE5 Editor Toolbar Menu Extension for AI Assistant
Adds a toolbar dropdown with easy access to troubleshooting tools
"""

def register_toolbar_menu():
    """Register AI Assistant menu in UE5 editor toolbar"""
    try:
        import unreal
    except ImportError:
        print("⚠️ Not in UE5 environment - skipping toolbar registration")
        return
    
    try:
        # Get the menu system
        menus = unreal.ToolMenus.get()
        
        # Find or create the main menu bar
        main_menu = menus.find_menu("LevelEditor.MainMenu")
        if not main_menu:
            print("⚠️ Could not find main menu bar")
            return
        
        # Create AI Assistant menu section
        ai_menu = main_menu.add_sub_menu(
            owner=main_menu.menu_name,
            section_name="",
            name="AIAssistant",
            label="AI Assistant"
        )
        
        # Add Launch Troubleshooter menu item
        troubleshooter_entry = unreal.ToolMenuEntry(
            name="LaunchTroubleshooter",
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        troubleshooter_entry.set_label(unreal.Text("🔧 Launch Troubleshooter"))
        troubleshooter_entry.set_tool_tip(unreal.Text("Import troubleshooter tools and show available commands"))
        troubleshooter_entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="import AIAssistant.troubleshooter as ts; ts.help(); print('\\n✅ Troubleshooter loaded! Use ts.reconnect(), ts.status(), ts.info(), ts.dashboard()')"
        )
        ai_menu.add_menu_entry("AIAssistantCommands", troubleshooter_entry)
        
        # Add Restart Assistant menu item
        restart_entry = unreal.ToolMenuEntry(
            name="RestartAssistant",
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        restart_entry.set_label(unreal.Text("🔄 Restart Assistant"))
        restart_entry.set_tool_tip(unreal.Text("Restart the AI Assistant connection (fixes most connection issues)"))
        restart_entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from AIAssistant.auto_update import force_restart_assistant; force_restart_assistant(); print('\\n✅ Assistant restarted! Connection re-established.')"
        )
        ai_menu.add_menu_entry("AIAssistantCommands", restart_entry)
        
        # Add Test Connection menu item
        test_entry = unreal.ToolMenuEntry(
            name="TestConnection",
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        test_entry.set_label(unreal.Text("🔍 Test Connection"))
        test_entry.set_tool_tip(unreal.Text("Run diagnostics to check connection status"))
        test_entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="import AIAssistant.troubleshooter as ts; ts.status(); ts.info(); print('\\n💡 Use ts.reconnect() to fix connection issues')"
        )
        ai_menu.add_menu_entry("AIAssistantCommands", test_entry)
        
        # Add Open Dashboard menu item
        dashboard_entry = unreal.ToolMenuEntry(
            name="OpenDashboard",
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        dashboard_entry.set_label(unreal.Text("🌐 Open Dashboard"))
        dashboard_entry.set_tool_tip(unreal.Text("Open the web dashboard in browser"))
        dashboard_entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="import webbrowser; webbrowser.open('https://ue5-assistant-noahbutcher97.replit.app/dashboard'); print('\\n✅ Dashboard opened in browser!')"
        )
        ai_menu.add_menu_entry("AIAssistantCommands", dashboard_entry)
        
        # Refresh menus to show changes
        menus.refresh_all_widgets()
        
        unreal.log("✅ AI Assistant toolbar menu registered")
        print("✅ AI Assistant menu added to editor toolbar")
        
    except Exception as e:
        print(f"❌ Failed to register toolbar menu: {e}")
        import traceback
        traceback.print_exc()


def unregister_toolbar_menu():
    """Remove AI Assistant menu from toolbar (for cleanup)"""
    try:
        import unreal
        menus = unreal.ToolMenus.get()
        main_menu = menus.find_menu("LevelEditor.MainMenu")
        if main_menu:
            main_menu.remove_sub_menu("AIAssistant")
            menus.refresh_all_widgets()
            print("✅ AI Assistant menu removed from toolbar")
    except Exception as e:
        print(f"❌ Failed to unregister toolbar menu: {e}")
