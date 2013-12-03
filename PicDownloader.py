#!/usr/bin/env python
#-*- coding: utf8 -*-
import BeautifulSoup,os,urllib2,urllib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class PicDownloader(object):
    def __init__(self,keyWord,counts,searchEngine=None,selfSearchEngine=None,path="."):
        """
        if the parameter selfSearchEngine not Null,use it as
        searchEngine ,and the "counts" defines how much pic to
        download
        """
        self.keyWord=keyWord
        self.__downloadedCounts=0
        self.__path=path
        if(selfSearchEngine!=None):
            self.searchEngine=selfSearchEngine
        else:
            self.searchEngine=searchEngine
        self.counts=counts


    def doSearch(self):
        """
        doSearch on internet ,and return a list of pic url list
        """

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
        self.getSearchUrl()
        self.baseReqData['word']=keyWord

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
        soup=BeautifulSoup.BeautifulSoup(html)
        print(soup)
        while True:
            div=soup.findNext('div')
            if(div==None):
                break
            print(div)
            if(div.attrMap.get('class',0)!=0):
                print(div.attrMap['class'])
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

if __name__=='__main__':

    engine=baiduEngine(u'树')
    print(engine.doSearch().read())
