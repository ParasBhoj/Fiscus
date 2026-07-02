import sys
import asyncio
from db_connector import LocalSQLiteConnector
from embedder import generate_embedding, compute_cosine_similarity
from rich.console import Console

console = Console()

async def search(query: str):
    console.print(f"[bold cyan]Searching database for:[/bold cyan] '{query}'")
    
    # 1. Generate math vector for your search query
    query_vector = await generate_embedding(query)
    if not query_vector:
        console.print("[bold red]Failed to generate embedding for query.[/bold red]")
        return

    # 2. Fetch all updates from the database
    db = LocalSQLiteConnector()
    updates = db.get_updates(limit=1000)
    
    # 3. Calculate similarity score for each document
    scored_updates = []
    for u in updates:
        vec_bytes = u.get("embedding")
        if vec_bytes:
            score = compute_cosine_similarity(query_vector, vec_bytes)
            u["score"] = score
            scored_updates.append(u)
            
    # 4. Sort by highest score first
    scored_updates.sort(key=lambda x: x["score"], reverse=True)
    
    # 5. Display top 3 results
    console.print("\n[bold green]Top 3 Results:[/bold green]\n")
    for i, item in enumerate(scored_updates[:3], 1):
        console.print(f"[bold white]{i}. {item['title']}[/bold white] (Score: {item['score']:.3f})")
        console.print(f"[dim]Source: {item['source']} | Impact: {item['regulatory_impact']}[/dim]")
        console.print(f"[italic]{item['summary']}[/italic]")
        console.print(f"[blue]{item['url']}[/blue]\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[bold red]Usage: python search_cli.py \"your search query\"[/bold red]")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    asyncio.run(search(query))
