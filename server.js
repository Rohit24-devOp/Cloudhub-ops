import http from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { extname, join, normalize } from 'node:path';

const port = Number(process.env.PORT || 3000);
const root = process.cwd();
const dataDir = join(root, 'data');
const dataPath = join(dataDir, 'cloudops.json');
const sessions = new Map();
const mime = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.json':'application/json; charset=utf-8' };
const hash = (value) => createHash('sha256').update(value).digest('hex');

const seed = {
  users: [],
  instances: [
    { id:'i-0a421d89', name:'production-api', type:'t3.large', region:'ap-south-1', status:'Running' },
    { id:'i-0a523d97', name:'worker-queue', type:'t3.medium', region:'ap-south-1', status:'Running' },
    { id:'i-0a618f21', name:'staging-web', type:'t3.small', region:'ap-south-1', status:'Stopped' }
  ],
  audits: [{ id:'audit-001', score:92, findings:[{ level:'medium', title:'3 users do not have MFA enabled', detail:'Identity controls' },{ level:'medium', title:'Access key inactive for over 90 days', detail:'developer-console' }] }],
  vpcs: [{ id:'vpc-0021', name:'production-network', cidr:'10.0.0.0/16', subnets:2, gateway:true }],
  waf: { name:'production-api-waf', rules:['AWS Core Rule Set','SQL injection protection','Known bad inputs','Rate limiting'], blocked:1248 },
  deployments: [{ id:'deploy-001', service:'production-api', branch:'main', status:'Healthy', createdAt:new Date().toISOString() }],
  notifications: ['Production deployment completed', 'IAM audit found 2 recommendations', 'Your weekly cost report is ready']
};
async function db(){ try { return JSON.parse(await readFile(dataPath, 'utf8')); } catch { await mkdir(dataDir, { recursive:true }); await writeFile(dataPath, JSON.stringify(seed, null, 2)); return structuredClone(seed); } }
async function persist(data){ await writeFile(dataPath, JSON.stringify(data, null, 2)); }
function send(res, code, body){ res.writeHead(code, { 'Content-Type':'application/json; charset=utf-8' }); res.end(JSON.stringify(body)); }
function cookie(req){ return (req.headers.cookie || '').split(';').map(x=>x.trim()).find(x=>x.startsWith('cloudops_session='))?.split('=')[1]; }
function user(req){ return sessions.get(cookie(req)); }
async function body(req){ let raw=''; for await (const chunk of req) raw += chunk; try { return JSON.parse(raw || '{}'); } catch { return {}; } }
function requireUser(req, res){ const account=user(req); if (!account) { send(res,401,{error:'Please sign in to continue.'}); return null; } return account; }
function session(res, account){ const id=randomUUID(); sessions.set(id, account); res.setHeader('Set-Cookie', `cloudops_session=${id}; HttpOnly; SameSite=Lax; Path=/`); }
function dashboard(data){ const running=data.instances.filter(i=>i.status==='Running').length; return { securityScore:data.audits.at(-1)?.score || 0, running, stopped:data.instances.length-running, estimatedCost:8462, instances:data.instances, notifications:data.notifications, deployments:data.deployments, waf:data.waf }; }

