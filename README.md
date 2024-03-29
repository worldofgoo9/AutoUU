AutoUU-悠悠有品租赁自动上架的开源轻量化工具

项目系列文章：https://blog.csdn.net/weixin_43543078/article/details/130891185

教学视频：https://www.bilibili.com/video/BV1Yu4y1f7iE

蓝奏云下载地址：https://wwkp.lanzoum.com/iQOBA0xcw4zc 密码:a4ee

注：因为API失效目前不能正常使用，请等待更新，当前代码仅供学习参考。

注：本项目依据GPL3.0协议开源


(1)环境配置：

安装Python：基本上版本没有太大限制，3.X版本应该都可以。推荐通过安装miniconda：https://docs.conda.io/en/latest/miniconda.html，安装miniconda后python应该是自动安装好了！

安装requests包和schedule包：打开cmd（按windows+r，输入cmd并回车），输入命令pip install requests schedule -i https://mirrors.aliyun.com/pypi/simple/ 执行安装即可，有需要按y的按y即可。

更具体一点的话，我这里使用的版本为：

python 3.8.8

requests 2.25.1

schedule 1.2.0



(2)程序运行

1、下载本程序源码压缩包并解压缩。


2、修改配置文件，配置文件的具体说明见“程序篇”，如果你只是想使用，那么需要修改configIndex.json和myconfig.json。

<1>configIndex.json文件

configIndex.json格式示例如下：

{
    "configPath" : [
        "example.json",
        "myconfig.json"
    ],
    "userName" : "你的用户名(手机)", 
    "userPwd" : "登录密码",
    "retryTimes" : 3,
    "retryInterval" : 300.0,
    "runTime" : "17:00",
    "maxInvPage" : 2
}

其中configPath是一个列表，每一个对应了一个配置文件，之所以这里采用列表是为了控制多个配置文件的使能，使得配置更加灵活，例如：如果你有的时间只想上架一部分饰品（往往有这种需求的话会提前分类到不同的配置里），可以把不想上架的饰品对应的配置json去掉。**如果你是新手，可以不修改这一项。**

其他的字段为：

  "userName" : "你的用户名(手机)", 

  "userPwd" : "登录密码",

  "retryTimes" : 3, 代表了当出现错误时，重试的次数，**不建议更改**

  "retryInterval" : 300.0, 代表了当出现错误时，重试前等待的时间（秒），**不建议更改**

  "runTime" : "17:00" 代表了上架流程每天的运行时间，根据自己的需求更改，

  "maxInvPage" : 2  程序只会检测你的前X页库存，也就是这里的最大检测库存页数设定。库存页数根据自己需要上架库存量而定，建议够用即可，不要太大，否则会很慢还可能出问题。一般来说，新获得的物品都是在前面的，所以到cd的物品也是在前面，加上平均下来每一天的物品不会太多，所以一般2-3页就很多很多了。

 

<2>myconfig.json文件

具体的配置文件格式如下，这里以“myconfig.json”文件为例：

[
    {
        "float":"0.022881954",
        "strategy":"fix",
        "shortPrice":6.99,
        "longPrice":5.66,
        "valuePrice":16000.0,
        "maxDay":23,
        "message":"M9刺刀（★） | 虎牙"
    },
    {
        "float":"0.01373",
        "strategy":"long",
        "shortPrice":3.0,
        "longPrice":2.5,
        "valuePrice":14999.0,
        "maxDay":22,
        "message":"长租好价 001",
        "name":"M9刺刀（★） | 虎牙"
      }

]



该文件是一个字典的列表，每一个字典（{}）代表了一项配置，用逗号隔开（注意最后一项后面没有逗号），对应一个物品，其中各个字段含义如下：

  {

​    "float":"0.01342727987876540", 代表了物品的磨损值，是标识一个物品的关键（**请使用有品上的完整磨损值而不是某****buff****的，因为某buff****的显示不全**）

​    "strategy": "long", 代表了物品的上架策略，共有四种，会在下面解释。

​    "shortPrice":3.0, 物品的短租租金，注意在不同策略下含义不同。

​    "longPrice":2.5,  物品的长租租金，注意在不同策略下含义不同。

​    "valuePrice":14999.0, 物品的押金设置，售价会设置为同值

​    "maxDay":22, 物品的最长租赁时间

​    "message":"长租好价 001", 物品的上架描述

​    "name":"M9刺刀（★） | 虎牙" ，物品的名称，也可以看作备忘字段，可以填写任意字符，不会影响上架流程，目的是：如果你填写了，之后以后就知道这个是什么物品，不会忘了。

​    

  },

 

这里具体解释一下"strategy"字段，一共有四种设置：

"short": 顾名思义，代表了优先短租，短租价格会设置为(市场短租底价x*0.97-0.01)，长租价格会设置为(市场长租底价*x1.015+0.01)

"long": 代表了优先短租，短租价格会设置为(市场短租底价x*1.015+0.01)，长租价格会设置为(市场长租底价*x0.97-0.01)

"auto": 代表了无偏向性的自动定价，长短租价格会分别设置为(底价租金x0.985)。

"fix": 代表了固定的价格设置，长短租价格会固定设置为"shortPrice"和"longPrice"中的值。

此外，在自动定价的模式下（short/long/auto），"shortPrice"和"longPrice"代表了定价的下限，也就是说如果自动定价获取的价格小于你设置的下限，那么价格就会被设置为该下限值。

 

3、打开cmd（按windows+r，输入cmd并回车）

4、加载到源码压缩包目录，可以复制资源管理器的地址后 cd 地址（执行命令cd  {地址}）。如下图，注意如果你文件放在非系统盘（C盘），则需要先执行一个切换盘符的命令，即“{盘符}:”，如“D:”，并回车。



5、设置好了以后，执行命令python autouu.py，看到程序正常输出信息即代表正常运行。如果还提示缺少某些包，一般通过自行安装即可（输入命令pip install {包名称}）。
