from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_page(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = soup.title.get_text(strip=True) if soup.title else ""
    
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag['content'].strip() if description_tag and description_tag.get('content') else ""

    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    body = soup.find('body')
    if body:
        full_text = ' '.join(body.get_text(separator=' ').split())
    else:
        full_text = ''
    
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']

        absolute_url = urljoin(base_url, href)
   
        if absolute_url.startswith(('http://', 'https://')) and '#' not in absolute_url:
            links.add(absolute_url)
            
    return {
        "title": title,
        "description": description,
        "content": full_text, 
        "links": list(links)
    }