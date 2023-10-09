# Chỉ chạy file này 1 lần
wget https://dl.min.io/server/minio/release/linux-amd64/minio_20231007150738.0.0_amd64.deb
dpkg -i minio_20231007150738.0.0_amd64.deb
mkdir ~/minio
minio server ~/minio --console-address 0.0.0.0:9090 --address 0.0.0.0:9000 # Các lần chạy tiếp theo chỉ chạy lệnh này là được