const server=http.createServer(async (req,res)=>{
  const url=new URL(req.url, `http://${req.headers.host}`); const { pathname }=url;
  if (pathname === '/api/auth/register' && req.method === 'POST') { const input=await body(req); const data=await db(); if (!input.email || !input.password) return send(res,400,{error:'Email and password are required.'}); if (data.users.some(x=>x.email===input.email)) return send(res,409,{error:'This email is already registered.'}); const account={id:randomUUID(),name:input.name || input.email.split('@')[0],email:input.email,passwordHash:hash(input.password)}; data.users.push(account); await persist(data); session(res,account); return send(res,201,{user:{id:account.id,name:account.name,email:account.email}}); }
  if (pathname === '/api/auth/login' && req.method === 'POST') { const input=await body(req); const data=await db(); const account=data.users.find(x=>x.email===input.email && x.passwordHash===hash(input.password)); if (!account) return send(res,401,{error:'Invalid email or password. Create an account to get started.'}); session(res,account); return send(res,200,{user:{id:account.id,name:account.name,email:account.email}}); }
  if (pathname === '/api/auth/logout' && req.method === 'POST') { sessions.delete(cookie(req)); res.setHeader('Set-Cookie','cloudops_session=; Max-Age=0; Path=/'); return send(res,200,{ok:true}); }
  if (pathname === '/api/session') { const account=requireUser(req,res); if (!account) return; return send(res,200,{user:{id:account.id,name:account.name,email:account.email}}); }
  if (!pathname.startsWith('/api/')) return serveStatic(pathname,res);
  if (!requireUser(req,res)) return;
  const data=await db();
  if (pathname === '/api/dashboard') return send(res,200,dashboard(data));
  if (pathname === '/api/instances' && req.method === 'GET') return send(res,200,data.instances);
  if (pathname === '/api/instances' && req.method === 'POST') { const input=await body(req); if (!input.name) return send(res,400,{error:'Instance name is required.'}); const instance={id:`i-${randomUUID().replaceAll('-','').slice(0,8)}`,name:input.name,type:input.type||'t3.medium',region:'ap-south-1',status:'Running'}; data.instances.push(instance); data.notifications.unshift(`${instance.name} is provisioning`); await persist(data); return send(res,201,instance); }
  const instanceMatch=pathname.match(/^\/api\/instances\/([^/]+)\/(start|stop|restart|terminate)$/);
  if (instanceMatch && req.method === 'POST') { const item=data.instances.find(x=>x.id===instanceMatch[1]); if (!item) return send(res,404,{error:'Instance not found.'}); const action=instanceMatch[2]; if(action==='terminate') data.instances=data.instances.filter(x=>x.id!==item.id); else item.status=action==='stop'?'Stopped':'Running'; data.notifications.unshift(`${item.name}: ${action} action completed`); await persist(data); return send(res,200,{ok:true,instance:item}); }
  if (pathname === '/api/iam/audit' && req.method === 'GET') return send(res,200,data.audits.at(-1));
  if (pathname === '/api/iam/audit' && req.method === 'POST') { const audit={id:`audit-${Date.now()}`,score:92,findings:data.audits[0].findings,createdAt:new Date().toISOString()}; data.audits.push(audit); data.notifications.unshift('IAM security audit completed'); await persist(data); return send(res,201,audit); }
  if (pathname === '/api/vpcs' && req.method === 'GET') return send(res,200,data.vpcs);
  if (pathname === '/api/vpcs' && req.method === 'POST') { const input=await body(req); const vpc={id:`vpc-${randomUUID().slice(0,8)}`,name:input.name||'new-network',cidr:input.cidr||'10.1.0.0/16',subnets:input.subnets||2,gateway:true}; data.vpcs.push(vpc); await persist(data); return send(res,201,vpc); }
  if (pathname === '/api/waf' && req.method === 'GET') return send(res,200,data.waf);
  if (pathname === '/api/waf' && req.method === 'PUT') { const input=await body(req); data.waf.rules=input.rules||data.waf.rules; await persist(data); return send(res,200,data.waf); }
  if (pathname === '/api/deployments' && req.method === 'GET') return send(res,200,data.deployments);
  if (pathname === '/api/deployments' && req.method === 'POST') { const input=await body(req); const item={id:`deploy-${Date.now()}`,service:input.service||'production-api',branch:input.branch||'main',status:'Building',createdAt:new Date().toISOString()}; data.deployments.unshift(item); data.notifications.unshift(`${item.service} deployment started`); await persist(data); return send(res,201,item); }
  if (pathname === '/api/notifications') return send(res,200,data.notifications);
  return send(res,404,{error:'API endpoint not found.'});
});
async function serveStatic(pathname,res){ const safe=normalize(pathname === '/' ? '/index.html' : pathname).replace(/^([.][.][\\/])+/, ''); try { const file=join(root,safe); const content=await readFile(file); res.writeHead(200,{'Content-Type':mime[extname(file)]||'application/octet-stream'}); res.end(content); } catch { res.writeHead(404,{'Content-Type':'text/plain'}); res.end('Not found'); } }
server.listen(port,()=>console.log(`CloudOps Hub API running at http://localhost:${port}`));
