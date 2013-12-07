#!/usr/bin/env python
#-*-coding: utf8 -*-
import BeautifulSoup,urllib2,re,urllib

class baseSearchEngine(object):
    """define some API for each searchEngine"""

    def __init__(self,keyWord):
        self.keyWord=keyWord

    def doSearch(self):
        '''return a result html fd'''
        pass
    def getImgUrl(self):
        '''return a wanted image url'''
        pass
    def getConstructor(self):
        '''return a constructor that can return a img url 
        every time'''
        pass

class baiduEngine(baseSearchEngine):
    '''baidu pic search engine'''

    def __init__(self,keyWord):
        baseSearchEngine.__init__(self,keyWord)
        self.getSearchUrl() #gen self.url and self.baseReqData
        self.host='wap.baidu.com'
        self.baseReqData['word']=keyWord
        self.matchImgSrc=re.compile('src=(\S+([jJ][Pp][gG]|[pP][nN][gG]|[gG][iI][fF]))')
        self.IMGDIVCLASS='mt ct b'
        self.NEXTPAGEDIVCLASS='wm lh pr'

    def doSearch(self):
        '''return fd relate to search'''
        url=self.url+'?'+urllib.urlencode(self.baseReqData)
        print url
        try:
            self.resultFd=urllib2.urlopen(url)
        except :
            print("url open error")
        return self.resultFd

    def getImgUrl(self):
        '''retun a img url every time called'''
        self.doSearch()
        html=self.resultFd.read()
        while True:
            onePageUrls,nextPageUrl=self.getOnePagePicUrl(html)
            for i in xrange(len(onePageUrls)):
                yield onePageUrls[i]
            html=urllib2.urlopen(nextPageUrl).read()
        

    def getOnePagePicUrl(self,page):
        '''get all needed pic urls on one page
        the 'given' page is a string of webpage
        return imgUrls list that contain imgurls
        and nextPages url
        '''
        imgUrls=[]
        nextPageUrl=None
        soup=BeautifulSoup.BeautifulSoup(page)
        wantedDiv=None
        while (wantedDiv==None):
                divs=soup.findAll('div')
                for i in divs:
                    self.__genAttrMap(i)
                    iClass=i.attrMap.get('class',0)
                    if(iClass==self.IMGDIVCLASS):
                        wantedDiv=i
                    elif(iClass==self.NEXTPAGEDIVCLASS):
                        aUrls=i.findAll('a')
                        for aUrl in aUrls:
                            if(aUrl.getText()==u'下一页'):
                                nextPageUrl='http://'+self.host+'/'+aUrl['href']
                    else:
                       del i
        urls=None
        while(urls==None):
            urls=wantedDiv.findAll('a')
        for i in urls:
            self.__genAttrMap(i)
            imgUrlmatch=self.matchImgSrc.search(i.attrMap['href'])
            if(imgUrlmatch!=None):
                imgUrls.append(imgUrlmatch.groups()[0])
        return imgUrls,nextPageUrl

    def getSearchUrl(self):
        '''generate self.url and self.baseReqData'''

        hostUrl='http://wap.baidu.com/img'
        try:
            html=urllib2.urlopen(hostUrl).read()
        except:
            print('searchUrl open error')
        soup=BeautifulSoup.BeautifulSoup(html)
        form=soup.find('form')
        self.__genAttrMap(form)
        self.url='http://wap.baidu.com/'+form.attrMap['action']
        inputSegs=form.findAll('input')
        for i in inputSegs:
            i.attrMap=dict(j for j in i.attrs)
        self.baseReqData=dict((i.attrMap.get('name'),i.attrMap.get('value',0)) for i in inputSegs)

    def __genAttrMap(self,soup):
        soup.attrMap=dict(i for i in soup.attrs)
