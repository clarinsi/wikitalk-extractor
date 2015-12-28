#!/usr/bin/python
#-*-coding:utf8-*-
# Usage: ./extract_talk.py [ispagetalk|isusertalk] < in > out
# page talk <page><ns>1</ns></page>
# user talk <page><ns>3</ns></page>

import langid
import sys
import re
from lxml import etree

try:
    lang=sys.argv[2]
except:
    lang='sr'

lexicon={'sl':
        {'user_tag':'Uporabnik'},
        'hr':
        {'user_tag':'Suradnik'},
        'sr':
        {'user_tag':u'Корисник'}
        }

xmlroot=etree.Element('wikipedia',id="janes.wikipedia."+sys.argv[1])

text_re=re.compile(r'<text xml:space="preserve">(.+?)</text>',re.DOTALL)
title_re=re.compile(r'<title>(.+?)</title>')
smiley_re=re.compile(r'\{\{s(.+?)\}\}')
doublepar_re=re.compile(r'\{\{.+?\}\}',re.DOTALL)
div_re=re.compile(r'&lt;div.+&lt;/div&gt;',re.DOTALL)
ispage=False
ispagetalk=False
isusertalk=False
if sys.argv[1] not in ['pagetalk','usertalk']:
    sys.stderr.write('Wrong first argument (pagetalk|usertalk)\n')
    sys.exit(1)
articleid=0
for line in sys.stdin:
    if line.strip()=='<page>':
        ispage=True
        page=''
    elif line.strip()=='</page>':
        if eval('is'+sys.argv[1]):
            page=div_re.sub(' ',page.decode('utf8'))
            currenttopic=None
            pattern=text_re.search(page)
            if pattern:
                articleid+=1
                topicid=0
                title=title_re.search(page).group(1)
                xmlpage=etree.Element('page',id='janes.wikipedia.'+sys.argv[1]+'.'+str(articleid).zfill(8),title=title,url='https://'+lang+'.wikipedia.org/wiki/'+title.replace(' ','_'))
                xmlroot.append(xmlpage)
                text=pattern.group(1)
                text=doublepar_re.sub('',smiley_re.sub(r'<smiley type="\1"/>',text))
                pars=[]
                for line in text.split('\n'):
                    line=line.strip().lstrip('*:# ')
                    user_re=re.compile(r'\[\['+lexicon[lang]['user_tag']+':([^\]]+?)\|([^\]]+?)\]\]')#[[Uporabnik:Tcie/Wikimania2005]]
                    user2_re=re.compile(r'\[\['+lexicon[lang]['user_tag']+':([^\]]+?)\]\]')
                    link_re=re.compile(r'\[\[([^\]]+?)\|(.+?)\]\]')
                    link2_re=re.compile(r'\[\[(.+?)\]\]')
                    format_re=re.compile(r'&lt;.+?&gt;')
                    multiplequotes_re=re.compile(r'\'{2,}')
                    if line.startswith('==') and line.endswith('=='):
                        if len(pars)>0:
                            commentid+=1
                            xmlcomment=etree.Element('comment',id='janes.wikipedia.'+sys.argv[1]+'.'+str(articleid).zfill(8)+'.'+str(topicid).zfill(8)+'.'+str(commentid).zfill(8),lang=langid.classify(' '.join(pars))[0])
                            currenttopic.append(xmlcomment)
                            for par in pars:
                                try:
                                    xmlcomment.append(etree.fromstring('<p>'+par+'</p>'))
                                except:
                                    pass
                            pars=[]                            
                        topicid+=1
                        commentid=0
                        xmltopic=etree.Element('topic',id='janes.wikipedia.'+sys.argv[1]+'.'+str(articleid).zfill(8)+'.'+str(topicid).zfill(8))
                        title=link2_re.sub(r'<a href="\1">\1</a>',link_re.sub(r'<a href="\1">\2</a>',line.strip('= ')))
                        xmltitle=etree.Element('title')
                        #try:
                        xmltopic.append(etree.fromstring('<title>'+title+'</title>'))
                        #except:
                        #    xmltitle.text=title
                        #xmltopic.append(xmltitle)
                        xmlpage.append(xmltopic)
                        currenttopic=xmltopic
                        continue
                    if line.strip()!='':
                        if currenttopic==None:
                            topicid+=1
                            commentid=0
                            currenttopic=etree.Element('topic',id='janes.wikipedia.'+sys.argv[1]+'.'+str(articleid).zfill(8)+'.'+str(topicid).zfill(8))
                            xmlpage.append(currenttopic)
                        text=multiplequotes_re.sub('',link2_re.sub(r'<a href="\1">\1</a>',link_re.sub(r'<a href="\1">\2</a>',user2_re.sub(r'<user name="\1">\1</user>',user_re.sub(r'<user name="\1">\2</user>',format_re.sub('',line))))))
                        if text.strip()=='':
                            continue
                        pars.append(text)
                        if '<user ' in text:
                            commentid+=1
                            xmlcomment=etree.Element('comment',id='janes.wikipedia.'+sys.argv[1]+'.'+str(articleid).zfill(8)+'.'+str(topicid).zfill(8)+'.'+str(commentid).zfill(8),lang=langid.classify(' '.join(pars))[0])
                            currenttopic.append(xmlcomment)
                            for par in pars:
                                try:
                                    xmlcomment.append(etree.fromstring('<p>'+par+'</p>'))
                                except:
                                    pass
                            pars=[]
                if len(pars)>0:
                    commentid+=1
                    xmlcomment=etree.Element('comment',id='janes.wikipedia.'+sys.argv[1]+'.'+str(articleid).zfill(8)+'.'+str(topicid).zfill(8)+'.'+str(commentid).zfill(8),lang=langid.classify(' '.join(pars))[0])
                    currenttopic.append(xmlcomment)
                    for par in pars:
                        try:
                            xmlcomment.append(etree.fromstring('<p>'+par+'</p>'))
                        except:
                            pass
                    pars=[]                            
        ispage=False
        ispagetalk=False
        isusertalk=False
    if ispage:
        page+=line
    if line.strip()=='<ns>1</ns>':
        ispagetalk=True
    elif line.strip()=='<ns>3</ns>':
        isusertalk=True
sys.stdout.write(etree.tostring(xmlroot,pretty_print=True,xml_declaration=True,encoding='UTF-8'))
