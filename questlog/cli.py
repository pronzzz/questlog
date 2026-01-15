import typer
from rich.console import Console
from rich import print

app = typer.Typer(help="QuestLog: Generate infinite, trackable skill trees in Markdown.")
console = Console()

@app.command()
def new(
    topic: str = typer.Argument(..., help="The topic you want to learn (e.g., 'Docker for Data Science')"),
    difficulty: str = typer.Option("intermediate", help="Difficulty level: novice, adept, master"),
    language: str = typer.Option("en", help="Output language: en, es, fr"),
):
    """
    Generate a new QuestLog roadmap for a specific topic.
    """
    from questlog.core import configure_gemini, generate_roadmap_data, render_markdown, process_roadmap
    
    ascii_art = r"""
   ___                 _   _             
  / _ \ _   _  ___ ___| |_| | ___   __ _ 
 | | | | | | |/ _ \ __| __| |/ _ \ / _` |
 | |_| | |_| |  __\__ \ |_| | (_) | (_| |
  \__\_\\__,_|\___|___/\__|_|\___/ \__, |
                                   |___/ 
    """
    console.print(f"[bold purple]{ascii_art}[/bold purple]")
    console.print(f"[bold green]Generating QuestLog for:[/bold green] {topic} ({difficulty})")
    
    try:
        configure_gemini()
        
        with console.status("[bold green]Consulting the Senior Staff Engineer (Gemini)...[/bold green]") as status:
            data = generate_roadmap_data(topic, difficulty, language)
            
            status.update("[bold yellow]Validating resource links... (checking for link rot)[/bold yellow]")
            data = process_roadmap(data)
            
        console.print("[dim]Data received and validated. Rendering roadmap...[/dim]")
        markdown_content = render_markdown(data)
        
        filename = f"Quest-{topic.replace(' ', '-')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        console.print(f"[bold blue]Success! Roadmap saved to {filename}[/bold blue]")
        console.print(f"Run [bold]code {filename}[/bold] (or your editor) to view it.")
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
    
@app.command()
def status():
    """
    Check progress of existing roadmaps in the current directory.
    """
    print("[yellow]Status command not yet implemented.[/yellow]")

if __name__ == "__main__":
    app()
