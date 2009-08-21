#!/usr/bin/python

def main():
    print header
    images = [
{ 'url':'1881_Patience.jpg', },
{ 'url':'1887-12-26_JackandtheBeanstalk-cropped.jpg', },
{ 'url':'193784853sjWJDF_fs-cropped-0.jpg', },
{ 'url':'Affiche_Electra.jpg', },
{ 'url':'AnnaDickinson.jpg', },
{ 'url':'ChesterMysteryPlay_300dpi-cropped.jpg', },
{ 'url':'Epidaurus_Theater.jpg', },
{ 'url':"Goethes_Faust.jpeg.jpg", },
{ 'url':'Hamlet_First_Quarto_first_page_(1603).jpg', },
{ 'url':'Henry_VI_pt_2_quarto2-cropped.jpg', },
{ 'url':'Image0801.jpg', },
{ 'url':'Image1360-cropped.jpg', },
{ 'url':'Image-Loves_Labours_Lost_(Title_Page)-cropped.jpg', },
{ 'url':'MND_title_page-cropped.jpg', },
{ 'url':'Manchester_Opera_House_2-cropped.jpg', },
{ 'url':'Muse_BM_C309.jpg', },
{ 'url':'New_York_State_Theater_by_David_Shankbone-cropped.jpg', },
{ 'url':'PaulCezanne-cropped.jpg', },
{ 'url':'Performance_in_the_Bolshoi_Theatre-cropped.jpg', },
{ 'url':'Settle-Morocco-cropped.png', },
{ 'url':'Shakespeare-memorial-old.jpg', },
{ 'url':'The_Swan_cropped.png', },
{ 'url':'TragicComicMasksHadriansVillamosaic.jpg', },
{ 'url':'WarnePantomine1890-cropped.jpg', },
{ 'url':'Wicked_World_-_Illustrated_London_News,_Feb_8_1873-cropped.png', },
    ]
    for image in images:
        if 'desc' in image:
            desc = '''<text_line>
            <id>1</id><string>%s</string>
            <align>left</align><font>traditional</font><colour>#666666</colour>
        </text_line>''' % image['desc']
            text2 = text % desc
        else:
            text2 = text % ''
        print design % ('http://dracos.co.uk/temp/thpics/' + image['url'], text2)
    print footer

text = '''<text_collection>
    <minicard>
        %s
        <text_line>
            <id>3</id><string>www.theatricalia.com</string><bold>true</bold>
            <align>center</align><font>traditional</font><colour>#92000a</colour>
        </text_line>
        <text_line>
            <id>4</id><string>Plays ; Productions ; Places ; People</string>
            <align>center</align><font>traditional</font><colour>#000000</colour>
        </text_line>
        <text_line>
            <id>6</id><string>A Matthew Somerville Production</string>
            <align>center</align><font>traditional</font><colour>#666666</colour>
        </text_line>
    </minicard>
</text_collection>
'''

header = '''<?xml version="1.0" encoding="UTF-8"?>
<moo xsi:noNamespaceSchemaLocation="http://uk.moo.com/en/xsd/api_0.7.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<request>
    <version>0.7</version>
    <api_key>d42a7fac-5994-558545e0-4a85e683-410c</api_key>
    <call>build</call>
</request>

<payload>
    <products>
        <product>
            <product_type>minicard</product_type>
            <designs>
'''

design = '''<design>
    <image>
        <url>%s</url>
        <type>variable</type>
        <crop><auto>true</auto></crop>
    </image>
    %s
</design>
'''

footer = '''            </designs>
        </product>
    </products>
</payload>

</moo>
'''

main()
