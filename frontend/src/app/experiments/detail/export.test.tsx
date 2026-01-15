
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ExperimentDetailContent } from './page'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'

// Use vi.hoisted to define mock data that can be used inside vi.mock factories
const { mockExperiment } = vi.hoisted(() => {
    return {
        mockExperiment: {
            id: 'exp-123',
            prompt: 'Test Prompt',
            target_brand: 'Test Brand',
            status: 'completed',
            created_at: '2023-01-01T00:00:00Z',
            iterations: [
                {
                    iteration_index: 0,
                    status: 'completed',
                    is_success: true,
                    wait_time: 1.5,
                    error_message: null,
                    raw_response: 'This is a "test" response with commas, and quotes.'
                }
            ]
        }
    }
})

// Mocks
vi.mock('next/navigation', () => ({
    useSearchParams: () => ({ get: () => 'exp-123' }),
}))

vi.mock('@/hooks/useAuth', () => ({
    useAuth: () => ({ user: { id: 'user-1' }, isLoading: false }),
}))

vi.mock('@/lib/api', () => ({
    experimentsApi: {
        getDetails: vi.fn().mockResolvedValue(mockExperiment)
    }
}))

// Mock React Query
vi.mock('@tanstack/react-query', () => ({
    useQuery: () => ({
        data: mockExperiment,
        isLoading: false,
        refetch: vi.fn()
    })
}))

// Mock Navbar (avoid rendering complex children)
vi.mock('@/components/Navbar', () => ({
    Navbar: () => <div data-testid="navbar">Navbar</div>
}))

describe('ExperimentDetailContent - CSV Export', () => {
    const originalCreateObjectURL = global.URL.createObjectURL
    const originalRevokeObjectURL = global.URL.revokeObjectURL

    beforeEach(() => {
        // Mock URL.createObjectURL
        global.URL.createObjectURL = vi.fn(() => 'mock-url')
        global.URL.revokeObjectURL = vi.fn()
    })

    afterEach(() => {
        global.URL.createObjectURL = originalCreateObjectURL
        global.URL.revokeObjectURL = originalRevokeObjectURL
        vi.clearAllMocks()
    })

    it('generates and downloads CSV when Export CSV button is clicked', () => {
        render(<ExperimentDetailContent />)

        // Find export button
        const exportBtn = screen.getByText('Export CSV')
        expect(exportBtn).toBeDefined()

        // Mock anchor click
        const clickSpy = vi.fn()
        const appendSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => null as any)
        const removeSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => null as any)

        // Intercept createElement to spy on the anchor tag
        const createElementSpy = vi.spyOn(document, 'createElement').mockImplementation((tagName) => {
            if (tagName === 'a') {
                return {
                    setAttribute: vi.fn(),
                    click: clickSpy,
                    style: {},
                } as any
            }
            return document.createElement(tagName)
        })

        // Click export
        fireEvent.click(exportBtn)

        // Assert URL.createObjectURL was called with correct blob
        expect(global.URL.createObjectURL).toHaveBeenCalled()
        const blobArg = (global.URL.createObjectURL as any).mock.calls[0][0]
        expect(blobArg).toBeInstanceOf(Blob)

        // Verify Blob content type
        expect(blobArg.type).toContain('text/csv')

        // Verify element creation and click
        expect(createElementSpy).toHaveBeenCalledWith('a')
        expect(clickSpy).toHaveBeenCalled()
        expect(appendSpy).toHaveBeenCalled()
        expect(removeSpy).toHaveBeenCalled()
    })
})
