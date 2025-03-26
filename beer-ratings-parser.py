import requests
from bs4 import BeautifulSoup
import time
import csv
import os

def parse_beer_ratings(html_content):
    """
    Parse HTML content to extract beer details.
    
    :param html_content: String containing the HTML to parse
    :return: List of dictionaries with beer details
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all beer articles
    beer_articles = soup.find_all('article', class_='wpgb-card')
    
    # List to store beer details
    beer_details = []
    
    # Extract details for each beer
    for article in beer_articles:
        # Beer name
        beer_name_elem = article.find('h3', class_='wpgb-block-2')
        beer_name = beer_name_elem.get_text(strip=True) if beer_name_elem else 'Unknown'
        
        # Brewery name
        brewery_elem = article.find('div', class_='wpgb-block-3')
        brewery_name = brewery_elem.get_text(strip=True) if brewery_elem else 'Unknown'
        
        # Beer style
        style_elems = article.find_all('span', class_='wpgb-block-term', attrs={'data-id': True})

        beer_style = 'Unknown'
        for style_elem in style_elems:
            # List of rank terms to exclude, since both rank and style use the same class
            rank_terms = ['Gold', 'Silver', 'Bronze']
            if style_elem.get_text(strip=True) not in rank_terms:
                beer_style = style_elem.get_text(strip=True)
                break

        # Rating
        rating_elem = article.find('div', class_='wpgb-block-15')
        rating = rating_elem.get_text(strip=True) if rating_elem else 'Unknown'
        
        # Compile details
        beer_info = {
            'Name': beer_name,
            'Brewery': brewery_name,
            'Style': beer_style,
            'Rating': rating
        }
        
        beer_details.append(beer_info)
    
    return beer_details

def save_to_csv(beer_details, filename=None):
    """
    Save beer details to a CSV file.
    
    :param beer_details: List of dictionaries containing beer information
    :param filename: Optional custom filename, defaults to 'beer_ratings.csv'
    """
    # Use default filename if not provided
    if filename is None:
        filename = 'beer_ratings.csv'

    # Ensure the filename ends with .csv
    if not filename.lower().endswith('.csv'):
        filename += '.csv'
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            # If we have data, determine fieldnames from the first dictionary
            if beer_details:
                fieldnames = beer_details[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')

                if os.stat(filename).st_size == 0:
                    writer.writeheader()
                
                # Write data rows
                for beer in beer_details:
                    writer.writerow(beer)
            
            print(f"Beer ratings saved to {filename}")
    
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def main(url):
    """
    Fetch and parse beer ratings from a given URL.
    
    :param url: Website URL to scrape
    """
    try:
        # Send a GET request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse the beer ratings
        beers = parse_beer_ratings(response.text)
        
        # Save to CSV
        save_to_csv(beers)
        
    except requests.RequestException as e:
        print(f"Error fetching the website: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':

    for p in range(1,51):
        time.sleep(2)
        page = f'https://awards.untappd.com/region/united-states-wisconsin/?_pagination_001={p}'
        main(page)