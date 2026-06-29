'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'
import { signIn } from '@/auth'
import { AuthError } from 'next-auth'
import { createDocumentDocumentPost } from './orval/src/document-management/document-management'

export type State = {
    message?: string | null
}

export async function authenticate(prevState: string | undefined, formData: FormData) {
    try {
        await signIn('credentials', formData)
    } catch (error) {
        if (error instanceof AuthError) {
            switch (error.type) {
                case 'CredentialsSignin':
                    return 'Invalid credentials.'
                default:
                    return 'Something went wrong.'
            }
        }
        throw error
    }
}

const TransactionUpdateSchema = z.object({
    history: z.string().optional(),
    category_name: z.string().min(1, { message: 'Please enter a category name.' })
})

export type TransactionState = {
    errors?: {
        history?: string[]
        category_name?: string[]
    }
    message?: string | null
}

export async function updateTransaction(
    id: string,
    prevState: TransactionState,
    formData: FormData
) {
    const validatedFields = TransactionUpdateSchema.safeParse({
        history: formData.get('history'),
        category_name: formData.get('category_name')
    })

    if (!validatedFields.success) {
        return {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to Update Transaction.'
        }
    }

    const { history, category_name } = validatedFields.data

    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const url = `${baseUrl}/transactions/${id}`

        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                history,
                category_name
            }),
            cache: 'no-store'
        })

        if (!response.ok) {
            throw new Error(`Failed to update transaction: ${response.statusText}`)
        }
    } catch (error) {
        console.error('API Error:', error)
        return { message: 'API Error: Failed to Update Transaction.' }
    }

    revalidatePath('/dashboard/transactions')
    return { message: 'Transaction updated successfully!' }
}

export async function createDocument(prevState: State, formData: FormData) {
    const document_type = formData.get('type')
    const user_email = formData.get('user_email')
    const file = formData.get('file') as File

    try {
        const value = await createDocumentDocumentPost({
            pdf_filepath: `${process.env.PATH_TO_SHARED_FILES}${file.name}`,
            document_type: document_type as string,
            user_email: user_email as string
        })

        revalidatePath('/dashboard/documents')
    } catch (error) {
        console.error('API Error:', error)
        return { message: 'API Error: Failed to Create Document.' }
    }
}

export async function processDocument(documentId: string) {
    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const url = `${baseUrl}/transactions/${documentId}`

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                Accept: 'application/json'
            },
            cache: 'no-store'
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(
                errorData.detail || `Failed to process document: ${response.statusText}`
            )
        }

        const result = await response.json()
        revalidatePath('/dashboard/documents')
        return {
            success: true,
            message: `Document processed successfully! ${result.message || ''}`
        }
    } catch (error) {
        console.error('API Error:', error)
        return {
            success: false,
            message:
                error instanceof Error ? error.message : 'API Error: Failed to Process Document.'
        }
    }
}

// Export transactions to CSV
export async function exportTransactionsToCSV() {
    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const response = await fetch(`${baseUrl}/transactions/export/csv`, {
            method: 'GET',
            headers: {
                Accept: 'application/json'
            },
            cache: 'no-store'
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(errorData.detail || `Failed to export CSV: ${response.statusText}`)
        }

        const result = await response.json()
        return {
            success: true,
            message: result.message || 'CSV exported successfully!',
            filename: result.filename || 'transactions.csv'
        }
    } catch (error) {
        console.error('Export CSV Error:', error)
        return {
            success: false,
            message: error instanceof Error ? error.message : 'Failed to export CSV.'
        }
    }
}

// Import transactions from CSV
export async function importTransactionsFromCSV() {
    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'
        const response = await fetch(`${baseUrl}/transactions/import/csv`, {
            method: 'POST',
            headers: {
                Accept: 'application/json'
            },
            cache: 'no-store'
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(errorData.detail || `Failed to import CSV: ${response.statusText}`)
        }

        const result = await response.json()
        revalidatePath('/dashboard/transactions')
        return {
            success: true,
            message: result.message || 'CSV imported successfully!',
            updated_count: result.updated_count || 0
        }
    } catch (error) {
        console.error('Import CSV Error:', error)
        return {
            success: false,
            message: error instanceof Error ? error.message : 'Failed to import CSV.'
        }
    }
}
