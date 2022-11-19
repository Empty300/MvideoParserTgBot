import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains



def gethtml1():
    driver = webdriver.Chrome(
        executable_path="chrom/chromedriver.exe"
    )
    driver.maximize_window()

    try:
        driver.get("https://www.mvideo.ru/catalog?from=footer")
        time.sleep(2)
        with open("temp.html","w",encoding="utf8") as file:
            file.write(driver.page_source)
        return driver.page_source
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

with open("temp.html", "r", encoding="utf8") as file:
    texti = file.read()
soup = BeautifulSoup(texti, "lxml")
all_tags = soup.find("div", class_="c-catalog").find_all("div", class_ ="u-inline-block u-mr-12 u-mb-12 c-catalog-item__links-item")
result = {}
for i in all_tags:
    if "mvideo" in i.find("a").get("href"):
        result[i.text.strip()] =i.find("a").get("href")
    else:
        result[i.text.strip()] = f'https://www.mvideo.ru{i.find("a").get("href")}'
with open("result.json", "w",encoding="utf8") as file:
    json.dump(result, file, indent=4, ensure_ascii=False)
names_list = list()
categorys = {}
count = 0
for i in result:
    if "vse-akcii" in result[i] or "blog" in result[i] or "xiaomi" in result[i]:
        continue
    driver = webdriver.Chrome(
        executable_path="chrom/chromedriver.exe"
    )
    driver.maximize_window()
    try:
        driver.get(result[i])
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "lxml")
        all_data = soup.find("div",class_ = "sidebar-categories-wrapper").find_all("li", class_ = "sidebar-category")
        for i in all_data:
            if i.text.strip() not in names_list:
                if (i.find("a").get("href").split("/")[-1].split("-")[-1]).isdigit():
                    names_list.append(i.text.strip())
                    categorys[i.text.strip()] = i.find("a").get("href").split("/")[-1].split("-")[-1]
                    print(i.text.strip(),i.find("a").get("href").split("/")[-1].split("-")[-1])
            count+=1
            print(len(all_data) - count)



    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

with open("categories.json", "w", encoding="utf8") as file:
    json.dump(categorys, file, indent=4, ensure_ascii=False)








