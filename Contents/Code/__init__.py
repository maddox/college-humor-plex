import re, datetime
from PMS import Plugin, Log, DB, Thread, XML, HTTP, JSON, RSS, Utils
from PMS.MediaXML import MediaContainer, DirectoryItem, SearchDirectoryItem, VideoItem
from PMS.Shorthand import _L, _R, _E, _D

PF_PLUGIN_PREFIX   = "/video/college_humor"
PF_ROOT            = "http://www.collegehumor.com"
PF_RECENT          = "/originals/recent"
PF_VIEWED          = "/originals/most-viewed"
PF_LIKED           = "/originals/most-liked"
PF_PLAYLIST        = "/moogaloop"

PF_ALT_ROOT        = "http://pitchfork.tv"
PF_VIDEO_HOST      = "http://video.pitchfork.tv/"
CACHE_INTERVAL     = 3600
PF_NAMESPACE       = {'p':'http://xspf.org/ns/0/'}




####################################################################################################
def Start():
  Plugin.AddRequestHandler(PF_PLUGIN_PREFIX, HandleVideosRequest, "College Humor", "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup("Details", viewMode="InfoList", contentType="items")
####################################################################################################

def GetFlvUrl(video_path):
  playlist_xml = XML.ElementFromString(HTTP.GetCached(PF_ROOT + PF_PLAYLIST + '/' + video_path, CACHE_INTERVAL), True)
  
  try: flv_url = playlist_xml.xpath("video/file")[0].text_content()
  except: flv_url = ''
  Log.Add(flv_url)
  return flv_url

def AddVideos(site, dir, path, parentSectionID = ''):
  xmlFile = None
  
  for div in site.xpath(path):
  
    # Get XML file.
    # if xmlFile is None:
    #   xmlFile = GetXmlFile(div)
  
    #title
    try: title = div.xpath("div[@class='linked_details']/strong[@class='title']")[0].text_content().strip()
    except: title = ''

    #Summary
    try: summary = div.xpath("div[@class='linked_details']/p")[0].text_content().strip()
    except: summary = ''

    #Image
    try: thumb = div.xpath("a/img[@class='media_thumb']")[0].get('src')
    except: thumb = ''

    #Video url
    try: video_path = div.xpath("a[@class='video_link']")[0].get('href')
    except: video_path = ''
    
    # d = DirectoryItem(PF_PLUGIN_PREFIX+'/play'+video_path, title, thumb, summary)
    d = VideoItem(GetFlvUrl(video_path), title, summary, '', thumb)
    dir.AppendItem(d)
    
    

####################################################################################################
def HandleVideosRequest(pathNouns, count):
  dir = MediaContainer("art-default.jpg", None, "College Humor")
  dir.SetAttr("content", "items")
  
  
  Log.Add("Count: " + str(count))
  Log.Add("pathNouns: " + str(pathNouns))
  
  show_matcher = re.compile("^show")
  play_matcher = re.compile("^play")

  # Top level menu.
  if count == 0:
    dir.AppendItem(DirectoryItem("shows", "Shows"))
    dir.AppendItem(DirectoryItem("recent", "Recently Added"))
    dir.AppendItem(DirectoryItem("most_viewed", "Most Viewed"))
    dir.AppendItem(DirectoryItem("most_liked", "Most Liked"))
  elif count == 1 and pathNouns[0] == 'shows':
    dir = MediaContainer("art-default.jpg", 'Details', "College Humor", pathNouns[0])

    dir.AppendItem(DirectoryItem("prank_wars", "Prank Wars", Plugin.ExposedResourcePath("icon-prank-wars.png"), 'The epic battle of Streeter Vs. Amir'))
    dir.AppendItem(DirectoryItem("show$hardly_working", "Hardly Working", Plugin.ExposedResourcePath("icon-hardly-working.png")))
    dir.AppendItem(DirectoryItem("show$jake_and_amir", "Jake & Amir", Plugin.ExposedResourcePath("icon-jake-amir.png"), 'BFFS. No were not.'))
    dir.AppendItem(DirectoryItem("show$bleep_bloop", "Bleep Bloop", Plugin.ExposedResourcePath("icon-bleep-bloop.png"), 'The videogames talk show hosted by Jeff Rubin.'))
    dir.AppendItem(DirectoryItem("show$street_fighter_the_later_years", "Street Fighter: The Later Years", Plugin.ExposedResourcePath("icon-street-fighter.png")))
    dir.AppendItem(DirectoryItem("show$michael_showalter", "The Michael Showalter Showalter", Plugin.ExposedResourcePath("icon-showalter.png")))
  elif count == 1 and pathNouns[0] == 'recent':
    dir = MediaContainer("art-default.jpg", 'Details', "College Humor", pathNouns[0])
    site = XML.ElementFromString(HTTP.GetCached(PF_ROOT + PF_RECENT, CACHE_INTERVAL), True)
    AddVideos(site, dir, "//div[@id='tab_content_0']/ul[@class='media_list cfx']/li[@class='video']")
  elif count == 1 and pathNouns[0] == 'most_viewed':
    dir = MediaContainer("art-default.jpg", 'Details', "College Humor", pathNouns[0])
    site = XML.ElementFromString(HTTP.GetCached(PF_ROOT + PF_VIEWED, CACHE_INTERVAL), True)
    AddVideos(site, dir, "//div[@id='tab_content_1']/ul[@class='media_list cfx']/li[@class='video']")
  elif count == 1 and pathNouns[0] == 'most_liked':
    dir = MediaContainer("art-default.jpg", 'Details', "College Humor", pathNouns[0])
    site = XML.ElementFromString(HTTP.GetCached(PF_ROOT + PF_LIKED, CACHE_INTERVAL), True)
    AddVideos(site, dir, "//div[@id='tab_content_2']/ul[@class='media_list cfx']/li[@class='video']")
  elif count == 2 and pathNouns[1] == 'prank_wars':
    title = pathNouns[1].replace('_', ' ')
    dir = MediaContainer("art-default.jpg", 'Details', "College Humor", title)
    site = XML.ElementFromString(HTTP.GetCached(PF_ROOT + "/tag:prank-war/videos", CACHE_INTERVAL), True)
    AddVideos(site, dir, "//div[@id='tags_listing'][@class='video listing']/ul[@class='media_list cfx']/li[@class='video']")
  elif count == 2 and show_matcher.match(pathNouns[1]):
    title = pathNouns[1].split('$')[1].replace('_', ' ')
    Log.Add(title)
    tag = title.replace(' ', '')
    dir = MediaContainer("art-default.jpg", 'Details', "College Humor", title)
    site = XML.ElementFromString(HTTP.GetCached(PF_ROOT + "/tag:" + tag, CACHE_INTERVAL), True)
    AddVideos(site, dir, "//div[@id='tags_listing'][@class='all listing']/ul[@class='media_list cfx']/li[@class='video']")
  # elif pathNouns[0] == 'play':
  #   title = pathNouns[1].replace('_', ' ')
  #   Log.Add(title)
  #   tag = title.replace(' ', '')
  #   dir = MediaContainer("art-default.jpg", 'Details', "College Humor", title)
  # 
  #   d = VideoItem(GetFlvUrl(pathNouns[1]), 'Play', '', '', '')
  #   dir.AppendItem(d)



  Plugin.Dict["CacheWorkaround"] = datetime.datetime.now()
  return dir.ToXML()
