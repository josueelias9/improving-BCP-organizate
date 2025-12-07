'use client'

import { lusitana } from '@/app/ui/fonts'
import type { DocumentTable } from '@/app/lib/definitions'

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

export default function DocumentsTable({ documents }: { documents: DocumentTable[] }) {
    const not_included_columns = ["account_number","unique_identifier","user_id","id","previous_balance"]
    
    // Get column names from the first document
    const columns = documents.length > 0 
        ? Object.keys(documents[0]).filter(col => !not_included_columns.includes(col))
        : []

    return (
        <div className='flex w-full flex-col'>
            <h2 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
                All Documents
            </h2>
            <div className='flex grow flex-col justify-between rounded-xl bg-gray-50 p-4'>
                <div className='overflow-x-auto'>
                    <table className='min-w-full text-gray-900'>
                        <thead className='rounded-lg text-left text-sm font-normal'>
                            <tr>
                                {columns.map((column) => (
                                    <th key={column} scope='col' className='px-3 py-5 font-medium'>
                                        {column}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className='bg-white'>
                            {documents.map((document) => (
                                <tr
                                    key={document.id}
                                    className='w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg'
                                >
                                    {columns.map((column) => {
                                        const value = document[column as keyof typeof document]
                                        let displayValue: React.ReactNode = value || 'N/A'

                                        // Special formatting for specific columns
                                        if (column === 'type') {
                                            displayValue = (
                                                <span
                                                    className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                                                        value === 'debit'
                                                            ? 'bg-red-100 text-red-700'
                                                            : 'bg-green-100 text-green-700'
                                                    }`}
                                                >
                                                    {value}
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
                                        } else if (column === 'created_at') {
                                            displayValue = formatDocumentDate(value as string)
                                        } else if (column === 'filename') {
                                            displayValue = (
                                                <span className='font-medium'>{value}</span>
                                            )
                                        } else if (typeof value === 'string' && value.length > 30) {
                                            // Truncate long strings
                                            displayValue = (
                                                <div className='truncate max-w-[200px]' title={value}>
                                                    {value.substring(0, 30)}...
                                                </div>
                                            )
                                        }

                                        return (
                                            <td key={column} className='whitespace-nowrap px-3 py-3'>
                                                {displayValue}
                                            </td>
                                        )
                                    })}
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
