import postgres from 'postgres'
import {
    CustomerField,
    DocumentTable,
    DocumentType
} from './definitions'

const sql = postgres(process.env.POSTGRES_URL!, { ssl: 'require' })

export async function fetchCustomers() {
    try {
        const customers = await sql<CustomerField[]>`
      SELECT
        id,
        name
      FROM customers
      ORDER BY name ASC
    `

        return customers
    } catch (err) {
        console.error('Database Error:', err)
        throw new Error('Failed to fetch all customers.')
    }
}


export async function fetchDocuments(skip: number = 0, limit: number = 100) {
    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const url = `${baseUrl}/document/?skip=${skip}&limit=${limit}`

        console.log('Fetching documents from:', url)

        const response = await fetch(url, {
            headers: {
                Accept: 'application/json'
            },
            cache: 'no-store',
            next: { revalidate: 0 }
        })

        if (!response.ok) {
            console.error(`Failed to fetch documents: ${response.status} ${response.statusText}`)
            return []
        }

        const data: {
            documents: DocumentTable[]
            total_returned: number
            skip: number
            limit: number
        } = await response.json()
        return data.documents
    } catch (error) {
        console.error('API Error:', error)
        return []
    }
}

export async function fetchDocumentTypes() {
    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const url = `${baseUrl}/document-types/`

        console.log('Fetching document types from:', url)

        const response = await fetch(url, {
            headers: {
                Accept: 'application/json'
            },
            cache: 'no-store',
            next: { revalidate: 0 }
        })

        if (!response.ok) {
            console.error(
                `Failed to fetch document types: ${response.status} ${response.statusText}`
            )
            return []
        }

        const data: { document_types: DocumentType[]; total_count: number } = await response.json()
        return data.document_types
    } catch (error) {
        console.error('API Error:', error)
        return []
    }
}
