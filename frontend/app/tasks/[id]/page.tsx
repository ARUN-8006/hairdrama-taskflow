'use client';
import {useParams} from 'next/navigation';
export default function TaskDetails(){const params=useParams();return <main className="container"><div className="card"><h1>Task {params.id}</h1><p className="muted">Task details are available from the dashboard.</p></div></main>}
