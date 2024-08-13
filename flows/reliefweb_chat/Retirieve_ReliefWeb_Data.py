import datetime
import json
import requests
from bs4 import BeautifulSoup
from langchain import LLMChain, Tool

# ReliefWeb API Base URL
RELIEFWEB_API_URL = "https://api.reliefweb.int/v1"

def convert_to_iso8601(date_str):
    """Convert a date string to ISO 8601 format with timezone offset."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        iso8601_date = date_obj.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        return iso8601_date
    except ValueError:
        return date_str

def get_rweb_data(query: dict, endpoint: str) -> list:
    """Retrieve ReliefWeb data based on the provided query and endpoint."""
    url = f"{RELIEFWEB_API_URL}/{endpoint}"
    print(f"Getting {url} \n\n {query} ...")
    response = requests.post(url, json=query)
    
    if response.status_code == 200:
        answer = response.json()
    else:
        print("Error: No data was returned for keyword")
        query = str(query).replace("'", '"')
        return f"No data was returned for query: {query}"

    results = []
    for article in answer["data"]:
        article_url = article["fields"]["url"]
        article_response = requests.get(article_url)
        soup = BeautifulSoup(article_response.text, "html.parser")
        web_content = [p.text for p in soup.find_all("p")]
        article["fields"]["endpoint"] = endpoint
        article["fields"]["body"] = web_content
        results.append(article["fields"])
    
    print(f"REPORT SIZE {len(results)}")
    report_components = json.dumps(results, indent=4)
    return report_components

def get_rweb_reports_and_news_data(
    keyword: str = "",
    date_from: str = None,
    date_to: str = None,
    disaster_id: str = None,
    sort: str = None,
    limit: int = 5,
    offset: int = 0,
    format_name: str = None,
) -> str:
    """Retrieve reports and news data from ReliefWeb API."""
    endpoint = "reports"
    filter_conditions = []

    if date_from is not None and date_to is not None:
        date_from = convert_to_iso8601(date_from)
        date_to = convert_to_iso8601(date_to)
        filter_conditions.append(
            {"field": "date.created", "value": {"from": date_from, "to": date_to}}
        )

    if disaster_id is not None:
        filter_conditions.append({"field": "disaster.id", "value": disaster_id})
    
    if format_name is not None:
        filter_conditions.append({"field": "format.name", "value": format_name})
    
    filter = {"conditions": filter_conditions}
    
    fields = {
        "include": [
            "title",
            "body",
            "url",
            "source",
            "date",
            "format",
            "status",
            "primary_country",
            "id",
        ]
    }

    query = {
        "appname": "myapp",
        "query": {"value": keyword, "operator": "AND"},
        "filter": filter,
        "limit": limit,
        "offset": offset,
        "fields": fields,
        "preset": "latest",
        "profile": "list",
    }
    
    if sort is not None:
        query["sort"] = [sort]

    print(json.dumps(query, indent=4))
    return get_rweb_data(query, endpoint)

def get_rweb_disasters_data(
    keyword: str = "",
    date_from: str = None,
    date_to: str = None,
    sort: str = None,
    limit: int = 20,
    offset: int = 0,
    status: str = None,
    country: str = None,
    id: str = None,
    disaster_type: str = None,
    detailed_query: bool = False,
) -> str:
    """Retrieve disaster data from ReliefWeb API."""
    endpoint = "disasters"
    filter_conditions = []

    if date_from is not None and date_to is not None:
        date_from = convert_to_iso8601(date_from)
        date_to = convert_to_iso8601(date_to)
        filter_conditions.append(
            {"field": "date.event", "value": {"from": date_from, "to": date_to}}
        )

    if status is not None:
        filter_conditions.append({"field": "status", "value": status})
    
    if country is not None:
        filter_conditions.append({"field": "country.name", "value": country})
    
    if disaster_type is not None:
        filter_conditions.append({"field": "type.name", "value": disaster_type})
    
    if id is not None:
        filter_conditions.append({"field": "id", "value": id})

    filter = {"operator": "AND", "conditions": filter_conditions}

    fields = ["name", "date", "url", "id", "status", "glide", "country"]
    
    if detailed_query:
        fields.append("description")

    fields = {"include": fields}

    query = {
        "appname": "myapp",
        "query": {"value": keyword},
        "filter": filter,
        "limit": limit,
        "offset": offset,
        "fields": fields,
    }
    
    if sort is not None:
        query["sort"] = [sort]

    return get_rweb_data(query, endpoint)

# Define a Tool using LangChain to wrap the `get_rweb_reports_and_news_data` function
get_rweb_reports_and_news_data_tool = Tool.from_function(
    func=get_rweb_reports_and_news_data,
    name="Get ReliefWeb Reports and News Data",
    description="Retrieve reports and news data from ReliefWeb API based on specified parameters.",
    args_schema={
        "keyword": (str, "Keyword to search for in the reports and news data."),
        "date_from": (str, "Start date for the search in ISO 8601 format.", None),
        "date_to": (str, "End date for the search in ISO 8601 format.", None),
        "disaster_id": (str, "ID of the disaster to filter results.", None),
        "sort": (str, "Sort order for the results.", None),
        "limit": (int, "Maximum number of results to retrieve.", 5),
        "offset": (int, "Offset for pagination.", 0),
        "format_name": (str, "Format name to filter results.", None),
    },
)

# Example usage of the Tool
if __name__ == "__main__":
    result = get_rweb_reports_and_news_data_tool.run(
        keyword="earthquake",
        date_from="2023-01-01",
        date_to="2023-12-31",
        sort="date:desc",
        limit=2,
        offset=0,
    )
    print(result)
