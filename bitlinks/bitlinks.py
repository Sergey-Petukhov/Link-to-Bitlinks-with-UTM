"""Web service for automatic processing of URLs and generating bitlinks.

The bottom line
    There is an Internet project: a website and 3 resources in social networks.
    The project team needs to post links to pages in social networks.

Problems:
    1) Source links are very long - 100-130 characters, they need to be shorten using a third-party service https://bitly.com/, using the project profile.

    2) For web analytics purposes, the original links should be changed by adding the necessary UTM tags (then it will be possible to determine from which social network the user made the transition).
    As a result, for one page of the site you need to create and simplify 3 different links.

    3) 95% of the original links contain other tags that require removal.

    4) A large team performs similar actions from a smartphone (NOT a hi-end model with small display) with a poor Internet connection and sometimes disabled JavaScript (https://bitly.com/ does not work).

    As a result, the processing of links for one page takes ~ 10 minutes.

Example:
    Original link: https://subdomain.domain.ru/category/page-name-some-id?from=somewhere

    It is necessary to remove "from = somewhere": https://subdomain.domain.ru/category/page-name-some-id?

    Create 3 links for social networks with the necessary UTM tags:
    https://subdomain.domain.ru/category/page-name-some-id?utm_source=telegram&utm_medium=social&utm_campaign=our-channel
    https://subdomain.domain.ru/category/page-name-some-id?utm_source=vk&utm_medium=social&utm_campaign=our-public
    https://subdomain.domain.ru/category/page-name-some-id?utm_source=instagram&utm_medium=social&utm_campaign=our-profile

    Shorting 3 different links using https://bitly.com/, using the project profile:
    http://bit.ly/2QgHMIE
    http://bit.ly/2Vl9gAB
    http://bit.ly/2QgjM8y

Service available here: http://35.156.199.247/bitlinks"""

from urllib.request import urlopen
import urllib.error
from multiprocessing.dummy import Pool as ThreadPool
from flask import Flask, request, make_response, jsonify
import bitly_api

app = Flask(__name__)


@app.route("/bitlinks")
def home():
    """Main screen (home page)
    Example available here: http://35.156.199.247/bitlinks
    Simple form with input for original link.
    Default form action (/bitlinks/go) for users with enabled JavaScript.
    Hidden submit with <noscript> tag for users with disabled JavaScript."""

    resp = make_response('''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Link to Bitlinks with UTM</title>
    <meta name="description" content="Web service for automatic processing of URLs and generating bitlinks.">
    <link rel="icon" type="image/png" href="/bitlinks/favicon.png">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style nonce="2726c7f26c">
        html {
            height: 100%;
            background: #092756
        }
        
        #feedback-page {
            text-align: center
        }
        
        #form-main {
            width: 100%;
            float: left;
            padding-top: 0
        }
        
        #form-div {
            background-color: rgba(72, 72, 72, .4);
            width: 450px;
            float: left;
            left: 50%;
            position: absolute;
            margin-top: 190px;
            margin-left: -260px;
            -moz-border-radius: 7px;
            -webkit-border-radius: 7px;
            padding: 35px 35px 50px
        }
        
        .feedback-input {
            color: #3c3c3c;
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 500;
            font-size: 18px;
            border-radius: 0;
            line-height: 22px;
            background-color: #fbfbfb;
            padding: 13px 13px 13px 54px;
            margin-bottom: 10px;
            width: 100%;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            -ms-box-sizing: border-box;
            box-sizing: border-box;
            border: 3px solid transparent
        }
        
        .feedback-input:focus {
            background: #fff;
            box-shadow: 0;
            border: 3px solid #3498db;
            color: #3498db;
            outline: 0;
            padding: 13px 13px 13px 54px
        }
        
        #instagram,
        #instagram:focus,
        #link,
        #link:focus,
        #telegram,
        #telegram:focus,
        #vk,
        #vk:focus {
            background-size: 30px 30px;
            background-position: 11px 8px;
            background-repeat: no-repeat
        }
        
        .focused {
            color: #30aed6;
            border: 3px solid #30aed6
        }
        
        textarea {
            width: 100%;
            height: 150px;
            line-height: 150%;
            resize: vertical
        }
        
        input:focus,
        input:hover,
        textarea:focus,
        textarea:hover {
            background-color: #fff
        }
        
        .btn {
            font-family: Montserrat, Arial, Helvetica, sans-serif;
            float: left;
            width: 100%;
            border: 4px solid #fbfbfb;
            cursor: pointer;
            background-color: #3498db;
            color: #fff;
            font-size: 24px;
            padding-top: 22px;
            padding-bottom: 22px;
            -webkit-appearance: none;
            -webkit-transition: all .3s;
            -moz-transition: all .3s;
            transition: all .3s;
            margin-top: -4px;
            font-weight: 700
        }
        
        .btn:hover {
            background-color: #fbfbfb;
            color: #0493bd
        }
        
        .submit:hover {
            color: #3498db
        }
        
        #button-blue-nojs {
            margin-top: 10px
        }
        
        @media only screen and (max-width:580px) {
            #form-div {
                left: 3%;
                margin-right: 3%;
                margin-top: 30px;
                width: 88%;
                margin-left: 0;
                padding-left: 3%;
                padding-right: 3%
            }
        }
    </style>
</head>

<body>
    <div id="form-main">
        <div id="form-div">
            <form class="form" id="form1" action="/bitlinks/go" method="GET">
                <p>
                    <input required name="url" type="url" class="feedback-input" placeholder="e.g. https://yandex.ru" id="link" /> </p>
                <div class="submit">
                    <input type="submit" value="Give Me Bitlinks" class="btn" id="button-blue" />
                    <noscript>
                        <input formaction="/bitlinks/nojs" type="submit" value="AND paranoid_mode = TRUE" class="btn" id="button-blue-nojs">
                    </noscript>
                </div>
            </form>
        </div>
    </div>
    <link rel="stylesheet" type="text/css" href="/bitlinks/styles.css">
</body>

</html>''')

    return resp

