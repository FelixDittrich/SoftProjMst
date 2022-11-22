import os
import json
import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime
from googleapiclient.discovery import build, HttpError
from dotenv import load_dotenv

console = Console()
app = typer.Typer()

def configure():
    load_dotenv()

def googleSearch(q, dateRestrict, exactTerms, excludeTerms, linkSite, num):
    with build("customsearch", "v1", developerKey=os.getenv("API_KEY")) as service:
        collection = service.cse()
        request = collection.list(q=q, dateRestrict=dateRestrict, exactTerms=exactTerms, excludeTerms=excludeTerms, linkSite=linkSite, num=num, cx=os.getenv("CSE_ID"))
        try:
            response = request.execute()
            saveResponse(response, q)
        except HttpError as e:
            print("Error response status code : {0}, reason : {1}".format(e.status_code, e.error_details))
        return response

def saveResponse(data, q):
    filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    filename += "_" + q + ".json"
    with open("./results/" + filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.command()
def search(
    q:str=typer.Argument(
        ...,
        help=
            """
            Search Query.
            """,
        show_default=False),
    dateRestrict:str=typer.Option(
        None, 
        help=
            """
            Restrict results to URLs based od date. Supported values include:\n
            [bold]d[number][/bold]: requests results from the specified number of past days.\n
            w[number]: requests results from the specified number of past weeks.\n
            m[number]: requests results from the specified number of past months.\n
            y[number]: requests results from the specified number of past years.\n
            """, 
        show_default=False),
    exactTerms:str=typer.Option(
        None,
        help=
            """
            Identifies a phrase that all documents in the search results must contain.
            """,
        show_default=False),
    excludeTerms:str=typer.Option(
        None,
        help=
            """
            Identifies a word or phrase that should not appear in any documents in the search results.
            """,
        show_default=False),
    linkSite:str=typer.Option(
        None,
        help=
            """
            Specifies that all search results should contain a link to a particular URL.
            """,
        show_default=False),
    num:int=typer.Option(
        None,
        help=
            """
            Number of search results to return. Valid values are integers between 1 and 10, inclusive.
            """,
        show_default=False),
):
    response = googleSearch(q, dateRestrict, exactTerms, excludeTerms, linkSite, num)

    # f = open("data.json")
    # response = json.load(f)

    table = Table()
    table.add_column("Index", style="cyan", no_wrap=True)
    table.add_column("Result", style="yellow")
    table.add_column("Link")

    for index, value in enumerate(response["items"]):
        table.add_row(str(index+1), "[u][i][b]" + value["title"] + "[/b][/i][/u]" + "\n" + value["snippet"], value["link"])
    
    console.print(table)


if __name__ == "__main__":
    configure()
    app()
