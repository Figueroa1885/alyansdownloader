
import re
import time
from pathlib import Path
from urllib.parse import unquote

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    TaskProgressColumn,
)
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.style import Style
from rich.columns import Columns

console = Console()

CYAN = "cyan"
MAGENTA = "magenta"
GREEN = "green"
YELLOW = "yellow"
RED = "red"
DIM = "dim"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


LOGO = """
[bold magenta]╔══════════════════════════════════════════════════════════════╗[/]
[bold magenta]║[/]            [bold cyan]     _    _                  _       [/]             [bold magenta]║[/]
[bold magenta]║[/]            [bold cyan]    / \\  | |_   _  __ _ _ __ ( )___  [/]             [bold magenta]║[/]
[bold magenta]║[/]            [bold cyan]   / _ \\ | | | | |/ _` | '_ \\|// __| [/]             [bold magenta]║[/]
[bold magenta]║[/]            [bold cyan]  / ___ \\| | |_| | (_| | | | | \\__ \\ [/]             [bold magenta]║[/]
[bold magenta]║[/]            [bold cyan] /_/   \\_\\_|\\__, |\\__,_|_| |_| |___/ [/]             [bold magenta]║[/]
[bold magenta]║[/]            [bold cyan]            |___/                    [/]             [bold magenta]║[/]
[bold magenta]║[/]                   [bold white]FitGirl Downloader[/] [dim]v1.0[/]                    [bold magenta]║[/]
[bold magenta]╠══════════════════════════════════════════════════════════════╣[/]
[bold magenta]║[/]        [dim]Extract and download FitGirl repacks with ease[/]        [bold magenta]║[/]
[bold magenta]╚══════════════════════════════════════════════════════════════╝[/]
"""


def show_welcome():
    """Display welcome banner."""
    console.print()
    console.print(Align.center(LOGO))
    console.print()


def part_number(url: str) -> int:
    """Extract part number from URL for sorting."""
    match = re.search(r"\.part(\d+)\.rar", url, re.IGNORECASE)
    return int(match.group(1)) if match else 10**9


def is_fuckingfast_link(url: str) -> bool:
    """Check if URL is a fuckingfast.co link."""
    lower = url.lower().strip()
    return (
        "://fuckingfast.co/" in lower
        or "://www.fuckingfast.co/" in lower
        or "://sub.fuckingfast.co/" in lower
    )


def is_part_file(url: str) -> bool:
    """Check if URL is a main repack .partXXX.rar file."""
    return bool(re.search(r"_--_fitgirl-repacks\.site_--_\.part\d+\.rar", url, re.IGNORECASE))


def get_filename_from_url(url: str) -> str:
    """Extract filename from URL fragment."""
    if "#" in url:
        return unquote(url.split("#")[-1])
    return f"download_{int(time.time())}.rar"


def get_part_display_name(url: str) -> str:
    """Get a short display name for a part."""
    filename = get_filename_from_url(url)
    match = re.search(r"\.part(\d+)\.rar", filename, re.IGNORECASE)
    if match:
        return f"Part {int(match.group(1)):03d}"
    return filename[:30]


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def extract_links(page_url: str) -> list[str]:
    """Fetch page and extract fuckingfast links."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Fetching page...", total=None)
        
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            console.print(f"\n[red]✗ Error fetching page:[/red] {e}")
            return []

    links = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    links = [link for link in links if is_fuckingfast_link(link) and is_part_file(link)]
    
    seen = set()
    unique_links = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    
    unique_links.sort(key=part_number)
    
    return unique_links


def extract_download_url(html: str) -> str | None:
    """Extract the direct download URL from the page's download() function."""
    pattern = r'window\.open\(["\']+(https://fuckingfast\.co/dl/[^"\']+)["\']+'
    match = re.search(pattern, html)
    return match.group(1) if match else None


