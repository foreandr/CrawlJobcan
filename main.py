import re
import time
import random
import hyperSel
import hyperSel.selenium_utilities

search_keywords = ['computer','database','software', 'python', 'programmer', 'developer', 'software tester', 'software qa', 'software quality assurance', 'data', 'IT', 'information technology', 'analyst']

def custom_strip(input_string):
    # Split the string by whitespace characters
    words = input_string.split()

    # Join the words back together with a single space between them
    cleaned_string = ' '.join(words)

    return cleaned_string

def extract_numbers(input_string):
    # Use regular expression to find all numeric sequences
    numbers = re.findall(r'\d+', input_string)

    # Join the numbers into a comma-separated string
    result = ''.join(numbers)
    
    return result

def get_total_num_results_from_job_bank_search(driver):
    try:
        soup = hyperSel.selenium_utilities.get_driver_soup(driver)
        item = soup.find("span", class_='found').text
        number_cleaned = extract_numbers(input_string=item)
        # print("item:", item)
        return int(number_cleaned)
    except Exception as e:
        print("COULDNT GET TOTAL NUM RESULTS?")
        return 10

def fix_job_title(job_title):
    if 'verified' in job_title.lower():
        title = job_title.lower().split('verified')[0]
        return title.title()
    else:
        return job_title.title()
    
def get_all_job_posts_on_page(driver):
    soup = hyperSel.selenium_utilities.get_driver_soup(driver)
    articles = soup.find('div', class_="results-jobs")
    skipped_jobs = 0
    gotten_jobs = []
    for article in articles:
        try:
            job_title = article.select_one('span.noctitle').text.strip()
            title = fix_job_title(custom_strip(job_title))
            job_url = article.select_one('a.resultJobItem')['href']

            full_url = f'https://www.jobbank.gc.ca{job_url}'
            gotten_jobs.append([title, full_url])
        except Exception as e:
            skipped_jobs+=1
            continue

    total_jobs = len(gotten_jobs) + skipped_jobs
    return gotten_jobs, total_jobs

def job_search_url(keyword):
    print("keyword", keyword)

    template = 'https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=@KEYWORD&locationstring='
    url = template.replace('@KEYWORD', keyword)

    driver = hyperSel.selenium_utilities.open_site_selenium(url, show_browser=True)

    total_num_results = get_total_num_results_from_job_bank_search(driver)
    posts_per_page = 25
    print("total_num_results", total_num_results)

    iterations = int(round((total_num_results / posts_per_page) , 0))
    print('iterations', iterations)
    print("===================================================================================")

    for i in range(1, iterations):
        url_ = f'https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={keyword}&locationstring=&page={i}'
        driver.get(url_)
        hyperSel.selenium_utilities.default_scroll_to_buttom(driver, time_between_scrolls=5)    
        hyperSel.selenium_utilities.click_button(driver, xpath='''//*[@id="moreresultbutton"]''', time=360)
        
        posts, total_jobs = get_all_job_posts_on_page(driver)
        for post in posts:
            write_job_to_file_as_done(post)

        # input("PAUSE")
    hyperSel.selenium_utilities.close_driver(driver)

def get_company_name(soup):
    comapny_name = None
    
    for i in soup.find_all('span', {'property': 'name'}):
        # print(strip())
        nom = custom_strip(input_string=i.text)
        if 'government' not in nom.lower():
            comapny_name = nom
    return comapny_name
    
def check_string_for_good_keywords(combination_string):
    job_wanted_keywords = ['python', 'backend', 'junior', 'testing', 'recent grad', 'entry', 'jr',' back end', 'fresh', 'flask', 'intermediate', 'mid']
    for keyword in job_wanted_keywords:
        if check_keyword_with_regex(string=combination_string, keyword=keyword):
            # colors.print_green(f"KEYWORD SUCESS : [{keyword}]")
            return True
    for keyword in search_keywords:
        if check_keyword_with_regex(string=combination_string, keyword=keyword):
            # colors.print_green(f"KEYWORD SUCESS : [{keyword}]")
            return True
    return False

def check_string_for_bad_keywords(combination_string):
    combination_string = combination_string.lower()
    keywords_to_avoid = []
    for keyword in keywords_to_avoid:
        if check_keyword_with_regex(string=combination_string, keyword=keyword):
            # colors.print_warning(f"KEYWORD FAILED : [{keyword}]")
            return True, keyword
    return False, None

def check_keyword_with_regex(string, keyword):
    # Convert both string and keyword to lowercase for case-insensitive matching
    string_lower = string.lower()
    keyword_lower = re.escape(keyword.lower())

    # Use a regular expression with word boundaries for more accurate matching
    pattern = re.compile(rf'\b{keyword_lower}\b')
    
    return bool(pattern.search(string_lower))

def keyword_check_job_details(job_string):
    job_string = job_string.lower()
    result_good = check_string_for_good_keywords(combination_string=job_string)
    result_bad = check_string_for_bad_keywords(combination_string=job_string)

    if result_good and not result_bad:
        return True
    else: return False

def write_job_to_file_as_done(job):
    try:
        with open('./files/applications_already_done.txt', 'a') as file:
            file.write(str(job) + '\n')
        # print(f"Job '{job}' has been marked as done and written to 'done_jobs.txt'.")
    except Exception as e:
        print(f"Error writing job to file: {e}")

def main():
    print("--STARTING MAIN--")
    random.shuffle(search_keywords)
    while True:
        for keyword in search_keywords:
            job_search_url(keyword)
        print('DID ALL KEYWORDS, WAITING 12 HOURS...')
        time.sleep(3600 * 12) # wait 12 hours

if __name__ == "__main__":
    main()