HTML_ESCAPE_TABLE = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Function for escaping characters to prevent XSS."""

    return "".join(HTML_ESCAPE_TABLE.get(c, c) for c in text)


@app.route("/bitlinks/go")
def bitlinks():
    """Function to display a page with bitlinks for users with enabled JavaScript.
    Example available here: http://35.156.199.247/bitlinks/go?url=https://yandex.ru/
    """

    url = html_escape(request.args.get('url', ''))

    #Search for the requested URL in the cache
    with open('/change-me/bitlinks/cache.txt') as in_stream:
        for line in in_stream:
            new_line = line.strip().split('\t')
            if new_line[0] == url:
                #If there is, generate a page without using Ajax, immediately filling out bilinks
                resp = make_response('''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Link to Bitlinks with UTM | ''' + url + '''</title>
    <meta name="description" content="Web service for automatic processing of URLs and generating bitlinks.">
    <link rel="icon" type="image/png" href="/bitlinks/favicon.png">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style nonce="2726c7f26c">
        html {
            height: 100%;
            background: #092756
        }
        
        #feedback-page {
            text-align: center
        }
        
        #form-main {
            width: 100%;
            float: left;
            padding-top: 0
        }
        
        #form-div {
            background-color: rgba(72, 72, 72, .4);
            width: 450px;
            float: left;
            left: 50%;
            position: absolute;
            margin-top: 140px;
            margin-left: -260px;
            -moz-border-radius: 7px;
            -webkit-border-radius: 7px;
            padding: 35px 35px 50px
        }
        
        .feedback-input {
            display: inline-block;
            color: #3c3c3c;
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 500;
            font-size: 18px;
            border-radius: 0;
            line-height: 22px;
            background-color: #fbfbfb;
            padding: 13px 13px 13px 54px;
            margin-bottom: 10px;
            width: 100%;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            -ms-box-sizing: border-box;
            box-sizing: border-box;
            border: 3px solid transparent
        }
        
        .feedback-input:focus {
            background: #fff;
            box-shadow: 0;
            border: 3px solid #3498db;
            color: #3498db;
            outline: 0;
            padding: 13px 13px 13px 54px
        }
        
        #instagram,
        #instagram:focus,
        #link,
        #link:focus,
        #telegram,
        #telegram:focus,
        #vk,
        #vk:focus {
            background-size: 30px 30px;
            background-position: 11px 8px;
            background-repeat: no-repeat
        }
        
        .focused {
            color: #30aed6;
            border: 3px solid #30aed6
        }
        
        textarea {
            width: 100%;
            height: 150px;
            line-height: 150%;
            resize: vertical
        }
        
        input:focus,
        input:hover,
        textarea:focus,
        textarea:hover {
            background-color: #fff
        }
        
        .btn {
            font-family: Montserrat, Arial, Helvetica, sans-serif;
            float: left;
            width: 100%;
            border: 4px solid #fbfbfb;
            cursor: pointer;
            background-color: #3498db;
            color: #fff;
            font-size: 24px;
            padding-top: 22px;
            padding-bottom: 22px;
            -webkit-appearance: none;
            -webkit-transition: all .3s;
            -moz-transition: all .3s;
            transition: all .3s;
            margin-top: -4px;
            font-weight: 700
        }
        
        .btn:hover {
            background-color: #fbfbfb;
            color: #0493bd
        }
        
        .submit:hover {
            color: #3498db
        }
        
        @media only screen and (max-width:580px) {
            #form-div {
                left: 3%;
                margin-right: 3%;
                margin-top: 0px;
                width: 88%;
                margin-left: 0;
                padding-left: 3%;
                padding-right: 3%
            }
        }
    </style>
</head>

<body>
    <div id="form-main">
        <div id="form-div">
            <p class="feedback-input" id="telegram">''' + new_line[1] + '''</p>
            <div class="submit">
                <button class="btn" id="button-telegram" data-clipboard-target="#telegram">Copy</button>
            </div>
            <p class="feedback-input" id="vk">''' + new_line[2] + '''</p>
            <div class="submit">
                <button class="btn" id="button-vk" data-clipboard-target="#vk">Copy</button>
            </div>
            <p class="feedback-input" id="instagram">''' + new_line[3] + '''</p>
            <div class="submit">
                <button class="btn" id="button-instagram" data-clipboard-target="#instagram">Copy</button>
            </div>
        </div>
    </div>
    <link rel="stylesheet" type="text/css" href="/bitlinks/styles.css">
    <script src="/bitlinks/clipboard.min.js"></script>
    <script nonce="2726c7f26c">
        new ClipboardJS('.btn');
    </script>
</body>

</html>''')

                return resp

    #If not, generate a page using Ajax and a temporary loader
    resp = make_response('''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Link to Bitlinks with UTM | ''' + url + '''</title>
    <meta name="description" content="Web service for automatic processing of URLs and generating bitlinks.">
    <link rel="icon" type="image/png" href="/bitlinks/favicon.png">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style nonce="2726c7f26c">
        html {
            height: 100%;
            background: #092756
        }
        
        #feedback-page {
            text-align: center
        }
        
        #form-main {
            width: 100%;
            float: left;
            padding-top: 0
        }
        
        #form-div {
            background-color: rgba(72, 72, 72, .4);
            width: 450px;
            float: left;
            left: 50%;
            position: absolute;
            margin-top: 140px;
            margin-left: -260px;
            -moz-border-radius: 7px;
            -webkit-border-radius: 7px;
            padding: 35px 35px 50px
        }
        
        .feedback-input {
            display: inline-block;
            color: #3c3c3c;
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 500;
            font-size: 18px;
            border-radius: 0;
            line-height: 22px;
            background-color: #fbfbfb;
            padding: 13px 13px 13px 54px;
            margin-bottom: 10px;
            width: 100%;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            -ms-box-sizing: border-box;
            box-sizing: border-box;
            border: 3px solid transparent
        }
        
        .feedback-input:focus {
            background: #fff;
            box-shadow: 0;
            border: 3px solid #3498db;
            color: #3498db;
            outline: 0;
            padding: 13px 13px 13px 54px
        }
        
        #instagram,
        #instagram:focus,
        #link,
        #link:focus,
        #telegram,
        #telegram:focus,
        #vk,
        #vk:focus {
            background-size: 30px 30px;
            background-position: 11px 8px;
            background-repeat: no-repeat
        }
        
        .focused {
            color: #30aed6;
            border: 3px solid #30aed6
        }
        
        textarea {
            width: 100%;
            height: 150px;
            line-height: 150%;
            resize: vertical
        }
        
        input:focus,
        input:hover,
        textarea:focus,
        textarea:hover {
            background-color: #fff
        }
        
        .btn {
            font-family: Montserrat, Arial, Helvetica, sans-serif;
            float: left;
            width: 100%;
            border: 4px solid #fbfbfb;
            cursor: pointer;
            background-color: #3498db;
            color: #fff;
            font-size: 24px;
            padding-top: 22px;
            padding-bottom: 22px;
            -webkit-appearance: none;
            -webkit-transition: all .3s;
            -moz-transition: all .3s;
            transition: all .3s;
            margin-top: -4px;
            font-weight: 700
        }
        
        .btn:hover {
            background-color: #fbfbfb;
            color: #0493bd
        }
        
        .submit:hover {
            color: #3498db
        }
        
        @media only screen and (max-width:580px) {
            #form-div {
                left: 3%;
                margin-right: 3%;
                margin-top: 0;
                width: 88%;
                margin-left: 0;
                padding-left: 3%;
                padding-right: 3%
            }
        }
    </style>
</head>

<body>
    <div id="form-main">
        <div id="form-div">
            <p class="feedback-input" id="telegram">
                <?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="105px" height="16px" viewBox="0 0 158 24" xml:space="preserve">
                        <rect x="0" y="0" width="100%" height="100%" fill="#FFFFFF" />
                        <path fill="#e9f4fb" d="M64 4h10v10H64V4zm20 0h10v10H84V4zm20 0h10v10h-10V4zm20 0h10v10h-10V4zm20 0h10v10h-10V4zM4 4h10v10H4V4zm20 0h10v10H24V4zm20 0h10v10H44V4z" />
                        <path fill="#cae4f6" d="M144 14V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10H84zm9-9h-8v8h8V5zm-29 9V4h10v10H64zm9-9h-8v8h8V5zm-29 9V4h10v10H44zm9-9h-8v8h8V5zm-29 9V4h10v10H24zm9-9h-8v8h8V5zM4 14V4h10v10H4zm9-9H5v8h8V5z" />
                        <g>
                            <path fill="#e1f0fa" d="M-58 16V2h14v14h-14zm13-13h-12v12h12V3z" />
                            <path fill="#b0d7f1" fill-opacity="0.3" d="M-40 0h18v18h-18z" />
                            <path fill="#c2e0f4" d="M-40 18V0h18v18h-18zm17-17h-16v16h16V1z" />
                            <path fill="#b0d7f1" fill-opacity="0.7" d="M-20 0h18v18h-18z" />
                            <path fill="#71b7e6" d="M-20 18V0h18v18h-18zM-3 1h-16v16h16V1z" />
                            <animateTransform attributeName="transform" type="translate" values="20 0;40 0;60 0;80 0;100 0;120 0;140 0;160 0;180 0;200 0" calcMode="discrete" dur="3200ms" repeatCount="indefinite" />
                        </g>
                    </svg>
            </p>
            <div class="submit">
                <button class="btn" id="button-telegram" data-clipboard-target="#telegram">Copy</button>
            </div>
            <p class="feedback-input" id="vk">
                <?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="105px" height="16px" viewBox="0 0 158 24" xml:space="preserve">
                        <rect x="0" y="0" width="100%" height="100%" fill="#FFFFFF" />
                        <path fill="#e9f4fb" d="M64 4h10v10H64V4zm20 0h10v10H84V4zm20 0h10v10h-10V4zm20 0h10v10h-10V4zm20 0h10v10h-10V4zM4 4h10v10H4V4zm20 0h10v10H24V4zm20 0h10v10H44V4z" />
                        <path fill="#cae4f6" d="M144 14V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10H84zm9-9h-8v8h8V5zm-29 9V4h10v10H64zm9-9h-8v8h8V5zm-29 9V4h10v10H44zm9-9h-8v8h8V5zm-29 9V4h10v10H24zm9-9h-8v8h8V5zM4 14V4h10v10H4zm9-9H5v8h8V5z" />
                        <g>
                            <path fill="#e1f0fa" d="M-58 16V2h14v14h-14zm13-13h-12v12h12V3z" />
                            <path fill="#b0d7f1" fill-opacity="0.3" d="M-40 0h18v18h-18z" />
                            <path fill="#c2e0f4" d="M-40 18V0h18v18h-18zm17-17h-16v16h16V1z" />
                            <path fill="#b0d7f1" fill-opacity="0.7" d="M-20 0h18v18h-18z" />
                            <path fill="#71b7e6" d="M-20 18V0h18v18h-18zM-3 1h-16v16h16V1z" />
                            <animateTransform attributeName="transform" type="translate" values="20 0;40 0;60 0;80 0;100 0;120 0;140 0;160 0;180 0;200 0" calcMode="discrete" dur="3200ms" repeatCount="indefinite" />
                        </g>
                    </svg>
            </p>
            <div class="submit">
                <button class="btn" id="button-vk" data-clipboard-target="#vk">Copy</button>
            </div>
            <p class="feedback-input" id="instagram">
                <?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="105px" height="16px" viewBox="0 0 158 24" xml:space="preserve">
                        <rect x="0" y="0" width="100%" height="100%" fill="#FFFFFF" />
                        <path fill="#e9f4fb" d="M64 4h10v10H64V4zm20 0h10v10H84V4zm20 0h10v10h-10V4zm20 0h10v10h-10V4zm20 0h10v10h-10V4zM4 4h10v10H4V4zm20 0h10v10H24V4zm20 0h10v10H44V4z" />
                        <path fill="#cae4f6" d="M144 14V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10h-10zm9-9h-8v8h8V5zm-29 9V4h10v10H84zm9-9h-8v8h8V5zm-29 9V4h10v10H64zm9-9h-8v8h8V5zm-29 9V4h10v10H44zm9-9h-8v8h8V5zm-29 9V4h10v10H24zm9-9h-8v8h8V5zM4 14V4h10v10H4zm9-9H5v8h8V5z" />
                        <g>
                            <path fill="#e1f0fa" d="M-58 16V2h14v14h-14zm13-13h-12v12h12V3z" />
                            <path fill="#b0d7f1" fill-opacity="0.3" d="M-40 0h18v18h-18z" />
                            <path fill="#c2e0f4" d="M-40 18V0h18v18h-18zm17-17h-16v16h16V1z" />
                            <path fill="#b0d7f1" fill-opacity="0.7" d="M-20 0h18v18h-18z" />
                            <path fill="#71b7e6" d="M-20 18V0h18v18h-18zM-3 1h-16v16h16V1z" />
                            <animateTransform attributeName="transform" type="translate" values="20 0;40 0;60 0;80 0;100 0;120 0;140 0;160 0;180 0;200 0" calcMode="discrete" dur="3200ms" repeatCount="indefinite" />
                        </g>
                    </svg>
            </p>
            <div class="submit">
                <button class="btn" id="button-instagram" data-clipboard-target="#instagram">Copy</button>
            </div>
        </div>
    </div>
    <link rel="stylesheet" type="text/css" href="/bitlinks/styles.css">
    <script src="/bitlinks/jquery.min.js"></script>
    <script src="/bitlinks/clipboard.min.js"></script>
    <script nonce="2726c7f26c">
        function get_bitlinks(t) {
            $.post("/bitlinks/ajax", {
                url: t
            }).done(function(t) {
                $(telegram).text(t.bitlink_telegram), $(vk).text(t.bitlink_vk), $(instagram).text(t.bitlink_instagram)
            }).fail(function() {
                $(telegram).text("Connection Error! Try: http://35.156.199.247/bitlinks/nojs?url=''' + url + '''"), $(vk).text("Connection Error! Try: http://35.156.199.247/bitlinks/nojs?url=''' + url + '''"), $(instagram).text("Connection Error! Try: http://35.156.199.247/bitlinks/nojs?url=''' + url + '''")
            })
        }
        new get_bitlinks("''' + url + '''"), new ClipboardJS(".btn");
    </script>
</body>

</html>''')

    return resp


@app.route("/bitlinks/ajax", methods=['POST'])
def ajax():
    """Function to wait for a response from https://bitly.com/ and refresh the page (/bitlinks/go) without reloading using Ajax."""

    url = request.form['url']

    #Search for the requested URL in the cache
    with open('/change-me/bitlinks/cache.txt') as in_stream:
        for line in in_stream:
            new_line = line.strip().split('\t')
            if new_line[0] == url:
                #If there is, generate a page without using https://bitly.com

                return jsonify({
                    'bitlink_telegram': new_line[1],
                    'bitlink_vk': new_line[2],
                    'bitlink_instagram': new_line[3],
                })

    your_website = 'your-website-address'
    clean_url, lenght, status_code = None, len(your_website), None

    #Getting the response code of the requested page
    try:
        status_code = urllib.request.urlopen(url).getcode()
    except:
        status_code = 0

    #Checking that the user has requested an existing page of an allowed website
    if url[:lenght] != your_website or status_code != 200:

        return jsonify({
            'bitlink_telegram': 'Bad URL or HTTP / Connection Error',
            'bitlink_vk': 'Only correct documents (SATUS_CODE == 200 OK; NOT https://site.ru/123456) from %our_website% are allowed.',
            'bitlink_instagram': ':(',
        })

    #If the URL is correct, clear it of unnecessary tags
    elif '?from=' in url or '&from=' in url:
        clean_url = url[:url.find('from=')]

    elif '?' not in url:
        clean_url = url + '?'

    elif '?utm_' in url or '&utm_' in url:
        clean_url = url[:url.find('utm_')]

    elif '?_openstat=' in url or '&_openstat=' in url:
        clean_url = url[:url.find('_openstat=')]

    else:
        clean_url = url + '&'

    #Create URL`s with the necessary UTM tags for 3 social networks
    urls = [
        clean_url + 'utm_source=telegram&utm_medium=social&utm_campaign=our-channel',
        clean_url + 'utm_source=vk&utm_medium=social&utm_campaign=our-public',
        clean_url + 'utm_source=instagram&utm_medium=social&utm_campaign=our-profile',
    ]

    #Connect to the bitly by API
    bitly = bitly_api.Connection(access_token='your-bitly-token')

    #In parallel, run the function of shorten links using threads (multiprocessing.dummy)
    pool = ThreadPool(3)

    results = pool.map(bitly.shorten, urls)

    pool.close()
    pool.join()

    #Response from the bilty - is dictionary, assigned to the variabled obtained short links
    bitlink_telegram, bitlink_vk, bitlink_instagram = results[0]['url'], results[1]['url'], results[2]['url']

    #Write the data to the cache
    with open('/change-me/bitlinks/cache.txt', 'a') as out_stream:
        out_stream.write('\n' + url + '\t' + bitlink_telegram + '\t' + bitlink_vk + '\t' + bitlink_instagram)

    return jsonify({
        'bitlink_telegram': bitlink_telegram,
        'bitlink_vk': bitlink_vk,
        'bitlink_instagram': bitlink_instagram,
    })


