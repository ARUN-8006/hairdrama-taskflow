export type User = { id:string; name:string; email:string; avatar_url?:string|null };
export type Task = { id:string; title:string; description:string; created_by:string; assigned_to:string; status:'pending'|'completed'; created_at:string; completed_at?:string|null; created_by_user?:User; assigned_user?:User };
