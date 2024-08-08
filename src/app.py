import api
from flask import Flask, render_template_string, request, session

app = Flask(__name__)

app.secret_key = b'890b51db46ed652bb62aecc5f4c2d5f64309cfa2a50afcd130bdb420837182a3'

@app.route("/")
def get_root():
    
    return """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Search | Anime Downloader</title>
            </head>
        
            <script>
                function openURL()
                {
                    let data = document.getElementById("url-input").value;
                    data = data.replaceAll(" ", "+");
                    
                    const a = document.createElement('a');
                    a.href = "/search?query=" + data;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            </script>
        
            <body>
                <h1>Enter Anime Name</h1>
                <input id="url-input" placeholder="Enter here:" autofocus>
                <input type="button" value="Open" onclick="openURL();">
            </body>
        </html>
        """


@app.get("/search")
def get_search():
    
    query = request.args.get("query", "")
    
    animes = api.search(query)
    
    session["animes"] = []
    if animes[0] == "No Results":
        session["animes"].append("No Results")
    else:
        for anime in animes:
            session["animes"].append(anime)
    
    return render_template_string("""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Search | Anime Downloader</title>
            </head>
            
            <script>
                function openURL()
                {
                    let data = document.getElementById("url-input").value;
                    data = data.replaceAll(" ", "+");
                    
                    const a = document.createElement('a');
                    a.href = "/search?query=" + data;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            </script>
            
            <style>
                .results
                {
                    width: 100%;
                    height: 300px;
                    border: 2px solid black;
                    display: flex;
                    flex-flow: row wrap;
                    justify-content: space-around;
                    overflow: scroll;
                }
                
                .result
                {
                    height: 90%;
                    text-align: center;
                    margin: 12px 0px 12px 0px;
                    cursor: pointer;
                }
                
                .result p {
                    margin: 8px 0px 12px 0px;
                }
                
                .result img
                {
                    height: 90%;
                }
                
                .loader {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    visibility: hidden;
                    border: 16px solid LightGrey;
                    border-top: 16px solid black;
                    border-radius: 50%;
                    width: 120px;
                    height: 120px;
                    animation: spin 2s linear infinite;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        
            <body>
                <h1>Enter Anime Name</h1>
                <input id="url-input" placeholder="Enter here:" autofocus>
                <input type="button" value="Open" onclick="openURL();">
                
                <div class="results">
                    {% if animes[0] == "No Results" %}
                        No Results
                    {% else %}
                        {% for anime in animes %}
                        <div class="result" onclick="location.href='/stream?anime-id={{ anime.anime_id }}'; document.getElementById('loading').style.visibility = 'visible'">
                            <img src="{{ anime.cover_image }}" alt="Image Not Found">
                            <p>{{ anime.title }}</p>
                        </div>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <br>
                <div class="loader" id="loading"></div>
            </body>
        </html>
        """, animes=session["animes"])


@app.get("/stream")
def get_stream():
    
    anime = [anime for anime in session["animes"] if anime.get("anime_id") == request.args.get('anime-id', '')][0]
    session.pop("animes", None)
    
    anime = api.Anime( anime.get("anime_id"), anime.get("title"), anime.get("cover_image"), anime.get("episodes") )
    
    anime.get_episodes()
    
    while not anime.episodes_have_links():
        pass
    
    return render_template_string("""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Stream | Anime Downloader</title>
            </head>
            
            <script>
                function selectChoice(tag)
                {
                    parent = tag.parentNode;
                    
                    for (let node of parent.children)
                    {
                        node.style.border = "1px solid black";
                    }
                    
                    tag.style.border = "2px solid black";
                }
            </script>
            
            <style>
                .stream-display
                {
                    display: flex;
                }
                
                .list
                {
                    width: 38%;
                    height: 500px;
                    border: 2px solid black;
                    margin-right: 2%;
                }
                
                .list-title
                {
                    text-align: center;
                    height: 5%;
                    font-size: 24px;
                }
                
                .list-content
                {
                    float: bottom;
                    height: 85%;
                    width: 100%;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    align-content: center;
                    overflow: scroll;
                }
                
                .list-content input
                {
                    text-align: center;
                    width: 96%;
                    margin: 2%;
                    padding: 4px;
                    font-size: 16px;
                }
                
                .stream
                {
                    float: right;
                    width: 60%;
                    align-self: center;
                }
                
                .stream-title
                {
                    text-align: center;
                    font-size: 24px;
                }
                
                .stream-video
                {
                    width: 100%;
                }
            </style>
        
            <body>
                <p style="font-size: 20px; text-align: center;"><a href="/">Go To Search</a></p>
                <hr style="border: 1px solid black;">
                <br>
                
                <div class="stream-display">
                    
                    <div class="list">
                        <p class="list-title">Episodes</p>
                        <div class="list-content">
                            {% for episode in anime.episodes %}
                                {% if loop.index == 1 %}
                                    <input type="button" style="border: 2px solid black;" value="Episode {{ loop.index }} {{ episode.quality }}" onclick="document.getElementsByClassName('stream-video')[0].setAttribute('src', '{{ episode.download_link }}'); selectChoice(this);">
                                {% else %}
                                    <input type="button" value="Episode {{ loop.index }} {{ episode.quality }}" onclick="document.getElementsByClassName('stream-video')[0].setAttribute('src', '{{ episode.download_link }}'); selectChoice(this);">
                                {% endif %}
                            {% endfor %}
                            
                        </div>
                    </div>
                    
                    <div class="stream">
                        <p class="stream-title">{{ anime.title }}</p>
                        <video class="stream-video" controls preload="auto" src="{{ anime.episodes[0].download_link }}"></video>
                    </div>
                </div>
            </body>
        </html>
        """, anime=anime)