"""
AI Agent API Client - Terminal User Interface (TUI)

An interactive terminal interface for the AI Agent API using Textual.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Input, Label, DataTable, TabbedContent, TabPane, Log
from textual.screen import Screen
from textual import on
from textual.binding import Binding

# Import the API client from the main client module
sys.path.insert(0, str(Path(__file__).parent))
from client import APIClient, API_BASE_URL, API_TIMEOUT

# Constants
MESSAGE_PREVIEW_LENGTH = 500  # Max characters to show in message preview


class ProjectListScreen(Screen):
    """Screen for listing and selecting projects."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("n", "new_project", "New Project"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, client: APIClient):
        super().__init__()
        self.client = client
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📁 Projects", classes="title"),
            Static("Select a project or create a new one", classes="subtitle"),
            DataTable(id="projects_table"),
            Horizontal(
                Button("New Project", variant="primary", id="btn_new"),
                Button("Refresh", variant="default", id="btn_refresh"),
                Button("Back", variant="default", id="btn_back"),
                classes="button_row"
            ),
            classes="project_list_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Set up the projects table."""
        table = self.query_one("#projects_table", DataTable)
        table.add_columns("Key", "Name", "Created")
        table.cursor_type = "row"
        self.load_projects()
    
    def load_projects(self) -> None:
        """Load projects from API."""
        table = self.query_one("#projects_table", DataTable)
        table.clear()
        
        try:
            projects = self.client.list_projects()
            for project in projects:
                created = project.get("created_at", "Unknown")
                if created and created != "Unknown":
                    # Format datetime if possible
                    try:
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        created = dt.strftime("%Y-%m-%d %H:%M")
                    except (ValueError, TypeError, AttributeError):
                        # Keep original value if parsing fails
                        pass
                table.add_row(
                    project["key"],
                    project["name"],
                    created
                )
        except Exception as e:
            self.notify(f"Error loading projects: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#btn_new")
    def action_new_project(self) -> None:
        """Create a new project."""
        self.app.push_screen(CreateProjectScreen(self.client))
    
    @on(Button.Pressed, "#btn_refresh")
    def action_refresh(self) -> None:
        """Refresh the project list."""
        self.load_projects()
        self.notify("Projects refreshed")
    
    @on(Button.Pressed, "#btn_back")
    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle project selection."""
        table = self.query_one("#projects_table", DataTable)
        row = table.get_row_at(event.cursor_row)
        project_key = str(row[0])
        self.app.push_screen(ProjectDetailScreen(self.client, project_key))


class CreateProjectScreen(Screen):
    """Screen for creating a new project."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]
    
    def __init__(self, client: APIClient):
        super().__init__()
        self.client = client
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("➕ Create New Project", classes="title"),
            Label("Project Key:"),
            Input(placeholder="e.g., PROJ001", id="input_key"),
            Label("Project Name:"),
            Input(placeholder="e.g., My Project", id="input_name"),
            Horizontal(
                Button("Create", variant="primary", id="btn_create"),
                Button("Cancel", variant="default", id="btn_cancel"),
                classes="button_row"
            ),
            classes="form_container"
        )
        yield Footer()
    
    @on(Button.Pressed, "#btn_create")
    def action_create(self) -> None:
        """Create the project."""
        key_input = self.query_one("#input_key", Input)
        name_input = self.query_one("#input_name", Input)
        
        key = key_input.value.strip()
        name = name_input.value.strip()
        
        if not key or not name:
            self.notify("Please fill in all fields", severity="warning")
            return
        
        try:
            self.client.create_project(key, name)
            self.notify(f"Project '{key}' created successfully!", severity="information")
            self.app.pop_screen()
        except SystemExit:
            # Error was already displayed by the client
            pass
    
    @on(Button.Pressed, "#btn_cancel")
    def action_cancel(self) -> None:
        """Cancel project creation."""
        self.app.pop_screen()


