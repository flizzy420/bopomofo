from loader import words
import re

sep = ""

def trans_word(text):
    if text in words:
        try:
            res = ""
            # print(re.split('-|ˊ|ˇ|ˋ|˙', words[text]))
            for x in re.split('-|ˊ|ˇ|ˋ|˙', words[text]):
                x = x.strip()
                if x != "":
                    res = res + x[0]

            return res
        except:
            return ""
    else:
        return text

def trans_sentense(text):
    ret = ""
    buf = ""
    for x in text:
        if x not in words:
            ret = ret + sep + trans_word(buf)
            buf = ""
            ret = ret + sep + trans_word(x)
            continue
        if buf + x not in words:
            ret = ret + sep + trans_word(buf)
            buf = x
        else:
            buf = buf + x
    ret = ret + sep + trans_word(buf)
    return ret

if __name__ == "__main__":
    # print(trans_sentense("不再忍耐那些為你長久忍耐的耳語"))
    
    # while True:
    #     x = input(">>> ")
    #     print(trans_sentense(x))

    import requests, os, threading
    from bs4 import BeautifulSoup

    # target = "ㄅㄗㄖㄋㄋㄒㄨㄋㄔㄐㄖㄋㄉㄦㄩ"
    # target = "ㄉㄋㄏㄕㄐㄅㄗㄐㄘㄋㄨㄉㄧㄏㄧㄅㄗㄆㄘ"
    target = "ㄉㄋㄗㄉㄋㄊㄨㄅㄗㄕㄍㄕㄌ"

    # response = requests.get("https://mojim.com/twh100163.htm") # Jolin
    response = requests.get("https://mojim.com/twh100090.htm") # Amei
    soup = BeautifulSoup(response.text, "html.parser")

    lyrics_list = []
    for node in soup.find_all("a"):
        try:
            if "/twy" in node.attrs['href']:
                lyrics_list.append(node.attrs['href'])
        except KeyError:
            pass

    # lyrics_list = ["/twy100163x33x28.htm"]

    print(len(lyrics_list))

    def extract_chinese(text):
        text = text.split("[00:00.00]")[0]

        blacklist = [
            "更多更詳盡歌詞 在 ※ Mojim.com　魔鏡歌詞網",
            "修正歌詞友站連結"
        ]

        for x in blacklist:
            text = text.replace(x, "")

        pattern = re.compile("[\u4e00-\u9fa5]")
        return "".join(pattern.findall(text))

    def process(link, filename):
        response = requests.get("https://mojim.com/" + link)
        soup = BeautifulSoup(response.text, "html.parser")
        lyrics = soup.find("dd", class_="fsZx3").text
        lyrics_chi = extract_chinese(lyrics)
        lyrics_bopo = trans_sentense(lyrics_chi).replace("˙", "　")

        with open("cache/" + filename, "w", encoding="utf-8") as file:
            file.write(lyrics_chi)
            file.write("\n\n\n")
            file.write(lyrics_bopo)

        if target in lyrics_bopo:
            print(lyrics_chi)
            print(lyrics_bopo)
        
        limiter.release()

    if not os.path.exists("cache"):
        os.makedirs("cache")

    limiter = threading.Semaphore(20)
    for i in range(len(lyrics_list)):
        link = lyrics_list[i]
        filename = link.replace("/", "")

        if not os.path.exists("cache/" + filename) or True:
            print(i, "https://mojim.com" + link)
            limiter.acquire()
            threading.Thread(target=process, args=(link, filename)).start()