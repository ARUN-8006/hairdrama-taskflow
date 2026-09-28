'use client';
import Script from 'next/script';
import { useRouter } from 'next/navigation';
import { saveSession } from '../../lib/api';
import { useState } from 'react';

export default function Login(){
  const router=useRouter(); const [error,setError]=useState('');
  async function handleCredential(response:{credential:string}){
    try{
      setError('');
      const api=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
      const res=await fetch(`${api}/auth/google`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:response.credential})});
      const data=await res.json(); if(!res.ok) throw new Error(data.error||'Login failed');
      saveSession(data.token,data.user); router.push('/dashboard');
    }catch(e){setError(e instanceof Error?e.message:'Login failed')}
  }
  return <>
    <Script src="https://accounts.google.com/gsi/client" strategy="afterInteractive" onLoad={()=>{
      const google=(window as any).google; if(!google) return;
      google.accounts.id.initialize({client_id:process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,callback:handleCredential});
      google.accounts.id.renderButton(document.getElementById('google-btn'),{theme:'outline',size:'large',width:320,text:'continue_with'});
    }}/>
    <main className="container" style={{maxWidth:520,paddingTop:100}}><div className="card">
      <div className="brand">TaskFlow</div><h1>Task management, simplified.</h1><p className="muted">Sign in with your Google account to manage and assign tasks.</p>
      {error&&<p className="error">{error}</p>}<div id="google-btn" style={{marginTop:24}} />
    </div></main>
  </>;
}
