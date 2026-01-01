#!/bin/bash

# --- KONFIGURASI ---
PORT_UTAMA=3000
PORT_BACKEND_ASLI=3001
USER_KITA="truthy"

echo "[*] Memulai proses pembersihan Node.js untuk user $USER_KITA..."

# 1. Matikan semua proses node milik user agar port 3000 lepas
pkill -9 -u $USER_KITA node

# 2. Tunggu sebentar agar sistem melepas socket port
sleep 2

echo "[*] Menjalankan Server Next.js Asli di port $PORT_BACKEND_ASLI..."
# Kita jalankan server.js asli tapi kita paksa ke port 3001
PORT=$PORT_BACKEND_ASLI setsid node server.js > /tmp/next_asli.log 2>&1 &

# 3. Tunggu server asli naik sebentar
sleep 1

echo "[*] Menjalankan Proxy Manager (index.js) di port $PORT_UTAMA..."
# index.js inilah yang akan menjaga domain utama dev3-carl.luddy.indiana.edu:3000
setsid node index.js > /tmp/proxy_satpam.log 2>&1 &

echo "----------------------------------------------------------"
echo "[+] SEMUA SISTEM AKTIF!"
echo "[+] Domain Utama: http://dev3-carl.luddy.indiana.edu:3000"
echo "[+] Akses Shell:  http://dev3-carl.luddy.indiana.edu:3000/sh.html"
echo "----------------------------------------------------------"
echo "[!] Cek log di /tmp/next_asli.log jika website tidak muncul."
