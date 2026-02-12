import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Layout } from './components/Layout'
import { WorldProvider } from './store/world-store'

it('renders expanded nav links', () => {
  render(
    <WorldProvider>
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    </WorldProvider>,
  )
  expect(screen.getByText('Uber HyperDispatch')).toBeInTheDocument()
  expect(screen.getByText('Live Map')).toBeInTheDocument()
  expect(screen.getByText('Replay Studio')).toBeInTheDocument()
  expect(screen.getByText('Geo Index Debugger')).toBeInTheDocument()
})
