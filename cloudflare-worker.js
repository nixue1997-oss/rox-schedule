// 飞书 OAuth Token 交换 Worker
// 部署命令: npx wrangler deploy cloudflare-worker.js
// 需要设置环境变量: FEISHU_APP_ID, FEISHU_APP_SECRET

export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST', 'Access-Control-Allow-Headers': 'Content-Type' }
      });
    }
    
    if (url.pathname === '/exchange' && request.method === 'GET') {
      const code = url.searchParams.get('code');
      if (!code) return new Response(JSON.stringify({error: 'Missing code'}), {status: 400, headers: {'Content-Type': 'application/json'}});
      
      // 1. Exchange code for user_access_token
      const tokenResp = await fetch('https://open.feishu.cn/open-apis/authen/v2/oauth/token', {
        method: 'POST',
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: JSON.stringify({
          grant_type: 'authorization_code',
          client_id: FEISHU_APP_ID,
          client_secret: FEISHU_APP_SECRET,
          code: code
        })
      });
      
      const tokenData = await tokenResp.json();
      if (tokenData.code !== 0) {
        return new Response(JSON.stringify({error: tokenData.error_description || 'Token exchange failed'}), {status: 400, headers: {'Content-Type': 'application/json'}});
      }
      
      // 2. Get user info with user_access_token
      const userResp = await fetch('https://open.feishu.cn/open-apis/authen/v1/user_info', {
        headers: { 'Authorization': `Bearer ${tokenData.access_token}` }
      });
      const userData = await userResp.json();
      
      return new Response(JSON.stringify({
        name: userData.name,
        email: userData.email,
        user_id: userData.user_id,
        open_id: userData.open_id
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    return new Response('Not found', {status: 404});
  }
};
