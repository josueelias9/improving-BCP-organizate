import { NextResponse } from 'next/server'

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url)
        const skip = searchParams.get('skip') || '0'
        const limit = searchParams.get('limit') || '1000'

        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const url = `${baseUrl}/api/transactions?skip=${skip}&limit=${limit}`

        console.log('Proxying request to:', url)

        const response = await fetch(url, {
            headers: {
                'Accept': 'application/json'
            },
            cache: 'no-store'
        })

        if (!response.ok) {
            return NextResponse.json(
                { error: `Failed to fetch: ${response.statusText}` },
                { status: response.status }
            )
        }

        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('API Proxy Error:', error)
        return NextResponse.json(
            { error: 'Failed to fetch transactions' },
            { status: 500 }
        )
    }
}
