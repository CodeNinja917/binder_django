# binder
> dns web管理系统
> 
> - 域名: 通过文件操作, rndc
> - 记录: dnspython
> 
## DNS配置
```
allow-new-zones yes;  // 允许添加域名
zone-statistics yes;  // 域名数据统计
```

*添加数据统计通信通道*
```
statistics-channels {
    inet * port 8053 allow { any; };
};
```

*生成rndc-key*
```
rm -rf /etc/rndc.key
rndc-confgen > /etc/rndc.conf
```

*在named.conf中配置rndc*
```
key "rndc-key" {
    algorithm hmac-md5;
    secret "4dUGckthvEwnuZj89YuRrg==";
};

controls {
    inet 127.0.0.1 port 953
        allow { any; } keys { "rndc-key"; };
};
```

*生成dessec-key, 用于加密通信*
```
dnssec-keygen -a HMAC-MD5 -b 128 -n HOST "web"
```

*在namec.conf中配置tsig*
```
key "web" {
    algorithm hmac-md5;
    secret "gmP4qpf0T5bkZLRPodruQg==";
};
```

## web管理系统

*安装依赖*
```
pip install -r requirement.txt
```

### 初始化
- 添加tsig key
- 添加master dns
- 同步域名信息
- 同步域名记录新

*同步域名信息*
```
api: /dns/server/{server_id}/sync_server_zone/
```

*同步域名记录信息*
```
api: /dns/zones/{zone_id}/sync_zone_records/
```
