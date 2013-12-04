#!/usr/bin/env python
#-*- coding: utf8 -*-
import BeautifulSoup,os,urllib2,urllib
import sys,re,threading,getopt
reload(sys)
sys.setdefaultencoding('utf8')

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
        self.matchImgSrc=re.compile('src=(\S+([jJ][Pp][gG]|[pP][nN][gG]))')
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
        urls=wantedDiv.findAll('a')
        for i in urls:
            self.__genAttrMap(i)
            imgUrls.append(self.matchImgSrc.search(i.attrMap['href']).groups()[0])
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

class picDownloader(object):
    def __init__(self,keyWord,counts,searchEngine=baiduEngine,path=".",maxThreads=10):
        """
        if the parameter selfSearchEngine not Null,use it as
        searchEngine ,and the "counts" defines how much pic to
        download
        """
        self.keyWord=keyWord
        self.downloadedCounts=0
        self.path=path
        self.maxThreads=maxThreads
        self.searchEngine=searchEngine
        self.counts=counts

    def startDownload(self):
        engine=self.searchEngine(self.keyWord)
        urlGenerator=engine.getImgUrl()
        if(not os.path.exists(self.path)):
            os.makedirs(self.path)
        i=1
        while(downloadThread.preDownloadedCounts!=self.counts+1):
            flag=True
            while flag:
                if(downloadThread.numOfThreads<=self.maxThreads):
                    imgurl=urlGenerator.next()
                    t=downloadThread(imgurl,self.path+os.sep+str(i)+self.getImgType(imgurl))
                    t.setDaemon(True)
                    t.start()
                    flag=False
            i+=1 
        while(downloadThread.preDownloadedCounts-downloadThread.downloadedCounts-1):
            imgurl=urlGenerator.next()
            t=downloadThread(imgurl,self.path+'/'+str(i)+self.getImgType(imgurl))
            t.setDaemon(True)
            t.start()
            t.join()
            i+=1

    def getImgType(self,imgurl):
        return imgurl[imgurl.rfind('.'):]



class downloadThread(threading.Thread):
    '''multi thread download'''
    numOfThreads=0
    downloadedCounts=0
    preDownloadedCounts=0

    def __init__(self,imgUrl,path): 
        '''imgUrl to download,path to write file(include filename)'''
        threading.Thread.__init__(self)
        self.imgUrl=imgUrl
        self.path=path

    def run(self):
        downloadThread.numOfThreads+=1
        downloadThread.preDownloadedCounts+=1
        try:
            fd=urllib2.urlopen(self.imgUrl)
        except:
            downloadThread.preDownloadedCounts-=1
            downloadThread.numOfThreads-=1
            sys.exit()
        print('downloading:'+str(self.imgUrl))
        if(os.path.exists(self.path)==False):
            fw=open(self.path,'w')
            data=fd.read(1024)
            while(len(data)!=0):
                fw.write(data)
                data=fd.read(1024)
        downloadThread.downloadedCounts+=1
        downloadThread.numOfThreads-=1


def Usage():
    '''picDownloader's usage'''
    print('Usage: -w keyword -c counts -p store path\nlike: picDownloader.py -w 树 -c 100 -p E:\Pic')


if __name__=='__main__':
    try:
        opts,args=getopt.getopt(sys.argv[1:],'hw:c:p:',['help'])
    except getopt.GetoptError as err:
        print(str(err))
        Usage()
        sys.exit(2)
    optDict=dict(i for i in opts)
    if(optDict.get('-w',0)==0 or optDict.get('-c',0)==0):
        print('You MUST specify the "-w keyword" and "-c counts" option')
        sys.exit(2)
    elif(optDict.get('-p',0)!=0): #has -p option
        d=picDownloader(optDict['-w'],optDict['-c'],path=optDict['-p'])
    else:
        d=picDownloader(optDict['-w'],optDict['-c'])
    d.startDownload()

