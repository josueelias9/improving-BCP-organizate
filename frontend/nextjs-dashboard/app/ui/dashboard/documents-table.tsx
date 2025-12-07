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
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Filename
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Type
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    User Email
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Created At
                                </th>
                            </tr>
                        </thead>
                        <tbody className='bg-white'>
                            {documents.map((document) => (
                                <tr
                                    key={document.id}
                                    className='w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg'
                                >
                                    <td className='whitespace-nowrap px-3 py-3 font-medium'>
                                        {document.filename}
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        <span
                                            className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                                                document.type === 'debit'
                                                    ? 'bg-red-100 text-red-700'
                                                    : 'bg-green-100 text-green-700'
                                            }`}
                                        >
                                            {document.type}
                                        </span>
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        {document.user_email}
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        {formatDocumentDate(document.created_at)}
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