class ProjectDetailScreen(Screen):
    """Screen for viewing project details and running commands."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]
    
    def __init__(self, client: APIClient, project_key: str):
        super().__init__()
        self.client = client
        self.project_key = project_key
        self.project_info = None
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"📊 Project: {self.project_key}", classes="title"),
            TabbedContent(
                TabPane("Info", id="tab_info"),
                TabPane("Commands", id="tab_commands"),
                TabPane("Artifacts", id="tab_artifacts"),
            ),
            Horizontal(
                Button("Back", variant="default", id="btn_back"),
                classes="button_row"
            ),
            classes="project_detail_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load project data."""
        self.load_project_info()
        self.setup_commands_tab()
        self.load_artifacts()
    
    def load_project_info(self) -> None:
        """Load project information."""
        try:
            state = self.client.get_project_state(self.project_key)
            self.project_info = state.get("project_info", {})
            
            # Update info tab
            info_tab = self.query_one("#tab_info", TabPane)
            info_tab.mount(
                Static(f"Name: {self.project_info.get('name', 'N/A')}"),
                Static(f"Key: {self.project_info.get('key', 'N/A')}"),
                Static(f"Methodology: {self.project_info.get('methodology', 'N/A')}"),
                Static(f"Created: {self.project_info.get('created_at', 'N/A')}"),
                Static(f"Updated: {self.project_info.get('updated_at', 'N/A')}"),
            )
        except Exception as e:
            self.notify(f"Error loading project: {str(e)}", severity="error")
    
    def setup_commands_tab(self) -> None:
        """Setup the commands tab."""
        commands_tab = self.query_one("#tab_commands", TabPane)
        commands_tab.mount(
            Static("Select a command to run:", classes="subtitle"),
            Vertical(
                Button("🔍 Assess Gaps", id="cmd_assess_gaps", classes="command_button"),
                Button("📝 Generate Artifact", id="cmd_generate_artifact", classes="command_button"),
                Button("📅 Generate Plan", id="cmd_generate_plan", classes="command_button"),
                classes="command_list"
            )
        )
    
    def load_artifacts(self) -> None:
        """Load project artifacts."""
        try:
            artifacts = self.client.list_artifacts(self.project_key)
            artifacts_tab = self.query_one("#tab_artifacts", TabPane)
            
            if not artifacts:
                artifacts_tab.mount(Static("No artifacts yet. Run a command to generate artifacts."))
            else:
                table = DataTable()
                table.add_columns("Path", "Type")
                for artifact in artifacts:
                    table.add_row(artifact.get("path", ""), artifact.get("type", ""))
                artifacts_tab.mount(table)
        except Exception as e:
            self.notify(f"Error loading artifacts: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#btn_back")
    def action_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#cmd_assess_gaps")
    def run_assess_gaps(self) -> None:
        """Run assess_gaps command."""
        self.app.push_screen(RunCommandScreen(self.client, self.project_key, "assess_gaps"))
    
    @on(Button.Pressed, "#cmd_generate_artifact")
    def run_generate_artifact(self) -> None:
        """Run generate_artifact command."""
        self.notify("Generate Artifact feature coming soon!", severity="information")
    
    @on(Button.Pressed, "#cmd_generate_plan")
    def run_generate_plan(self) -> None:
        """Run generate_plan command."""
        self.app.push_screen(RunCommandScreen(self.client, self.project_key, "generate_plan"))


