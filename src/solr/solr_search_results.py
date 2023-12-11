import requests
import pandas as pd

def search_results(books, query):
    title_str = f'title:"{books[0]}"'
    for i in range(1, len(books)):
        title_str = title_str + ' OR ' + f'title:"{books[i]}"'
    title_str = '(' + title_str + ')'
    query_list = query.split()
    query_str = f'paragraph:"{query_list[0]}*"'
    for i in range(1, len(query_list)): 
        query_str = query_str + ' OR ' + f'paragraph:"{query_list[i]}*"'
    query_str = '(' + query_str + ')'
    solr_url = f'http://34.125.172.59:8983/solr/IRF23P3/select?q={title_str} AND {query_str}&wt=json'

    try:
        response = requests.get(solr_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()['response']['docs']
        results_df = pd.DataFrame(data)
        results_df.drop(columns=['id', '_version_'], inplace=True)
        return results_df
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


