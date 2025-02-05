生成秘钥生成 SSH 密钥对
```bash
  ssh-keygen -t rsa -b 2048 -f id_rsa -N ""
```
宿主机测试连接
```bash
ssh -i id_rsa -p 2222 root@127.0.0.1
```
容器连接
```bash
ssh -i id_rsa root@ssh-server
```
获取docker内网容器ip
```bash
docker ps
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <目标容器名称或ID>
```

配置airflowSSH连接
Admin > Connections
