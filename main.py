import requests

def main():
    URL = 'https://primamedia.ru/news/'
    response = requests.get(URL, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'})

    print(response.status_code)
    response.raise_for_status()
    response.encoding = 'utf-8'
    #print(response.text)

    #запись в файл
    f = open('index.html', 'w')
    f.write(str(response.status_code))
    f.write(response.text)
    f.close()

if __name__ == '__main__':
    main()