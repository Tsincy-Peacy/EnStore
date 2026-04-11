/**
 * EnStory — Cloudflare Worker Proxy
 * 
 * 用法：将此Worker部署到Cloudflare，Worker URL即为API_BASE
 * 
 * 请求格式：GET /?url={目标URL编码}
 * 返回格式：{ contents: "HTML字符串" }
 * 
 * 部署方式：
 * 1. 登录 https://dash.cloudflare.com
 * 2. 创建 Worker
 * 3. 粘贴此代码，保存并部署
 * 4. Worker URL 即为 API_BASE（如 https://enstory-proxy.xxx.workers.dev）
 */

const TARGET_HOST = 'www.ciyuangu.com';
const ALLOWED_HOSTS = ['www.ciyuangu.com'];

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrlParam = url.searchParams.get('url');

    if (!targetUrlParam) {
      return new Response(
        JSON.stringify({ error: 'Missing url parameter' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    let targetUrl;
    try {
      targetUrl = new URL(targetUrlParam);
    } catch {
      return new Response(
        JSON.stringify({ error: 'Invalid URL' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // 限制只允许请求词源谷
    if (!ALLOWED_HOSTS.includes(targetUrl.hostname)) {
      return new Response(
        JSON.stringify({ error: 'Forbidden: only ciyuangu.com allowed' }),
        { status: 403, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // 构造请求头，模拟浏览器
    const headers = new Headers();
    headers.set('User-Agent', 'Mozilla/5.0 (compatible; EnStory/1.0; +https://github.com/tsincy-peacy/EnStory)');
    headers.set('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8');
    headers.set('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8');
    headers.set('Referer', 'https://www.ciyuangu.com/');

    try {
      const response = await fetch(targetUrl.toString(), {
        headers,
        cf: { cacheTtl: 3600, cacheEverything: true }, // Cloudflare缓存1小时
      });

      const contents = await response.text();

      return new Response(
        JSON.stringify({ contents, status: response.status }),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=3600',
          },
        }
      );
    } catch (err) {
      return new Response(
        JSON.stringify({ error: 'Fetch failed: ' + err.message }),
        { status: 502, headers: { 'Content-Type': 'application/json' } }
      );
    }
  },
};
