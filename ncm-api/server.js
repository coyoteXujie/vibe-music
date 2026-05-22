const path = require("path");
const ncm = require("NeteaseCloudMusicApi");

async function start() {
  const generateConfig = require("NeteaseCloudMusicApi/generateConfig");
  await generateConfig();
  ncm.start({ port: 52401, host: "127.0.0.1" });
}

start().catch((err) => {
  console.error("NCM API 启动失败:", err.message);
  const server = require("NeteaseCloudMusicApi/server");
  server.serveNcmApi({ port: 52401, host: "127.0.0.1" });
});
