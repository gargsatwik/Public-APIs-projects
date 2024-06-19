import requests
import bs4

response = requests.get(url="https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features"
                            "/best-movies-2/").text
soup = bs4.BeautifulSoup(response, "html.parser")
names = soup.find_all(name="h3")
titles = []
for tag in names:
    titles.append(tag.getText())

i = 1
with open("list.txt", "w") as file:
    for name in titles:
        file.write(f"{i}) " + name.split(" ", 1)[1] + "\n")
        i += 1

print(titles)
