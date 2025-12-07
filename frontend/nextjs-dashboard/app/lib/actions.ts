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

export async function createInvoice(prevState: State, formData: FormData) {
    // Validate form fields using Zod
    const validatedFields = CreateInvoice.safeParse({
        customerId: formData.get('customerId'),
        amount: formData.get('amount'),
        status: formData.get('status')
    })

    // If form validation fails, return errors early. Otherwise, continue.
    if (!validatedFields.success) {
        return {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to Create Invoice.'
        }
    }

    // Prepare data for insertion into the database
    const { customerId, amount, status } = validatedFields.data
    const amountInCents = amount * 100
    const date = new Date().toISOString().split('T')[0]

    // Insert data into the database
    try {
        await sql`
      INSERT INTO invoices (customer_id, amount, status, date)
      VALUES (${customerId}, ${amountInCents}, ${status}, ${date})
    `
    } catch (error) {
        // If a database error occurs, return a more specific error.
        return {
            message: 'Database Error: Failed to Create Invoice.'
        }
    }

    // Revalidate the cache for the invoices page and redirect the user.
    revalidatePath('/dashboard/invoices')
    redirect('/dashboard/invoices')
}

export async function updateInvoice(id: string, prevState: State, formData: FormData) {
    const validatedFields = UpdateInvoice.safeParse({
        customerId: formData.get('customerId'),
        amount: formData.get('amount'),
        status: formData.get('status')
    })

    if (!validatedFields.success) {
        return {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to Update Invoice.'
        }
    }

    const { customerId, amount, status } = validatedFields.data
    const amountInCents = amount * 100

    try {
        await sql`
      UPDATE invoices
      SET customer_id = ${customerId}, amount = ${amountInCents}, status = ${status}
      WHERE id = ${id}
    `
    } catch (error) {
        return { message: 'Database Error: Failed to Update Invoice.' }
    }

    revalidatePath('/dashboard/invoices')
    redirect('/dashboard/invoices')
}

export async function deleteInvoice(id: string) {
    await sql`DELETE FROM invoices WHERE id = ${id}`
    revalidatePath('/dashboard/invoices')
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
        const url = `${baseUrl}/api/transactions/${id}`

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
    type: z.enum(['debit', 'credit'], {
        invalid_type_error: 'Please select a document type.'
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

    if (!file.name.endsWith('.PDF')) {
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
        const filePath = `/shared_files/only_one_file/${fileName}`

        // Send to API for processing
        const response = await fetch(`${baseUrl}/api/pdf-processing`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pdf_filename: filePath,
                type,
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
            message: `PDF processed successfully! Document ID: ${result.id || 'N/A'}`
        }
    } catch (error) {
        console.error('API Error:', error)
        return {
            message: error instanceof Error ? error.message : 'API Error: Failed to Process PDF.'
        }
    }
}
