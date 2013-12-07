#!/usr/bin/env python
#-*- coding: utf8 -*-
import BeautifulSoup,os,urllib2,urllib
import sys,re,threading,getopt
from baidu import *
reload(sys)
sys.setdefaultencoding('utf8')


class picDownloader(object):
    def __init__(self,keyWord,counts,path=".",searchEngine=baiduEngine,maxThreads=10):
        """
        if the parameter selfSearchEngine not Null,use it as
        searchEngine ,and the "counts" defines how much pic to
        download
        """
        self.keyWord=keyWord
        self.downloadedCounts=0
        self.path=path
        self.maxThreads=min(maxThreads,counts)
        self.searchEngine=searchEngine
        self.counts=counts

    def startDownload(self):
        engine=self.searchEngine(self.keyWord)
        urlGenerator=engine.getImgUrl()
        if(not os.path.exists(self.path)):
            os.makedirs(self.path)
        threadList=list()
        name=1
        for j in range(self.maxThreads):
            imgurl=urlGenerator.next()
            t=downloadThread(imgurl,self.path+os.sep+str(name)+self.getImgType(imgurl))
            name+=1
            threadList.append(t)
        for j in threadList:
            j.start()
        while(downloadThread.downloadedCounts<self.counts): #download not finished
            while(downloadThread.preDownloadedCounts<self.counts):       #download thread not full
                if(downloadThread.numOfThreads<self.maxThreads):
                    imgurl=urlGenerator.next()
                    t=downloadThread(imgurl,self.path+os.sep+str(name)+self.getImgType(imgurl))
                    name+=1
                    t.start()
        while(downloadThread.numOfThreads!=0):pass #wait until all download thread finished

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
        self.setDaemon(True)
        downloadThread.numOfThreads+=1
        downloadThread.preDownloadedCounts+=1

    def run(self):
        try:
            fd=urllib2.urlopen(self.imgUrl,timeout=10) #add timeout 
        except:
            downloadThread.preDownloadedCounts-=1
            downloadThread.numOfThreads-=1
            sys.exit()
        print('downloading:'+str(self.imgUrl))
        if(os.path.exists(self.path)==False):
            fw=open(self.path,'wb')
            data=self.safeRead(fd,fw)
            while(len(data)!=0):
                fw.write(data)
                data=self.safeRead(fd,fw)
	    fw.close()
        downloadThread.downloadedCounts+=1
        downloadThread.numOfThreads-=1

    def safeRead(self,fd,fw):
        '''handle the timeout exception'''
        try:
            data=fd.read(1024)
        except urllib2.URLError as e:
            downloadThread.preDownloadedCounts-=1
            downloadThread.numOfThreads-=1
            fd.close()
            fw.close()
            os.remove(self.path)
            sys.exit()
        return data


def Usage():
    '''picDownloader's usage'''
    print('Usage: -w keyword -c counts -p store path\nlike: picDownloader.py -w "small cat" -c 100 -p E:\Pic')


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
	Usage()
        sys.exit(2)
    elif(optDict.get('-p',0)!=0): #has -p option
        d=picDownloader(optDict['-w'],int(optDict['-c']),path=optDict['-p'])
    else:
        d=picDownloader(optDict['-w'],int(optDict['-c']))
    d.startDownload()

