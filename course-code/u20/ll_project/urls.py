# ll_project/urls.py —— 可选项：定制错误处理器
handler404 = 'learning_logs.views.my_404'    # 访问不存在的页面时调用这个视图
handler500 = 'learning_logs.views.my_500'    # 服务器内部错误时调用这个视图
