'use server'

import { z } from 'zod'
import postgres from 'postgres'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { signIn } from '@/auth'
import { AuthError } from 'next-auth'

const sql = postgres(process.env.POSTGRES_URL!, { ssl: 'require' })

const FormSchema = z.object({
    id: z.string(),
    customerId: z.string({
        invalid_type_error: 'Please select a customer.'
    }),
    amount: z.coerce.number().gt(0, { message: 'Please enter an amount greater than $0.' }),
    status: z.enum(['pending', 'paid'], {
        invalid_type_error: 'Please select an invoice status.'
    }),
    date: z.string()
})

const CreateInvoice = FormSchema.omit({ id: true, date: true })
const UpdateInvoice = FormSchema.omit({ date: true, id: true })

export type State = {
    errors?: {
        customerId?: string[]
        amount?: string[]
        status?: string[]
    }
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

const ProcessPDFSchema = z.object({
    type: z.string().min(1, {
        message: 'Please select a document type.'
    }),
    user_email: z.string().email({ message: 'Please enter a valid email.' })
})

export type ProcessPDFState = {
    errors?: {
        type?: string[]
        user_email?: string[]
        file?: string[]
    }
    message?: string | null
}

export async function processPDF(prevState: ProcessPDFState, formData: FormData) {
    const validatedFields = ProcessPDFSchema.safeParse({
        type: formData.get('type'),
        user_email: formData.get('user_email')
    })

    if (!validatedFields.success) {
        return {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to Process PDF.'
        }
    }

    const file = formData.get('file') as File
    if (!file || file.size === 0) {
        return {
            errors: { file: ['Please select a PDF file.'] },
            message: 'No file selected.'
        }
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        return {
            errors: { file: ['Only PDF files are allowed.'] },
            message: 'Invalid file type.'
        }
    }

    const { type, user_email } = validatedFields.data

    try {
        const baseUrl = process.env.API_URL || 'http://new-service:8000'

        // Save file to /shared_files/only_one_file
        const fileBuffer = await file.arrayBuffer()
        const fileName = file.name
        const filePath = `${process.env.PATH_TO_SHARED_FILES}${fileName}`

        // Send to API for processing
        const response = await fetch(`${baseUrl}/document/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pdf_filepath: filePath,
                document_type: type,
                user_email
            }),
            cache: 'no-store'
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(errorData.detail || `Failed to process PDF: ${response.statusText}`)
        }

        const result = await response.json()
        revalidatePath('/dashboard/documents')
        return {
            message: `PDF processed successfully! Document ID: ${result.document_id || 'N/A'}`
        }
    } catch (error) {
        console.error('API Error:', error)
        return {
            message: error instanceof Error ? error.message : 'API Error: Failed to Process PDF.'
        }
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
