const path = require("path");

async function start() {
  const generateConfig = require("NeteaseCloudMusicApi/generateConfig");
  await generateConfig();
  const server = require("NeteaseCloudMusicApi/server");
  await server.serveNcmApi({
    port: 52401,
    host: "127.0.0.1",
    checkVersion: false
  });
}

start().catch((err) => {
  console.error("NCM API 启动失败:", err.message);
  process.exit(1);
});