def download_file(url: str, dest_path: Path, session: requests.Session, progress: Progress, task_id) -> bool:
    """Download a file with progress display."""
    try:
        with session.get(url, headers=HEADERS, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            total_size = int(resp.headers.get("content-length", 0))
            progress.update(task_id, total=total_size)
            
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))
            
            return True
    except Exception as e:
        console.print(f"  [red]✗ Error:[/red] {e}")
        return False


def download_part(page_url: str, dest_folder: Path, session: requests.Session) -> tuple[bool, str]:
    """Download a single part: fetch page, extract URL, download file."""
    filename = get_filename_from_url(page_url)
    dest_path = dest_folder / filename
    short_name = filename[:45] + "..." if len(filename) > 45 else filename
    
    if dest_path.exists():
        console.print(f"    [yellow]⊘[/] [dim]Skipped (exists):[/] {short_name}")
        return True, filename
    
    console.print(f"    [cyan]↓[/] [dim]Fetching...[/]")
    
    try:
        resp = session.get(page_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        console.print(f"    [red]✗[/] Error: {e}")
        return False, filename
    
    download_url = extract_download_url(resp.text)
    if not download_url:
        console.print("    [red]✗[/] Could not find download URL")
        return False, filename
    
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}[/]"),
        BarColumn(bar_width=30, style="cyan", complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("    Downloading", total=0)
        success = download_file(download_url, dest_path, session, progress, task)
    
    if success:
        size = dest_path.stat().st_size
        console.print(f"    [green]✓[/] [bold]Complete:[/] {short_name} [dim]({format_size(size)})[/]")
    
    return success, filename


def display_parts(links: list[str]):
    """Display all found parts in a table."""
    console.print()
    
    table = Table(
        title="[bold cyan]📦 Found Parts[/]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold white on dark_blue",
        row_styles=["", "dim"],
        padding=(0, 1),
    )
    table.add_column("#", justify="center", style="bold yellow", width=5)
    table.add_column("Part", justify="center", style="cyan", width=12)
    table.add_column("Filename", style="white")
    
    for i, link in enumerate(links, 1):
        filename = get_filename_from_url(link)
        part_name = get_part_display_name(link)
        short_filename = filename[:50] + "..." if len(filename) > 50 else filename
        table.add_row(str(i), part_name, short_filename)
    
    console.print(Align.center(table))
    console.print()
    
    stats = Panel(
        f"[bold cyan]{len(links)}[/] parts ready to download",
        title="[bold]📊 Total[/]",
        border_style="green",
        padding=(0, 2),
    )
    console.print(Align.center(stats))
    console.print()


def parse_selection(selection: str, total: int) -> list[int]:
    """Parse user selection into list of indices (1-based)."""
    indices = set()
    
    for part in selection.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                start = int(start.strip())
                end = int(end.strip())
                indices.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                indices.add(int(part))
            except ValueError:
                continue
    
    return sorted([i for i in indices if 1 <= i <= total])


def main():
    show_welcome()
    
    step1 = Panel(
        "[white]Enter the FitGirl repack page URL[/]",
        title="[bold yellow]📎 Step 1[/]",
        border_style="yellow",
        padding=(0, 2),
    )
    console.print(Align.center(step1))
    page_url = Prompt.ask("[bold cyan]►[/] URL")
    
    if not page_url.strip():
        console.print(Panel("[red]No URL provided. Exiting.[/]", border_style="red"))
        return
    
    console.print()
    links = extract_links(page_url)
    
    if not links:
        console.print(Panel("[yellow]⚠ No download links found on this page.[/]", border_style="yellow"))
        return
    
    console.print(f"[green]✓[/] Extracted [bold cyan]{len(links)}[/] parts successfully!")
    
    display_parts(links)
    
    step2 = Panel(
        "[white]Select which parts to download[/]\n\n"
        "[dim]• Type [bold]all[/bold] to download everything[/]\n"
        "[dim]• Type numbers like [bold]1,3,5[/bold] or [bold]1-10[/bold] or [bold]1-5,8,10-15[/bold][/]",
        title="[bold yellow]🎯 Step 2[/]",
        border_style="yellow",
        padding=(0, 2),
    )
    console.print(Align.center(step2))
    
    selection = Prompt.ask("[bold cyan]►[/] Selection", default="all")
    
    if selection.lower() == "all":
        selected_indices = list(range(1, len(links) + 1))
    else:
        selected_indices = parse_selection(selection, len(links))
    
    if not selected_indices:
        console.print(Panel("[red]✗ No valid parts selected. Exiting.[/]", border_style="red"))
        return
    
    selected_links = [links[i - 1] for i in selected_indices]
    console.print(f"\n[green]✓[/] Selected [bold cyan]{len(selected_links)}[/] parts to download")
    
    console.print()
    step3 = Panel(
        "[white]Where should the files be saved?[/]",
        title="[bold yellow]📁 Step 3[/]",
        border_style="yellow",
        padding=(0, 2),
    )
    console.print(Align.center(step3))
    
    default_folder = "downloads"
    dest_input = Prompt.ask("[bold cyan]►[/] Folder", default=default_folder)
    
    dest_folder = Path(dest_input)
    dest_folder.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/] Saving to: [bold]{dest_folder.absolute()}[/]")
    
    console.print()
    confirm_panel = Panel(
        f"[white]Ready to download [bold cyan]{len(selected_links)}[/] parts[/]\n"
        f"[dim]Destination: {dest_folder.absolute()}[/]",
        title="[bold green]⚡ Confirm[/]",
        border_style="green",
        padding=(0, 2),
    )
    console.print(Align.center(confirm_panel))
    
    if not Confirm.ask("[bold]Start download?[/]"):
        console.print(Panel("[yellow]Download cancelled.[/]", border_style="yellow"))
        return
    
    console.print()
    console.print(Align.center(Panel(
        "[bold white]🚀 Download in Progress[/]",
        border_style="green",
        padding=(0, 4),
    )))
    
    session = requests.Session()
    results = {"success": [], "failed": [], "skipped": []}
    
    for i, link in enumerate(selected_links, 1):
        part_num = selected_indices[i - 1]
        console.print()
        console.print(Align.center(Panel(
            f"[bold white]Part {part_num:03d}[/] [dim]({i}/{len(selected_links)})[/]",
            border_style="blue",
            padding=(0, 2),
        )))
        
        success, filename = download_part(link, dest_folder, session)
        
        if success:
            dest = dest_folder / filename
            if dest.exists() and dest.stat().st_size > 0:
                results["success"].append(filename)
            else:
                results["skipped"].append(filename)
        else:
            results["failed"].append(filename)
        
        if i < len(selected_links):
            time.sleep(1)
    
    console.print()
    
    summary_table = Table(
        title="[bold]📊 Download Summary[/]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(0, 2),
    )
    summary_table.add_column("Status", justify="center", style="bold")
    summary_table.add_column("Count", justify="center")
    
    summary_table.add_row("[green]✓ Downloaded[/]", f"[bold green]{len(results['success'])}[/]")
    summary_table.add_row("[yellow]⊘ Skipped[/]", f"[bold yellow]{len(results['skipped'])}[/]")
    summary_table.add_row("[red]✗ Failed[/]", f"[bold red]{len(results['failed'])}[/]")
    
    console.print(Align.center(summary_table))
    
    console.print()
    console.print(Align.center(Panel(
        f"[dim]Files saved to:[/] [bold cyan]{dest_folder.absolute()}[/]",
        border_style="dim",
    )))
    
    if results["failed"]:
        console.print()
        failed_panel = Panel(
            "\n".join([f"[red]•[/] {f}" for f in results["failed"]]),
            title="[bold red]Failed Parts[/]",
            border_style="red",
        )
        console.print(Align.center(failed_panel))
    
    console.print()
    console.print(Align.center(Panel(
        "[bold magenta]★[/] [bold white]Thank you for using Alyan's FitGirl Downloader![/] [bold magenta]★[/]\n"
        "[dim]Happy gaming! 🎮[/]",
        border_style="magenta",
        padding=(1, 4),
    )))
    console.print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Download interrupted by user.[/yellow]\n")
