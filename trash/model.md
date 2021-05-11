# Search Engine Model:

Search By:
    - Person Name
    - Subject Area

### Filters:
- Country
- Institute

## Search via Person Name

###  What is a Peron's name?
- There is a name mentioned in the Google Scholar Page. (Need to remove the PHD details that are sometimes given in Name by some professors)
- There is a author name, which is the most frequent author name in the Publication Topic author's. (N Misra)

For Example: Neeldhara Misra, N Misra. We will take into account both.
- (NEW) try to implement using KNN

### Ranking Parameters:
- Reputation of a Professor:
  - h_index (all)

### Incentives in Ranking:
- If a Professor has provided a homepage
- If a Professor has a verified email
- If the professor is from a reputed Institutes (e.g. The Ivy League)
- If a Professor has a Profile Pic (not sure, if this should be an incentive)


## Search via Subject Area

## Ranking Parameters:
  - Default (modified TF-IDF) -- Final
  - Activeness for a year range (input : n, the number of citations on the papers written within the last 'n' years) along with i_10 index (since 2016) -- Final No. of papers
  - Slope of Citations (the average slope of the number of citations over the last 10 years) except current year --
  - h_index
  - Institute Reputation (based on the QS world ranking or similar ranking of the institute of the professor)

### Incentives in Ranking:
- If the professor is from a reputed Institutes (e.g. The Ivy League or top 50 institutes from their respective country)

### Penalties in Ranking:
- If a Professor does not have a verified email
- If a Professor have not provided a homepage
- If a Professor does not have a Profile Pic (not sure, if this should be an penalty)

### Calculation of scores for a subject topic (Default : modified TF-IDF):
- For subject derieved from Paper names:
  - Along with usual IDF factor, Factor of $log(No. of Citations of paper/ Total No. of Citations with given term)
  - Incentive Bonus if the paper was published in a highly-regarded Conference

- For subject derieved from Subjects mentioned in Google Scholar by the Person:
  - Along with usual IDF factor, Factor of $log(Total No. of Citations of person/ Total No. of Citations with given term of people with this subject)
  - $beta$, It will be a factor decided by us, that how much importance we give to these topics as compared to topics derieved from paper topics

- Bonus points:
-  For two terms of the search coming together. (decided by us)
-  For three terms of teh search coming together. (decided by us)
-  ... Similarly

### Incentives in Ranking:
- If the professor is from a reputed Institutes (e.g. The Ivy League or top 50 institutes from their respective country)
- If a professor have mentioned more than 5 (or Y) co-authors on his google-scholar
  - **[ we can take into account how reputed(number of citations) those co-authors are, but will have to write scrapy program for it]**
- If a professor have mentioned more than 10 (or Z) co-authors

### Penalties in Ranking:
- If a Professor does not have a verified email
- If a Professor have not provided a homepage
- If a Professor does not have a Profile Pic (not sure, if this should be an penalty)
- If the professor has provied more than 6(or X) topics in his google scholar. (spammming topics)

## Sliders in Search:
- We will have [1-10] sliders for the ranking parameters 

Ranking Final Points:
 = (TF-IDF / max-TF-IDF) * a1 + [ (h_index / max h_index in search) * a2 +     .......                  ] (if selected by user)

## Search Feedback Data:
- On a given search, the first page clicked get bonus of x1, second page clicked x2 and so on.
- In case a similar search is made in future, these bonus points would be considered.


## What to extract from the page:
- Name 
- Verified email -- True/False
- HomePage -- NOT FOUND/homepage
- self_topics
- total_citations
- citations over the year

(By Tonight)

## WorkPlan:
- Feature Extraction (Tonight)
- Basic TF-IDF
  - NO Filters/Scales


