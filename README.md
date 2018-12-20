# transfer (requests ver.)

因为12306网站改版了，原来用selenium写的不能再用了。并且selenium有个缺点是速度慢，并且考虑到有些人机子上没有装chromedriver，所以现在改用requests重写了一个提供换乘建议的代码。

## 依赖

这是用python3写的代码。

用到一些包：

#### requests

用于发送request请求获取车次信息。

#### json

用于解析12306所用的站名到站代号的映射。

#### datetime

#### getopt


## 使用说明
```
python transfer.py --from 广州南 --to 端州 --date 2018-12-20 --nearly 12:00 --nlate 22:00
```
#### Options

+ **--from**: 出发站, 目前只支持['广州南', '肇庆', '端州'].
+ **--to**: 到达站, 目前只支持['广州南', '肇庆', '端州'].
+ **--date**: 日期, 格式为'yyyy-mm-rr'.
+ **--nearly** [optional]: 筛选不早于此时间的车次, 格式为'hh:mm'.
+ **--nlate** [optional]: 筛选不晚于此时间的车次, 格式为'hh:mm'.

#### Output

+ 接驳方案：A车 -> B车
+ 时间：全程 起始时间-到达时间
+ 总时间
+ 接驳时间：中转接驳时间.

#### Update
+ 2018/12/20 添加了web版本, 可以通过访问https://coldog.cn/transfer/index.html, 在网页上使用换乘助手. 
使得自己不必用PC而只用手机就可以使用这个程序.

## TODO

1. 增加佛山西站作为中转站. (但我还没试过这种操作, 先看看这样方不方便.)
2. 增加广东省内的其他路线, 可能会用到图算法, 感觉较难, 闲得无聊再吧.
3. 尝试加入买票功能. (非抢票, 仅自用)
