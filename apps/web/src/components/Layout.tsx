import { Link, Outlet } from 'react-router-dom'
import { useWorld } from '../store/world-store'

const pages = ['map','dispatch','drivers','riders','trips','metrics','traces','geo','sim','settings']

export function Layout() {
  const { state } = useWorld()
  return <div style={{display:'flex',height:'100vh',background:'#111',color:'#eee'}}>
    <aside style={{width:220,padding:12,borderRight:'1px solid #333'}}>
      <h2>HyperDispatch</h2>
      {pages.map(p => <div key={p}><Link to={`/${p}`} style={{color:'#bbb'}}>{p}</Link></div>)}
    </aside>
    <main style={{flex:1,padding:12}}>
      <div>WS: {state.connected ? 'connected':'offline'}</div>
      <Outlet/>
    </main>
  </div>
}
