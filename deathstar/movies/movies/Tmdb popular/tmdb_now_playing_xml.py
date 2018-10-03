import requests, re
from BeautifulSoup import BeautifulSoup

site = "https://www.themoviedb.org/movie/now-playing?language=en"
# Set Max Amount Of Pages You Want It To Go Thru
maxPages = 20

# Get The Source Code.
def getSource(theURL):
        try:
                # Try To Pull Source And If Successful Return It
                html = requests.get(theURL,timeout=20).text
                return html
        except:
                # If It Cant Get Source Return The Boolean False... Alternatively We Could Return ""
                return False

# Opens And Closes The File
def openFile():
        # We Are Opening It And Starting The Next Function Passing The f Object
        f = open('now_playing_tmdb.xml','w')
        tmdbPull(f)


# Regex The Stuff. if theURL Is Not Defined When Being Called It Will Default to False
def tmdbPull(f,theURL=False):
        # Check If theURL is False If It IS Use The site Variable
        if not theURL:
                html = getSource(site)
        else:
                html = getSource(theURL)

        # One Way To Check If Grabbing The Source Failed
        if html != False:
                match1 = re.compile('<div class="image_content.+?id="movie_(.+?)".+?title="(.+?)".+?1x,(.+?) 2x.+?glyphicons-calendar x1"></span>  (.+?)</span>',re.DOTALL).findall(html)

                for id,name,icon,year in match1:
                        name = name.replace("&#x27;", "-")
                        html2 = getSource('http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=all' %(name))

                        # One Way To Check If Grabbing The Source Failed
                        if html2:
                                match2 = re.compile('<td class="primary_photo">.+?/title/(.+?)/',re.DOTALL).findall(html2)

                                # Check That The Regex Has More Than 0 Objects In It.
                                if len(match2) != 0:
                                        imdb = match2[0] # We Check Because If The Regex Didnt Grab Anything This Would Error
                                        html3 = getSource('https://www.themoviedb.org/movie/%s-%s/images/backdrops' %(id,name))

                                        # Again check That The Source Was Grabbed
                                        if html3:
                                                match3 = re.compile('<div class="image_content">.+?href="(.+?)"',re.DOTALL).findall(html3)

                                                # Make Sure That the Regex Was Successful
                                                if match3:
                                                        fanart = match3[0]

                                                        #print('<item>\n\t<title>%s</title>\n\t<meta>\n\t\t<content>movie</content>\n\t\t<imdb>%s</imdb>\n\t\t<title>%s</title>\n\t\t<year>%s</year>\n\t</meta>\n\t<link>\n\t\t<sublink></sublink>\n\t\t<sublink>search</sublink>\n\t\t<sublink>searchsd</sublink>\n\t</link>\n\t<animated_thumbnail></animated_thumbnail>\n\t<thumbnail>%s</thumbnail>\n\t<animated_fanart></animated_fanart>\n\t<fanart>%s</fanart>\n</item>\n' %(name,imdb,name,year,icon,fanart))

                                                        # For The Sake Of Simplicity (Reading And Editing) We Will Write It Like This
                                                        f.write('<item>\n')
                                                        f.write('\t<title>%s</title>\n' % name)
                                                        f.write('\t<meta>\n')
                                                        f.write('\t\t<content>movie</content>\n')
                                                        f.write('\t\t<imdb>%s</imdb>\n' % imdb)
                                                        f.write('\t\t<title>%s</title>\n' % name)
                                                        f.write('\t\t<year>%s</year>\n' % year)
                                                        f.write('\t</meta>\n')
                                                        f.write('\t<link>\n')
                                                        f.write('\t\t<sublink></sublink>\n')
                                                        f.write('\t\t<sublink>search</sublink>\n')
                                                        f.write('\t\t<sublink>searchsd</sublink>\n')
                                                        f.write('\t</link>\n')
                                                        f.write('\t<thumbnail>%s</thumbnail>\n' % icon)
                                                        f.write('\t<fanart>%s</fanart>\n' % fanart)
                                                        f.write('</item>\n')

                # For Loop Is Done Now Regex the Pages
                regex = r'<p class="left">Currently on page: ([^ ]*) of ([^ ]*) <span class="total_results.+?">'
                match = re.compile(regex).findall(html)

                # Check match sitn Empty
                if match:

                        # Check That Regex Has Two Values
                        if len(match[0]) == 2:

                                # Check That The Current Page Is Not The Last Page
                                if int(match[0][0]) < int(match[0][1]):

                                        # Check The Max Amount Of Pages To Go Thru
                                        if int(match[0][0]) < maxPages:
                                                # Make Next Page URL
                                                url = site+"?page="+str(int(match[0][0]) + 1)
                                                # Start Scraping Again Passing The File Object=f & The New URL
                                                tmdbPull(f,url)
                                        else:
                                                # Reached Max Pages So Close File And Quit Script
                                                f.close()
                                                quit()

                                else:
                                        # Theres No More Results And We Havent Reached The Max Pages SO Close And Quit
                                        f.close()
                                        quit()

                        # Back Up Way To Pull Next Page
                        else:
                                regex = r'<p class="right pagination"><a href="(/movie/now-playing\?page=[1-9]*&language=en)"><span'
                                match = re.compile(regex).findall(html)

                                # Check its Not Empty
                                if match:
                                        # Get current Page And Check Against Max Pages
                                        thisPage = int(match[0][-1])

                                        if thisPage <= maxPages:
                                                # Create New URL
                                                URL = site+str(match[0].split("=")[0])+"="+str(thisPage)
                                                tmdbPull(f,URL)

                                        else:
                                                f.close()
                                                quit()

                                else:
                                        f.close()
                                        quit()

                else:
                        # Couldnt Pull The Number Of Pages From Source So Do Whatever You Want
                        # I'll Just Put Closing And Quit
                        f.close()
                        quit()



openFile()
