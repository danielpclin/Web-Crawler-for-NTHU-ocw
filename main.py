import bs4
import requests
import string
import magic
import mimetypes
import os
import urllib

baseUrl = 'http://ocw.nthu.edu.tw/ocw/'
# (Directory Name, Url, Start Index)
courses = [('Differential Equation', 'http://ocw.nthu.edu.tw/ocw/index.php?page=chapter&cid=145&chid=1775', 1),
           ('Operating System', 'http://ocw.nthu.edu.tw/ocw/index.php?page=chapter&cid=141&chid=1819', 1)]


def download(url, file_name, dir_name=None, ext=None):

    # get request
    while True:
        response = requests.get(url, stream=True)
        if response.status_code == requests.codes.ok:
            break

    # Save in directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if dir_name is not None:
        dest_dir = os.path.join(script_dir, dir_name)
        try:
            os.makedirs(dest_dir)
        except OSError:
            pass  # already exists
        path = os.path.join(dest_dir, file_name)
    else:
        path = file_name

    print(f"Writing to file: {file_name}")
    # open in binary mode
    with open(path, "wb") as file:
        # write to file
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

    # guess mime if ext not given
    if ext is None:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(open(path, 'r+b').read(1024))
        # https://docs.python.org/3/library/functions.html#open
        ext = mimetypes.guess_extension(mime_type)
    # rename file with extension
    print(f"Renaming file {file_name} to {file_name+ext}")
    os.rename(path, path+ext)


for directory, nextUrl, start in courses:
    print(directory+": ")
    haveNext = True
    index = 1
    while haveNext:
        print(f"Lecture {str(index)}")
        while True:
            request = requests.get(nextUrl)
            if request.status_code == requests.codes.ok:
                break
        soup = bs4.BeautifulSoup(request.text, "lxml")
        if start <= index:
            imgs = soup.find_all('img', title="離線觀看")
            for img, letter in zip((img for img in imgs if img.parent.name == 'a'), string.ascii_uppercase):
                print("Link =", img.parent['href'])
                parseResult = urllib.parse.urlparse(img.parent['href'])
                queryDict = urllib.parse.parse_qs(parseResult.query)
                queryDict['filename'] = ['1920_1080_3072.MP4']
                queryString = urllib.parse.urlencode(queryDict, doseq=True)
                parseResult = parseResult._replace(query=queryString)
                downloadUrl = urllib.parse.urlunparse(parseResult)
                print("Changing link to high quality:", downloadUrl)
                download(downloadUrl, str(index) + letter, directory)
                # http://ocw.nthu.edu.tw/videosite/assert/3813/1920_1080_3072.MP4
        else:
            print("Page smaller than given Start index, Ignoring....")
        nextUrlList = soup.find('strong', text='相關連結').parent.next_sibling.next_sibling.find_all('li')
        if index == 1:
            nextUrl = baseUrl + nextUrlList[0].a['href']
        elif index == 2:
            nextUrl = baseUrl + nextUrlList[1].a['href']
        elif len(nextUrlList) >= 3:
            nextUrl = baseUrl + nextUrlList[2].a['href']
        else:
            haveNext = False
            print("=== Download Finished ===")
        index += 1
        print()
    print()
