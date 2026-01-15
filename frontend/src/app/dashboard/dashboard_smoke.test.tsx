
import { render, screen } from '@testing-library/react'
import DashboardPage from './page'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock useAuth
vi.mock('@/hooks/useAuth', () => ({
    useAuth: () => ({ user: { id: 'user-1', name: 'Test User' }, isLoading: false }),
}))

// Mock API data/hooks
vi.mock('@tanstack/react-query', () => ({
    useQuery: () => ({
        data: {
            avg_visibility_score: 85,
            completed_experiments: 12,
            total_experiments: 15,
            avg_position: 2.3
        },
        isLoading: false,
    })
}))

vi.mock('@/components/Navbar', () => ({
    Navbar: () => <div data-testid="navbar">Navbar</div>
}))

// Mock Charts to avoid resizing issues in JSDOM
vi.mock('@/components/dashboard/ShareOfVoiceChart', () => ({
    ShareOfVoiceChart: () => <div data-testid="sov-chart">SOV Chart</div>
}))
vi.mock('@/components/dashboard/VisibilityTrendChart', () => ({
    VisibilityTrendChart: () => <div data-testid="trend-chart">Trend Chart</div>
}))

describe('DashboardPage - Trend Indicators', () => {
    it('renders dashboard visuals and trend indicators', () => {
        render(<DashboardPage />)

        // Verify trend indicators are present
        // We look for the hardcoded values we added: +2.5% and +12%

        expect(screen.getByText('+2.5%')).toBeDefined()
        expect(screen.getByText('+12%')).toBeDefined()
    })
})
