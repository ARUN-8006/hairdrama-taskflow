const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export function getToken(){ if(typeof window==='undefined') return null; return localStorage.getItem('taskflow_token'); }
export function saveSession(token:string,user:unknown){ localStorage.setItem('taskflow_token',token); localStorage.setItem('taskflow_user',JSON.stringify(user)); }
export function clearSession(){ localStorage.removeItem('taskflow_token'); localStorage.removeItem('taskflow_user'); }
export function getStoredUser(){ if(typeof window==='undefined') return null; const raw=localStorage.getItem('taskflow_user'); return raw?JSON.parse(raw):null; }

export async function api(path:string, options:RequestInit={}){
  const token=getToken();
  const headers:HeadersInit={'Content-Type':'application/json',...(options.headers||{})};
  if(token) (headers as Record<string,string>).Authorization=`Bearer ${token}`;
  const res=await fetch(`${API}${path}`,{...options,headers});
  const data=await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}
