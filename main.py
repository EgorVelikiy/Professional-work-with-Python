import requests
import bs4
import fake_headers
import time
import json

import unicodedata
from unicodedata import normalize

headers_gen = fake_headers.Headers('opera', os='windows')
res = requests.get('https://spb.hh.ru/search/vacancy?area=2&area=1&order_by=publication_time&ored_clusters=true&text'
                   '=python&search_period=0', headers=headers_gen.generate())

main_html = res.text
main_soup = bs4.BeautifulSoup(main_html, 'lxml')
vacancy_list = main_soup.find('div', id='a11y-main-content')
vacancy_tags = vacancy_list.find_all('div', class_='vacancy-serp-item__layout')

parsed_data = []
keywords = ['Django', 'Flask']

for vac_tag in vacancy_tags:
    title = vac_tag.find('h3', class_='bloko-header-section-3').text
    link = vac_tag.find('a', class_='serp-item__title')['href']

    salary_tag = vac_tag.find('span', class_='bloko-header-section-2')
    if salary_tag is not None:
        salary = unicodedata.normalize('NFKD', salary_tag.text).encode('UTF-8', 'ignore')
        salary = salary.decode('UTF-8')
    else:
        salary = 'Не указана'

    company_tag = vac_tag.find('a', class_='bloko-link bloko-link_kind-tertiary')
    company = unicodedata.normalize('NFKD', company_tag.text).encode('UTF-8', 'ignore')
    company = company.decode()

    city_full_tag = vac_tag.find('div', class_='vacancy-serp-item__info')
    city_tag = city_full_tag.find('div', class_='bloko-text' ,attrs={"data-qa": "vacancy-serp__vacancy-address"})
    city = city_tag.text.split(',')[0]

    time.sleep(0.3)
    response_vacancy = requests.get(link, headers=headers_gen.generate())
    response_vacancy_html = response_vacancy.text
    response_vacancy_soup = bs4.BeautifulSoup(response_vacancy_html, 'lxml')
    vacancy_desc = response_vacancy_soup.find('div', attrs={"data-qa": "vacancy-description"})
    vacancy_desc_text = vacancy_desc.text

    if any(kw.lower() in vacancy_desc_text.lower() for kw in keywords):
        parsed_data.append({
            'title': title,
            'link': link,
            'salary': salary,
            'company': company,
            'city': city
        })

with open('vacancy.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)

