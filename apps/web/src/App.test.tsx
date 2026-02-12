import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { WorldProvider } from './store/world-store'
import { Layout } from './components/Layout'

it('renders nav links', () => {
  render(<WorldProvider><MemoryRouter><Layout/></MemoryRouter></WorldProvider>)
  expect(screen.getByText('HyperDispatch')).toBeInTheDocument()
  expect(screen.getByText('map')).toBeInTheDocument()
})
