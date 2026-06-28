'use client'

import { useState } from 'react'
import { lusitana } from '@/app/ui/fonts'
import { processDocument } from '@/app/lib/actions'
import { ArrowPathIcon } from '@heroicons/react/24/outline'
import { DTOGetDocumentsResponse } from '@/app/lib/orval/src/bcp.schemas'

function formatDocumentDate(dateString: string) {
    try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) {
            return dateString
        }
        return new Intl.DateTimeFormat('en-US', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date)
    } catch {
        return dateString
    }
}

export default function DocumentsTable({ data }: { data: DTOGetDocumentsResponse }) {
    const { documents } = data
    const [processingId, setProcessingId] = useState<string | null>(null)
    const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

    const handleProcessDocument = async (documentId: string) => {
        setProcessingId(documentId)
        setMessage(null)

        const result = await processDocument(documentId)

        setProcessingId(null)
        setMessage({
            text: result.message,
            type: result.success ? 'success' : 'error'
        })

        // Clear message after 5 seconds
        setTimeout(() => setMessage(null), 5000)
    }

    const not_included_columns = ['user_id', 'id', 'document_type_id', 'data', 'plain_text']

    // Get column names from the first document
    const columns =
        documents.length > 0
            ? Object.keys(documents[0]).filter(col => !not_included_columns.includes(col))
            : []

    return (
        <div className='flex w-full flex-col'>
            <h2 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>All Documents</h2>

            {message && (
                <div
                    className={`mb-4 rounded-md px-4 py-3 text-sm ${
                        message.type === 'success'
                            ? 'bg-green-50 text-green-800'
                            : 'bg-red-50 text-red-800'
                    }`}
                >
                    {message.text}
                </div>
            )}

            <div className='flex grow flex-col justify-between rounded-xl bg-gray-50 p-4'>
                <div className='overflow-x-auto'>
                    <table className='min-w-full text-gray-900'>
                        <thead className='rounded-lg text-left text-sm font-normal'>
                            <tr>
                                {columns.map(column => (
                                    <th key={column} scope='col' className='px-3 py-5 font-medium'>
                                        {column}
                                    </th>
                                ))}
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className='bg-white'>
                            {documents.map(document => (
                                <tr
                                    key={document.id}
                                    className='w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg'
                                >
                                    {columns.map(column => {
                                        const value = document[column as keyof typeof document]
                                        const primitiveValue =
                                            value === null || value === undefined
                                                ? null
                                                : typeof value === 'object'
                                                  ? JSON.stringify(value)
                                                  : value
                                        let displayValue: React.ReactNode = primitiveValue ?? 'N/A'

                                        // Special formatting for specific columns
                                        if (column === 'document_type_name') {
                                            displayValue = (
                                                <span
                                                    className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                                                        String(value).includes('debit')
                                                            ? 'bg-red-100 text-red-700'
                                                            : 'bg-green-100 text-green-700'
                                                    }`}
                                                >
                                                    {value as string}
                                                </span>
                                            )
                                        } else if (column === 'processed') {
                                            const isProcessed = value === true
                                            displayValue = (
                                                <span
                                                    className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                                                        isProcessed
                                                            ? 'bg-green-100 text-green-700'
                                                            : 'bg-red-100 text-red-700'
                                                    }`}
                                                >
                                                    {isProcessed ? 'Sí' : 'No'}
                                                </span>
                                            )
                                        } else if (
                                            column === 'start_date' ||
                                            column === 'end_date'
                                        ) {
                                            displayValue = formatDocumentDate(value as string)
                                        } else if (column === 'unique_identifier') {
                                            displayValue = (
                                                <span className='font-medium'>
                                                    {value as string}
                                                </span>
                                            )
                                        } else if (typeof value === 'string' && value.length > 30) {
                                            // Truncate long strings
                                            displayValue = (
                                                <div
                                                    className='truncate max-w-[200px]'
                                                    title={value}
                                                >
                                                    {value.substring(0, 30)}...
                                                </div>
                                            )
                                        }

                                        return (
                                            <td
                                                key={column}
                                                className='whitespace-nowrap px-3 py-3'
                                            >
                                                {displayValue}
                                            </td>
                                        )
                                    })}
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        <button
                                            onClick={() =>
                                                handleProcessDocument(document.id as string)
                                            }
                                            disabled={processingId === document.id}
                                            className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                                                processingId === document.id
                                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                    : 'bg-blue-600 text-white hover:bg-blue-700'
                                            }`}
                                            title='Process document and load to transactions'
                                        >
                                            <ArrowPathIcon
                                                className={`h-4 w-4 ${processingId === document.id ? 'animate-spin' : ''}`}
                                            />
                                            {processingId === document.id
                                                ? 'Processing...'
                                                : 'Process'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {documents.length === 0 && (
                        <div className='flex items-center justify-center py-10'>
                            <p className='text-gray-500'>No documents found.</p>
                        </div>
                    )}
                </div>
                <div className='flex items-center pt-6'>
                    <p className='text-sm text-gray-500'>
                        Total: {documents.length} document{documents.length !== 1 ? 's' : ''}
                    </p>
                </div>
            </div>
        </div>
    )
}
