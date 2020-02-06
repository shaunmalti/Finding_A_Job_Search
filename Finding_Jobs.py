import requests
import bs4
from bs4 import BeautifulSoup
import numpy as np
import itertools
import pandas as pd

URL = 'https://www.indeed.co.uk/jobs?q=junior%20data%20scientist&l=United%20Kingdom'
# add to URL - param start to change page currently viewing
baseURL = 'https://www.indeed.co.uk'

def main():
    # loop using start param to change page
    # loop over 35 pages of job postings
    k = 20
    # k is number of pages to iterate over
    allJobPosts = []
    for num in np.arange(0, k, 10):
        page = requests.get(URL, params=dict(
            start=num
        ))
        soup = BeautifulSoup(page.text, "lxml")
        allJobPosts.append(getHrefFromJobPost(soup))

    # merge into flat list
    merged = list(itertools.chain.from_iterable(allJobPosts))

    # create pd to save
    cols = ['JobTitle', 'CompName', 'JobLoc', 'JobPay', 'JobEmplType', 'JobURL', 'JobDesc']
    jobDf = pd.DataFrame(columns=cols)

    for item in merged:
        newPage = requests.get(baseURL + item)
        soup = BeautifulSoup(newPage.text, "lxml")

        print('************************')
        print(baseURL + item)
        print('URL')
        print('************************')

        # job title
        jobTitle = soup.find_all('div', attrs={"class": "jobsearch-JobInfoHeader-title-container"})[0].text

        # company name
        compName = soup.find_all('div', attrs={"class": "icl-u-lg-mr--sm"})[0].text

        # location
        jobLoc = soup.find_all('div', attrs={"class": "jobsearch-JobMetadataHeader-itemWithIcon"})[0].text

        # employment type and pay
        jobPay = 'not listed'
        try:
            jobEmplType = soup.find_all('div', attrs={"class": "jobsearch-JobMetadataHeader-itemWithIcon"})[1].text
            if '£' in jobEmplType or '€' in jobEmplType:
                jobPay = jobEmplType
                try:
                    jobEmplType = soup.find_all('div', attrs={"class": "jobsearch-JobMetadataHeader-itemWithIcon"})[2].text
                except:
                    jobEmplType = "not listed"
        except:
            jobEmplType = "not listed"

        # job description
        jobDesc = soup.find_all('div', attrs={"class": "jobsearch-jobDescriptionText"})[0].text.replace('\n',' ')

        # job url
        jobUrl = baseURL + item

        # jobDf[jobDfLen] = jobPost
        jobDf = jobDf.append({'JobTitle': jobTitle, 'CompName': compName, 'JobLoc': jobLoc, 'JobPay': jobPay, 'JobEmplType': jobEmplType, 'JobDesc': jobDesc, 'JobURL': jobUrl}, ignore_index=True)

    jobDf.to_csv('jobs.csv')



def getHrefFromJobPost(soup):
    jobPosts = []
    for div in soup.find_all(name="div", attrs={"class":"row"}):
        for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
            jobPosts.append(a.get('href'))
    return jobPosts


if __name__ == '__main__':
    main()