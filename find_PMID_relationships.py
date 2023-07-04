import re
import requests
import xml.etree.ElementTree as ET


#Accept either a PMID or pubmed URL to retrieve the PMID
def get_PMID(link):
    regex_link_pattern = r'^https://pubmed.ncbi.nlm.nih.gov/.*?(\d+)$'
    
    if link.isdigit():
        return link
    
    if not link.startswith("https://pubmed.ncbi.nlm.nih.gov/"):
        print("Invalid link. Please try again.")
        return None
    
    match = re.match(regex_link_pattern, link)
    
    if match:
        article_number = match.group(1)
        return article_number
    else:
        print("Invalid link, please try again")



#use the pubmed API to request the related  PMIDS

def get_related_articles(article_id):
    related_articles = {}
    related_articles[article_id] = []

    #

    pubmed_api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
    params = {
        "dbfrom": "pubmed",
        "id": article_id,
        "cmd": "neighbor",
        "linkname": "pubmed_pubmed"
    }

    response = requests.get(pubmed_api_url, params=params)

    if response.status_code == 200:
        xml_data = response.text

        # Parse the XML response to get all the PMID
        root = ET.fromstring(xml_data)

        # Extract the related article IDs
        for link in root.findall(".//LinkSetDb/Link/Id"):
            related_id = link.text
            related_articles[article_id].append(related_id)
    else:
        print("Failed to retrieve related articles.")

    print(f"Related Articles for {article_id}: {related_articles[article_id]}")

    return related_articles

def get_all_article_relationships(initial_article_id):
    article_relationships = {}


    article_relationships[initial_article_id] = get_related_articles(initial_article_id)

    visited_article_ids = set([initial_article_id])
    #recursively use get_related_articles to get the related articles to each query
    for article_id in article_relationships[initial_article_id][initial_article_id]:
        if article_id not in visited_article_ids:
            related_articles = get_related_articles(article_id)
            article_relationships[article_id] = related_articles
            visited_article_ids.add(article_id)
            

    return article_relationships
#find touples in each of the results above and allocate them in unique tuple pairs
def find_tuples(article_relationships):
    tuples = set()

    for article_id, related_articles in article_relationships.items():
        for related_PMID in related_articles.get(article_id, []):
            if related_PMID in article_relationships and article_id in article_relationships[related_PMID].get(related_PMID, []):
                ordered_tuple = (article_id, related_PMID)
                tuples.add(ordered_tuple)


    return tuples

def main():
    #ask for input which can be a pubmed link or the PMID remember that PMID is the convention used for article ID within pubmed DB
    starting_PMID = input("Please input your PubMed link or PMID number here: ")
    #fetch the PMID
    article_PMID = get_PMID(starting_PMID)
    
    #check if the value is cofrrect and proceeds
    if article_PMID:
        article_relationships = get_all_article_relationships(article_PMID)
    #checks if there are any related articles and proceed to order them on touples
        if article_relationships:
            ordered_tuples = find_tuples(article_relationships)
            print("Ordered Tuples:", ordered_tuples)
        else:
            print("No article relationships found.")

if __name__ == "__main__":
    main()
