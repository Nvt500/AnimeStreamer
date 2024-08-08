import urllib.request
import urllib.parse
import json
from threading import Thread
from dataclasses import dataclass
from html_parser import HTML


@dataclass
class Episode:
    
    episode_id: str
    download_link: str
    quality: str
    streaming_links: list[str]
    
    
    def __repr__(self) -> str:
        
        return self.episode_id
    
    
    def __iter__(self) -> iter:
        
        return iter([self.episode_id, self.download_link, self.quality, self.streaming_links])
    
    
    def get_episode_links(self) -> None:
        
        self = get_episode_info(self)


@dataclass
class Anime:
    
    anime_id: str
    title: str
    cover_image: str
    episodes: list[Episode]
    
    
    def __repr__(self) -> str:
        
        return f"{self.title}, {self.anime_id}, {self.cover_image}"
    
    
    def get_episodes(self, get_episode_links: bool = True) -> None:
        
        self = get_episode_ids(self)
        
        if get_episode_links:
            for episode in self.episodes:
                Thread(target=episode.get_episode_links).start()
    
    
    def episodes_have_links(self) -> bool:
        
        for episode in self.episodes:
            if not (episode.download_link and episode.streaming_links):
                return False
        
        return True


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
}

BASE_URL = "https://anitaku.so/"

BASE_URL_API = "https://ajax.gogocdn.net/"

SEARCH_URL = "{}search.html?keyword={}" # base_url, query

ANIME_URL = "{}category/{}" # base_url, anime_id

EPISODE_URL = "{}{}" # base_url, episode_id


def get_episode_info(episode: Episode) -> Episode:
    
    url = EPISODE_URL.format(BASE_URL, episode.episode_id)

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=HEADERS
    )
    
    while True:
        try:
            response = urllib.request.urlopen(request)
            if response.read(10) != "".encode():
                break
        except Exception:
            pass
        
    
    parser = HTML(response.read().decode("latin-1"))
    
    info = parser.find("div", {"class": "anime_muti_link"})[0].children[0]
    
    for li in info.children:
        episode.streaming_links.append(li.children[0].attrs.get("data-video"))
    
    url = parser.find("li", {"class": "dowloads"})[0].children[0].attrs.get("href")
    
    download_url = "https://embtaku.com/download"
    payload = {
      "id": url[ url.find("id=")+3 : url.find("id=")+3 + url[url.find("id=")+3:].find("&") ],
      "captcha_v3": "03AFcWeA64suoYn2KwV7r-9DWCPUmeVUp9twCjG03ryfCaf9HO3PAOrZmAZnE-R8Ry-eiglgCrcYgQHhVhswSOVEhUOAsfPuc4uD5K9o-O87-8jMREHACcZUebMxYpmMFLNCXxFblrpMNIoce0y-BqbZHXdJ15U30bGoKcYStybEyHHkB4EV9ehr0sdGfKPHoNvaXhus5jPBYBav45Obevmwe9J1La7swaVRbIg44orcVPH0uvqn4QbIWY2NdKhyfh8yupvjNNJANmYj9cftub_9by69cYaaj_AEOQ0M_svFXn1stbN_i5x9FdS_01OgkBnFIKDvbnoLMkZq3ro2ud3976TjIQ11mebjExfsjFreUwRTsUDpEWTE2eLpkiihHpqw-nu7ByJTbfsIXDYgLPJ12jQA2fjZGjIthUH2ansX2tezPABkwc1yvtAS0JFwvv7ZbMw48bc1jtPiZrrdCjDwzD1Sjo18Z8tmrfDi2dQxBV1UOr_DcmdwJhFXaYtg2CsgGsYnCqshJ-bI44RCs4ACAGSsIF3eNcNCJ8zZ3YbltO036FiQl9Fvg6iJ6zrxeKavj85V2SV4iirvRoGE8_McCv6N5VedjmRT1tVCAmHMpBjv-0B-ErpHEIwrF-6P-WAEiukK3i_c8T5Ub7XE1AZ9QHF0pXq1fK4G-zq4-feiD5q4CTv35EkbA"
    }
    
    urlencoded = urllib.parse.urlencode(payload, doseq=False)
    urlencoded = urlencoded.encode('ascii')
    
    request = urllib.request.Request(
        url=download_url,
        data=urlencoded,
        method="POST",
        headers=HEADERS
    )
    
    while True:
        try:
            response = urllib.request.urlopen(request)
            break
        except Exception:
            pass
    
    parser = HTML(response.read().decode("latin-1"))
    
    links = parser.find("div", {"class": "dowload"})
    
    qualities = ["720", "1080", "480", "360"]
    links = [link.children[0] for link in links if link.children[0].attrs.get("download")]
    
    for quality in qualities:
        
        link = [link for link in links if quality in link.data]
        if link:
            link = link[0]
            
            url = link.attrs.get("href")
            
            request = urllib.request.Request(
                url=url,
                method="GET",
                headers=HEADERS
            )
            
            try:
                response = urllib.request.urlopen(request)
            except Exception:
                continue
            
            if response.read(10) == "".encode():
                continue
            
            episode.quality = quality + "p"
            episode.download_link = url
            
            return episode
    
    return episode


def get_episode_ids(anime: Anime) -> Anime:
    
    url = ANIME_URL.format(BASE_URL, anime.anime_id)
    
    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=HEADERS
    )
    
    response = urllib.request.urlopen(request)
    
    parser = HTML(response.read().decode("latin-1"))
    
    info = parser.find("div", {"class": "anime_info_episodes_next"})[0]
    
    url_parameters = {
        "ep_start": "",
        "ep_end": "",
        "movie_id": "",
        "default_ep": "",
        "alias_anime": ""
    }
    
    for inp in info.children:
        url_parameters[inp.attrs.get("id")] = inp.attrs.get("value")
    
    info = parser.find("ul", {"id": "episode_page"})[0].children[0].children[0]
    
    url_parameters["ep_start"] = info.attrs.get("ep_start")
    url_parameters["ep_end"] = info.attrs.get("ep_end")
    
    url = f"{BASE_URL_API}ajax/load-list-episode?ep_start={url_parameters.get('ep_start')}&ep_end={url_parameters.get('ep_end')}&id={url_parameters.get('movie_id')}&default_ep={url_parameters.get('default_ep')}&alias={url_parameters.get('alias_anime')}"
    
    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=HEADERS
    )

    response = urllib.request.urlopen(request)
    
    parser = HTML(response.read().decode("latin-1"))
    
    episode_ids = []
    for li in parser.root.children:
        l = li.children[0].attrs.get("href")
        episode_ids.append(l[l.find("/")+1:])
    
    episode_ids.reverse()
    
    for ep_id in episode_ids:
        anime.episodes.append(Episode(ep_id, "", "", []))
    
    return anime


def search(query: str) -> list[Anime]:
    
    query = query.strip().split(" ")
    query = "+".join(query)
    
    url = SEARCH_URL.format(BASE_URL, query)
    
    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=HEADERS
    )
    
    response = urllib.request.urlopen(request)
    
    parser = HTML(response.read().decode("latin-1"))
    
    items = parser.find("ul", {"class": "items"})[0].children
    
    animes = []
    for item in items:
        try:
            tag = item.children[0].children[0]
        except Exception:
            return ["No Results"]
        anime_id =  tag.attrs.get("href")[tag.attrs.get("href").rfind("/")+1:]
        title = tag.attrs.get("title")
        tag = tag.children[0]
        cover_image = tag.attrs.get("src")
        animes.append(Anime(anime_id, title, cover_image, []))
    
    return animes