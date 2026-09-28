'use client';
import { useEffect,useState } from 'react';
import { useRouter } from 'next/navigation';
import { api,clearSession,getStoredUser,getToken } from '../../lib/api';
import type {Task,User} from '../../types';

function TaskCard({task,onComplete}:{task:Task;onComplete:()=>void}){
 const canComplete=task.status==='pending';
 return <div className="task"><div className="task-head"><div><strong>{task.title}</strong><p className="muted" style={{margin:'6px 0'}}>{task.description||'No description'}</p></div><span className={`badge ${task.status==='completed'?'done':''}`}>{task.status}</span></div><small className="muted">Assigned to: {task.assigned_user?.name||'User'} · Created by: {task.created_by_user?.name||'User'}</small>{canComplete&&<div style={{marginTop:12}}><button className="btn success" onClick={onComplete}>Mark completed</button></div>}</div>
}

export default function Dashboard(){
 const router=useRouter(); const [user,setUser]=useState<User|null>(null); const [created,setCreated]=useState<Task[]>([]); const [assigned,setAssigned]=useState<Task[]>([]); const [error,setError]=useState(''); const [loading,setLoading]=useState(true);
 async function load(){try{const d=await api('/tasks');setCreated(d.created);setAssigned(d.assigned)}catch(e){setError(e instanceof Error?e.message:'Could not load tasks')}finally{setLoading(false)}}
 useEffect(()=>{if(!getToken()){router.replace('/login');return}setUser(getStoredUser());load()},[router]);
 async function complete(id:string){try{await api(`/tasks/${id}/complete`,{method:'PATCH'});await load()}catch(e){setError(e instanceof Error?e.message:'Could not complete task')}}
 if(loading)return <main className="container">Loading dashboard...</main>;
 return <main className="container"><div className="topbar"><div><div className="brand">TaskFlow</div><span className="muted">Welcome, {user?.name}</span></div><div style={{display:'flex',gap:10}}><button className="btn" onClick={()=>router.push('/tasks/new')}>+ New task</button><button className="btn secondary" onClick={()=>{clearSession();router.replace('/login')}}>Logout</button></div></div>{error&&<p className="error">{error}</p>}<div className="grid"><section className="card"><h2>Assigned to me</h2>{assigned.length===0?<p className="muted">No assigned tasks.</p>:assigned.map(t=><TaskCard key={t.id} task={t} onComplete={()=>complete(t.id)}/>)}</section><section className="card"><h2>Created by me</h2>{created.length===0?<p className="muted">No tasks created yet.</p>:created.map(t=><TaskCard key={t.id} task={t} onComplete={()=>complete(t.id)}/>)}</section></div></main>
}
