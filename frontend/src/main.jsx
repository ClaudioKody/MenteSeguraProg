import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';
const api=async(path,opts={})=>{const r=await
fetch(`/api${path}`,{credentials:'include',headers:{'Content-Type':'application/json'},...opts});const d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.error||'No se pudocompletar la operación');return d};
const send=(path,method='GET',body)=>api(path,{method,
...(body?{body:JSON.stringify(body)}:{})});
function Login({go}){const
[register,setRegister]=useState(false),[admin,setAdmin]=useState(false),[data,setData]=useSta
te({}),[error,setError]=useState('');const submit=async
e=>{e.preventDefault();try{if(register){await
send('/auth/registro','POST',data);setRegister(false);return}const x=await
send('/auth/login','POST',data);go(x.user)}catch(e){setError(e.message)}};return <main
className="auth"><section className="card"><div className="mark">♡</div><h1>{register?'Crearcuenta':'Ingresar'}</h1><p>{register?'Tu espacio personal empieza acá.':'Continuá tu espaciode bienestar.'}</p><form onSubmit={submit}>{register&&<><input placeholder="Nombre" required
onChange={e=>setData({...data,nombre:e.target.value})}/><input placeholder="Apellido"
required onChange={e=>setData({...data,apellido:e.target.value})}/></>}<input
placeholder="Correo electrónico" type="email" required
onChange={e=>setData({...data,email:e.target.value})}/><input placeholder="Contraseña"
type="password" required
onChange={e=>setData({...data,password:e.target.value})}/>{register?<input
placeholder="Contacto de confianza" required
onChange={e=>setData({...data,contacto_confianza:e.target.value})}/>:<label><input
type="checkbox" checked={admin} onChange={e=>setAdmin(e.target.checked)}/> Soy
Administrador</label>}{admin&&!register&&<input placeholder="Documento"
onChange={e=>setData({...data,documento:e.target.value})}/>}<button>{register?'Registrarme':'Ingresar'}</button></form>{error&&<p className="error">{error}</p>}<button className="link"
onClick={()=>setRegister(!register)}>{register?'Ya tengo una cuenta':'Crear unacuenta'}</button></section></main>}
function App(){const[user,setUser]=useState(null),[page,setPage]=useState('hoy'),[data,setData]=useState(null);us
eEffect(()=>{api('/me').then(setUser).catch(()=>{})},[]);if(!user)return <Login
go={setUser}/>;return <main className="shell"><header><button className="menu"
onClick={()=>setPage(page==='menu'?'hoy':'menu')}>☰</button><span className="brand">Mente
Segura</span><button className="logout"
onClick={()=>send('/auth/logout','POST').then(()=>setUser(null))}>Salir</button></header>{page==='menu'?<Menu user={user} go={setPage}/>:page==='hoy'?<Home
go={setPage}/>:page==='diario'?<Diary/>:page==='chat'?<Chat
go={setPage}/>:page==='respirar'?<Breathe/>:page==='evolucion'?<Evolution/>:page==='biblioteca'?<Library/>:page==='ayuda'?<Help/>:page==='admin'?<Admin/>:<Home go={setPage}/>}</main>}
function Menu({user,go}){return <section className="card menu-panel"><h1>Menú</h1><button
onClick={()=>go('hoy')}>Frase del día</button><button onClick={()=>go('diario')}>Diario
emocional</button><button onClick={()=>go('chat')}>Chat preventivo</button><button
onClick={()=>go('respirar')}>Respiración guiada</button><button
onClick={()=>go('evolucion')}>Mi evolución</button><button
onClick={()=>go('biblioteca')}>Biblioteca</button><button onClick={()=>go('ayuda')}>Ayuda
profesional</button>{user.rol==='admin'&&<button onClick={()=>go('admin')}>Panel
administrador</button>}</section>}
function Home({go}){const
[q,setQ]=useState(null);useEffect(()=>{send('/frases').then(setQ)},[]);return <><section
className="hero"><span>FRASE DEL DÍA</span><h1>“{q?.texto||'Cuidarte también esavanzar.'}”</h1><p>— {q?.autor||'Mente Segura'}</p></section><div className="actions"><button
onClick={()=>{if(q)location.href=q.descarga}}>Descargar</button><button
onClick={()=>navigator.share?navigator.share({title:'MenteSegura',text:q?.texto}):navigator.clipboard?.writeText(q?.texto||'')}>Compartir</button><button onClick={()=>go('diario')}>Ingresar al diario</button></div></>}
function Diary(){const
[open,setOpen]=useState(false),[pin,setPin]=useState(''),[notes,setNotes]=useState([]),[editing,setEditing]=useState(null),[form,setForm]=useState({titulo:'',texto:''});const
load=()=>send('/notas').then(x=>setNotes(x.items));useEffect(()=>{if(open)load()},[open]);const save=async e=>{e.preventDefault();if(editing)await
send(`/notas/${editing}`,'PUT',form);else await
send('/notas','POST',form);setForm({titulo:'',texto:''});setEditing(null);load()};if(!open)return <section className="card"><h1>Diario emocional</h1><p>Este espacio es privado.</p><input
placeholder="PIN" type="password" value={pin} onChange={e=>setPin(e.target.value)}/><button
onClick={()=>send('/diario/pin','POST',{pin}).then(()=>setOpen(true)).catch(()=>alert('PINincorrecto'))}>Abrir diario</button></section>;return <section><h1>Diario emocional</h1><form
className="card form" onSubmit={save}><input placeholder="Título" value={form.titulo}
onChange={e=>setForm({...form,titulo:e.target.value})}/><textarea placeholder="Escribí
libremente..." required value={form.texto}
onChange={e=>setForm({...form,texto:e.target.value})}/><button>{editing?'Guardaredición':'Guardar nota'}</button></form>{notes.map(n=><article className="card note"
key={n.id_nota}><b>{n.titulo||'Registropersonal'}</b><small>{n.fecha_hora}</small><p>{n.texto}</p><button
onClick={()=>{setEditing(n.id_nota);setForm({titulo:n.titulo,texto:n.texto})}}>Editar</button
><button className="secondary"
onClick={()=>send(`/notas/${n.id_nota}`,'DELETE').then(load)}>Eliminar</button></article>)}</
section>}
function Chat({go}){const
[text,setText]=useState(''),[items,setItems]=useState([]),[crisis,setCrisis]=useState(null);const load=()=>send('/chat').then(x=>setItems(x.items));useEffect(load,[]);return
<section><h1>Chat preventivo</h1><p className="notice">Este chat no reemplaza atención
profesional.</p><div className="chatbox">{items.map((x,i)=><p className={`bubble ${x.rol}`}
key={i}>{x.texto}</p>)}</div><form className="form card" onSubmit={asynce=>{e.preventDefault();const x=await
send('/chat','POST',{mensaje:text});setItems([...items,{rol:'usuario',texto:text},...x.respuestas.map(t=>({rol:'asistente',texto:t}))]);if(x.nivel==='critico')setCrisis(x);setText('')}}>
<textarea value={text} onChange={e=>setText(e.target.value)} placeholder="¿Cómo te sentís
hoy?" required/><button>Enviar</button></form>{crisis&&<div className="cardcrisis"><h2>Alerta de cuidado</h2><p>{crisis.mensaje}</p><button onClick={()=>alert('Mensajepreparado para tu contacto de confianza: '+crisis.mensaje)}>Preparar SMS</button><a
className="call" href="tel:112">Llamar a emergencias</a><button
onClick={()=>go('respirar')}>Respirar ahora</button></div>}<button className="secondary"
onClick={()=>send('/chat','DELETE').then(load)}>Limpiar conversación</button></section>}
function Breathe(){const
[running,setRunning]=useState(false),[phase,setPhase]=useState('Listo paracomenzar');useEffect(()=>{if(!running)return;const phases=['Inhalá suavemente','Sostené elaire','Exhalá lentamente'];let i=0;setPhase(phases[i]);const
id=setInterval(()=>{i=(i+1)%phases.length;setPhase(phases[i])},4000);return()=>clearInterval(
id)},[running]);return <section className="card breathing"><h1>Respiración
guiada</h1><p>{phase}</p><div className="breath-circle"/><button
onClick={()=>setRunning(!running)}>{running?'Pausar':'Comenzar'}</button></section>}
function Evolution(){const
[x,setX]=useState(null);useEffect(()=>{send('/evolucion').then(setX)},[]);return
<section><h1>Mi evolución</h1><div className="card"><h2>También cuenta lo bueno</h2><p>Notas
registradas esta semana: {x?.notas_semana||0}</p>{x?.estados?.map(m=><p
key={m.estado}><b>{m.estado}</b>: {m.total}</p>)}</div></section>}
function Library(){const
[x,setX]=useState([]);useEffect(()=>{send('/biblioteca').then(d=>setX(d.items))},[]);return
<section><h1>Biblioteca digital</h1>{x.map(r=><article className="card item"
key={r.id_recurso}><b>{r.titulo}</b><small>{r.tipo}</small><p>{r.descripcion}</p><a
href={r.url} target="_blank">Ver recurso</a></article>)}</section>}
function Help(){const
[x,setX]=useState([]);useEffect(()=>{send('/ayuda').then(d=>setX(d.items))},[]);return
<section><h1>Ayuda profesional</h1>{x.map(r=><article className="card item"
key={r.id_ayuda}><b>{r.nombre}</b><small>{r.tipo}</small><p>{r.descripcion}</p><a
href={`tel:${r.telefono}`}>{r.telefono}</a></article>)}</section>}
function Admin(){const
[x,setX]=useState({resources:[],contacts:[]}),[newResource,setNewResource]=useState({titulo:'',descripcion:'',tipo:'Guía',url:''});const
load=()=>send('/admin').then(setX);useEffect(load,[]);const add=async
e=>{e.preventDefault();await
send('/admin/biblioteca','POST',newResource);setNewResource({titulo:'',descripcion:'',tipo:'Guía',url:''});load()};return <section><h1>Panel administrador</h1><p
className="notice">Gestión anónima. No se muestran diarios ni
chats.</p><h2>Biblioteca</h2><form className="card form" onSubmit={add}><input
placeholder="Título" required value={newResource.titulo}
onChange={e=>setNewResource({...newResource,titulo:e.target.value})}/><input
placeholder="URL" required value={newResource.url}
onChange={e=>setNewResource({...newResource,url:e.target.value})}/><input
placeholder="Descripción" value={newResource.descripcion}
onChange={e=>setNewResource({...newResource,descripcion:e.target.value})}/><button>Agregar
recurso</button></form>{x.resources.map(r=><article className="card item"
key={r.id_recurso}><input defaultValue={r.titulo} id={`r${r.id_recurso}`}/><button
onClick={()=>send(`/admin/biblioteca/${r.id_recurso}`,'PUT',{titulo:document.getElementById(`
r${r.id_recurso}`).value,descripcion:r.descripcion,tipo:r.tipo,url:r.url}).then(load)}>Guarda
r cambios</button><button className="secondary"
onClick={()=>send(`/admin/biblioteca/${r.id_recurso}`,'DELETE').then(load)}>Eliminar</button>
</article>)}<h2>Ayuda profesional</h2>{x.contacts.map(r=><article className="card item"
key={r.id_ayuda}><b>{r.nombre}</b><small>{r.telefono}</small><button className="secondary"
onClick={()=>send(`/admin/ayuda/${r.id_ayuda}`,'DELETE').then(load)}>Eliminar</button></article>)}</section>}
createRoot(document.getElementById('root')).render(<App/>);