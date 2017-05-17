## oval parser
OVAL是一种用来定义检查项、脆弱点等技术细节的一种描述语言，使用标准的XML格式组织其内容。
本工程是基于该语言针对资产进行相关脆弱性检测的封装包。


### 安装方法

1. 下载该工程

2. 安装RPM包
> yum install libxml2 libxslt libxslt-devel python-devel

3. 安装python包
> pip install -r requirements.txt


### 使用方法

1. 导入OvalParser
> from ovalparser.oval import OvalParser

2. 调用OvalParser
> OvalParser(oval_dir, Link).result()

   其中,
   ovail_dir是存放oval文件的文件夹
   Link是一个用于连接资产的类，Link类中需实现以下成员函数：

1、link 连接数据采集端

2、unlink 断开数据采集端

3、objects 获得某一类object的全部采集数据

4、flag 获得某一类object的采集状态

5、status 获得某一类object中某个数据的采集状态