@app.route("/bitlinks/nojs")
def nojs():
    """Function to display a page with bitlinks for users with disabled JavaScript.
    Example available here: http://35.156.199.247/bitlinks/nojs?url=https://yandex.ru/
    """

    url = html_escape(request.args.get('url', ''))

    with open('/change-me/bitlinks/cache.txt') as in_stream:
        for line in in_stream:
            new_line = line.strip().split('\t')
            if new_line[0] == url:
                resp = make_response('''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Link to Bitlinks with UTM | ''' + url + '''</title>
    <meta name="description" content="Web service for automatic processing of URLs and generating bitlinks.">
    <link rel="icon" type="image/png" href="/bitlinks/favicon.png">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style nonce="2726c7f26c">
        html {
            height: 100%;
            background: #092756
        }
        
        #feedback-page {
            text-align: center
        }
        
        #form-main {
            width: 100%;
            float: left;
            padding-top: 0
        }
        
        #form-div {
            background-color: rgba(72, 72, 72, .4);
            width: 450px;
            float: left;
            left: 50%;
            position: absolute;
            margin-top: 140px;
            margin-left: -260px;
            -moz-border-radius: 7px;
            -webkit-border-radius: 7px;
            padding: 35px 35px 50px
        }
        
        .feedback-input {
            display: inline-block;
            color: #3c3c3c;
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 500;
            font-size: 18px;
            border-radius: 0;
            line-height: 22px;
            background-color: #fbfbfb;
            padding: 13px 13px 13px 54px;
            margin-bottom: 10px;
            width: 100%;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            -ms-box-sizing: border-box;
            box-sizing: border-box;
            border: 3px solid transparent
        }
        
        .feedback-input:focus {
            background: #fff;
            box-shadow: 0;
            border: 3px solid #3498db;
            color: #3498db;
            outline: 0;
            padding: 13px 13px 13px 54px
        }
        
        #instagram,
        #instagram:focus,
        #link,
        #link:focus,
        #telegram,
        #telegram:focus,
        #vk,
        #vk:focus {
            background-size: 30px 30px;
            background-position: 11px 8px;
            background-repeat: no-repeat
        }
        
        .focused {
            color: #30aed6;
            border: 3px solid #30aed6
        }
        
        textarea {
            width: 100%;
            height: 150px;
            line-height: 150%;
            resize: vertical
        }
        
        input:focus,
        input:hover,
        textarea:focus,
        textarea:hover {
            background-color: #fff
        }
        
        .btn {
            font-family: Montserrat, Arial, Helvetica, sans-serif;
            float: left;
            width: 100%;
            border: 4px solid #fbfbfb;
            cursor: pointer;
            background-color: #3498db;
            color: #fff;
            font-size: 24px;
            padding-top: 22px;
            padding-bottom: 22px;
            -webkit-appearance: none;
            -webkit-transition: all .3s;
            -moz-transition: all .3s;
            transition: all .3s;
            margin-top: -4px;
            font-weight: 700
        }
        
        .btn:hover {
            background-color: #fbfbfb;
            color: #0493bd
        }
        
        .submit:hover {
            color: #3498db
        }
        
        @media only screen and (max-width:580px) {
            #form-div {
                left: 3%;
                margin-right: 3%;
                margin-top: 0;
                width: 88%;
                margin-left: 0;
                padding-left: 3%;
                padding-right: 3%
            }
        }
    </style>
</head>

<body>
    <div id="form-main">
        <div id="form-div">
            <p class="feedback-input" id="telegram">''' + new_line[1] + '''</p>
            <p class="feedback-input" id="vk">''' + new_line[2] + '''</p>
            <p class="feedback-input" id="instagram">''' + new_line[3] + '''</p>
        </div>
    </div>
    <link rel="stylesheet" type="text/css" href="/bitlinks/styles.css">
</body>

</html>''')

                return resp

    your_website = 'your-website-address'
    clean_url, lenght, status_code = None, len(your_website), None

    try:
        status_code = urllib.request.urlopen(url).getcode()
    except:
        status_code = 0

    if url[:lenght] != your_website or status_code != 200:
        resp = make_response('''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Bad URL or HTTP / Connection Error | ''' + url + '''</title>
</head>

<body>
    <h1>Bad URL or HTTP / Connection Error</h1>
    <p>Only <u>correct documents</u> (SATUS_CODE==<strong>200 OK</strong>; <u>NOT</u> https://site.ru/123456) from %our_website% are allowed.</p>
</body>

</html>''')

        return resp

    elif '?from=' in url or '&from=' in url:
        clean_url = url[:url.find('from=')]

    elif '?' not in url:
        clean_url = url + '?'

    elif '?utm_' in url or '&utm_' in url:
        clean_url = url[:url.find('utm_')]

    elif '?_openstat=' in url or '&_openstat=' in url:
        clean_url = url[:url.find('_openstat=')]

    else:
        clean_url = url + '&'

    urls = [
        clean_url + 'utm_source=telegram&utm_medium=social&utm_campaign=our-channel',
        clean_url + 'utm_source=vk&utm_medium=social&utm_campaign=our-public',
        clean_url + 'utm_source=instagram&utm_medium=social&utm_campaign=our-profile',
    ]

    bitly = bitly_api.Connection(access_token='your-bitly-token')

    pool = ThreadPool(3)

    results = pool.map(bitly.shorten, urls)

    pool.close()
    pool.join()

    bitlink_telegram, bitlink_vk, bitlink_instagram = results[0]['url'], results[1]['url'], results[2]['url']

    resp = make_response('''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Link to Bitlinks with UTM | ''' + url + '''</title>
    <meta name="description" content="Web service for automatic processing of URLs and generating bitlinks.">
    <link rel="icon" type="image/png" href="/bitlinks/favicon.png">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style nonce="2726c7f26c">
        html {
            height: 100%;
            background: #092756
        }
        
        #feedback-page {
            text-align: center
        }
        
        #form-main {
            width: 100%;
            float: left;
            padding-top: 0
        }
        
        #form-div {
            background-color: rgba(72, 72, 72, .4);
            width: 450px;
            float: left;
            left: 50%;
            position: absolute;
            margin-top: 140px;
            margin-left: -260px;
            -moz-border-radius: 7px;
            -webkit-border-radius: 7px;
            padding: 35px 35px 50px
        }
        
        .feedback-input {
            display: inline-block;
            color: #3c3c3c;
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 500;
            font-size: 18px;
            border-radius: 0;
            line-height: 22px;
            background-color: #fbfbfb;
            padding: 13px 13px 13px 54px;
            margin-bottom: 10px;
            width: 100%;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            -ms-box-sizing: border-box;
            box-sizing: border-box;
            border: 3px solid transparent
        }
        
        .feedback-input:focus {
            background: #fff;
            box-shadow: 0;
            border: 3px solid #3498db;
            color: #3498db;
            outline: 0;
            padding: 13px 13px 13px 54px
        }
        
        #instagram,
        #instagram:focus,
        #link,
        #link:focus,
        #telegram,
        #telegram:focus,
        #vk,
        #vk:focus {
            background-size: 30px 30px;
            background-position: 11px 8px;
            background-repeat: no-repeat
        }
        
        .focused {
            color: #30aed6;
            border: 3px solid #30aed6
        }
        
        textarea {
            width: 100%;
            height: 150px;
            line-height: 150%;
            resize: vertical
        }
        
        input:focus,
        input:hover,
        textarea:focus,
        textarea:hover {
            background-color: #fff
        }
        
        .btn {
            font-family: Montserrat, Arial, Helvetica, sans-serif;
            float: left;
            width: 100%;
            border: 4px solid #fbfbfb;
            cursor: pointer;
            background-color: #3498db;
            color: #fff;
            font-size: 24px;
            padding-top: 22px;
            padding-bottom: 22px;
            -webkit-appearance: none;
            -webkit-transition: all .3s;
            -moz-transition: all .3s;
            transition: all .3s;
            margin-top: -4px;
            font-weight: 700
        }
        
        .btn:hover {
            background-color: #fbfbfb;
            color: #0493bd
        }
        
        .submit:hover {
            color: #3498db
        }
        
        @media only screen and (max-width:580px) {
            #form-div {
                left: 3%;
                margin-right: 3%;
                margin-top: 0;
                width: 88%;
                margin-left: 0;
                padding-left: 3%;
                padding-right: 3%
            }
        }
    </style>
</head>

<body>
    <div id="form-main">
        <div id="form-div">
            <p class="feedback-input" id="telegram">''' + bitlink_telegram + '''</p>
            <p class="feedback-input" id="vk">''' + bitlink_vk + '''</p>
            <p class="feedback-input" id="instagram">''' + bitlink_instagram + '''</p>
        </div>
    </div>
    <link rel="stylesheet" type="text/css" href="/bitlinks/styles.css">
</body>

</html>''')

    with open('/change-me/bitlinks/cache.txt', 'a') as out_stream:
        out_stream.write('\n' + url + '\t' + bitlink_telegram + '\t' + bitlink_vk + '\t' + bitlink_instagram)

    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0')
