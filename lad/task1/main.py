from bs4 import BeautifulSoup
import requests
import csv
import ast

def save_to_csv(job_data_list):
    
    csv_file_name = 'job_data.csv'

    
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Company Name', 'Vacancy Title', 'Position Title', 'Level', 'Skills']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()

        for job_data in job_data_list:
            writer.writerow(job_data)


def get_job_listings(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        soup = BeautifulSoup(response.text, 'lxml')
        jobs = soup.find_all('div', class_='vacancy-card__info')
        return jobs

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []


def extract_job_data(job):
    try:
        company_name = job.find('div', class_='vacancy-card__company-title').text.strip()
        vacancy_title = job.find('div', class_='vacancy-card__title').text.strip()
        experience = job.find('div', class_='vacancy-card__skills')
        skills = [span.text.strip() for span in experience.find_all('span') if '•' not in span.text]

        position_title = skills[0] if skills else None
        level = None
        additional_skills = []

        
        common_levels = ["Средний (Middle)", "Старший (Senior)", "Младший (Junior)","Стажёр (Intern)","Ведущий (Lead)"]
        for skill in skills[1:]:
            print(skill)
            if skill in common_levels:
                level = skill
            else:
                additional_skills.append(skill)
        
        
        return {
            'Company Name': company_name,
            'Vacancy Title': vacancy_title,
            'Position Title': position_title,
            'Level': level,
            'Skills': additional_skills
        }

    except Exception as e:
        print(f"An error occurred while extracting job data: {e}")
        return {}


def main():
    job_data_list = []
    base_url = 'https://career.habr.com/vacancies'
    search_query = 'Data%20Science'
    location = 'r_14068'  
    total_job_count = 0

    for page in range(1, 6):  
        page_url = f'{base_url}?locations[]={location}&page={page}&q={search_query}&type=all'
        jobs = get_job_listings(page_url)
        total_job_count += len(jobs)  

        if not jobs:
            print(f"No job listings found on page {page}.")
            break  

        for job in jobs:
            job_data = extract_job_data(job)
            if job_data:
                job_data_list.append(job_data)
                print(f"Job Data: {job_data}")
                print('-' * 50)

    print(f"Total job listings found: {total_job_count}")

    save_to_csv(job_data_list)

if __name__ == "__main__":
    main()