class RunCommandScreen(Screen):
    """Screen for running a command with propose/apply workflow."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]
    
    def __init__(self, client: APIClient, project_key: str, command: str):
        super().__init__()
        self.client = client
        self.project_key = project_key
        self.command = command
        self.proposal = None
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"⚙️ Run Command: {self.command}", classes="title"),
            Static(f"Project: {self.project_key}", classes="subtitle"),
            Log(id="command_log", auto_scroll=True),
            Horizontal(
                Button("Propose", variant="primary", id="btn_propose"),
                Button("Apply", variant="success", id="btn_apply", disabled=True),
                Button("Cancel", variant="default", id="btn_cancel"),
                classes="button_row"
            ),
            classes="command_container"
        )
        yield Footer()
    
    @on(Button.Pressed, "#btn_propose")
    def action_propose(self) -> None:
        """Propose the command."""
        log = self.query_one("#command_log", Log)
        log.write_line(f"[bold cyan]Proposing {self.command}...[/bold cyan]")
        
        try:
            self.proposal = self.client.propose_command(self.project_key, self.command)
            
            log.write_line(f"[green]✓ Proposal generated![/green]")
            log.write_line(f"Proposal ID: {self.proposal['proposal_id']}")
            log.write_line(f"\nAssistant Message:")
            log.write_line(self.proposal['assistant_message'][:MESSAGE_PREVIEW_LENGTH])
            
            log.write_line(f"\nFile Changes ({len(self.proposal['file_changes'])}):")
            for change in self.proposal['file_changes']:
                log.write_line(f"  {change['operation'].upper()}: {change['path']}")
            
            # Enable apply button
            apply_btn = self.query_one("#btn_apply", Button)
            apply_btn.disabled = False
            
            self.notify("Proposal ready! Review and click Apply to commit.", severity="information")
            
        except SystemExit:
            log.write_line("[red]✗ Failed to generate proposal[/red]")
    
    @on(Button.Pressed, "#btn_apply")
    def action_apply(self) -> None:
        """Apply the proposal."""
        if not self.proposal:
            self.notify("No proposal to apply", severity="warning")
            return
        
        log = self.query_one("#command_log", Log)
        log.write_line(f"\n[bold cyan]Applying proposal...[/bold cyan]")
        
        try:
            result = self.client.apply_command(self.project_key, self.proposal['proposal_id'])
            
            log.write_line(f"[green]✓ Changes committed![/green]")
            log.write_line(f"Commit Hash: {result['commit_hash']}")
            log.write_line(f"Message: {result['message']}")
            
            self.notify("Command completed successfully!", severity="information")
            
            # Disable apply button
            apply_btn = self.query_one("#btn_apply", Button)
            apply_btn.disabled = True
            
        except SystemExit:
            log.write_line("[red]✗ Failed to apply proposal[/red]")
    
    @on(Button.Pressed, "#btn_cancel")
    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()


class MainMenuScreen(Screen):
    """Main menu screen."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🤖 AI Agent API Client", classes="title"),
            Static("Terminal User Interface", classes="subtitle"),
            Vertical(
                Button("📁 Projects", variant="primary", id="btn_projects"),
                Button("❤️ Health Check", variant="default", id="btn_health"),
                Button("❌ Exit", variant="error", id="btn_exit"),
                classes="menu_buttons"
            ),
            classes="main_menu_container"
        )
        yield Footer()
    
    @on(Button.Pressed, "#btn_projects")
    def show_projects(self) -> None:
        """Show projects screen."""
        self.app.push_screen(ProjectListScreen(self.app.client))
    
    @on(Button.Pressed, "#btn_health")
    def check_health(self) -> None:
        """Check API health."""
        try:
            health = self.app.client.health_check()
            self.notify(f"API Status: {health.get('status', 'unknown')}", severity="information")
        except Exception as e:
            self.notify(f"Health check failed: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#btn_exit")
    def exit_app(self) -> None:
        """Exit the application."""
        self.app.exit()


class AIAgentTUI(App):
    """AI Agent API Client TUI Application."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    .title {
        text-style: bold;
        color: $accent;
        text-align: center;
        padding: 1;
    }
    
    .subtitle {
        color: $text-muted;
        text-align: center;
        padding-bottom: 1;
    }
    
    .main_menu_container {
        align: center middle;
        width: 60;
    }
    
    .menu_buttons {
        align: center middle;
        padding: 2;
    }
    
    .menu_buttons Button {
        width: 40;
        margin: 1;
    }
    
    .project_list_container {
        padding: 1;
    }
    
    .form_container {
        align: center middle;
        width: 60;
        padding: 2;
    }
    
    .form_container Label {
        margin-top: 1;
        margin-bottom: 0;
    }
    
    .form_container Input {
        margin-bottom: 1;
    }
    
    .button_row {
        align: center middle;
        padding: 1;
    }
    
    .button_row Button {
        margin: 0 1;
    }
    
    .project_detail_container {
        padding: 1;
    }
    
    .command_list {
        padding: 1;
    }
    
    .command_button {
        width: 100%;
        margin: 1 0;
    }
    
    .command_container {
        padding: 1;
    }
    
    #command_log {
        height: 20;
        border: solid $primary;
        margin: 1 0;
    }
    
    DataTable {
        height: auto;
        margin: 1 0;
    }
    """
    
    TITLE = "AI Agent API Client"
    SUB_TITLE = "Terminal User Interface"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
    ]
    
    def __init__(self):
        super().__init__()
        self.client = APIClient(API_BASE_URL, API_TIMEOUT)
    
    def on_mount(self) -> None:
        """Show main menu on mount."""
        self.push_screen(MainMenuScreen())
    
    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def run_tui():
    """Run the TUI application."""
    app = AIAgentTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
