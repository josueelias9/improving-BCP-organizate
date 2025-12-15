import { NextResponse } from 'next/server'

export async function GET() {
    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const response = await fetch(`${baseUrl}/api/document-types/`, {
            headers: {
                'Accept': 'application/json',
            },
        })

        if (!response.ok) {
            console.error(`Failed to fetch document types: ${response.status} ${response.statusText}`)
            return NextResponse.json(
                { error: 'Failed to fetch document types' },
                { status: response.status }
            )
        }

        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('API Error:', error)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}
