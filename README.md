# Flask-bbs
项目已经上线 http://129.28.170.70  
测试账号 用户名：test 密码：1234  
## 简介  
数据存储使用MySQL，ORM使用SQLAlchemy，模板使用jinja2，使用Redis进行缓存优化  
使用 Redis 服务器存储 Token、Session 等数据，以实现多进程间的数据共享  
使用 Nginx 反向代理，过滤静态资源请求，提升访问速度，配置Gunicorn 多 worker 和 gevent 达到多进程负载均衡，使用Supervisor 管理进程  
## 主要功能  
- 用户登录与注册  
- 个人主页、信息管理功能  
- 话题的浏览、发布、评论，支持@用户功能  
- 邮件通知与系统消息通知功能，用户间支持私信功能  
- 支持通过邮件找回密码功能  
- 实现对CSRF、XSS、SQL注入攻击的防御  
# 详细
## 注册/登录
![login/register](https://github.com/FXYGR/Flask-bbs/blob/master/gif/login%26register.gif "login/register")
## 话题浏览与发布
![topic](https://github.com/FXYGR/Flask-bbs/blob/master/gif/topic.gif "topic")
## 个人主页
![profile](https://github.com/FXYGR/Flask-bbs/blob/master/gif/profile.gif "profile")
## 设置、修改签名和上传头像
![setting](https://github.com/FXYGR/Flask-bbs/blob/master/gif/setting.gif "setting")
## @用户与私信
![@user](https://github.com/FXYGR/Flask-bbs/blob/master/gif/@user.gif "@user")
## 找回密码
![password](https://github.com/FXYGR/Flask-bbs/blob/master/gif/password.gif "password")
