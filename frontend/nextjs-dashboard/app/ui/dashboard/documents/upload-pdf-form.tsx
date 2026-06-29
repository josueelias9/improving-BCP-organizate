'use client'

import { useActionState, useState } from 'react'
import { createDocument, State } from '@/app/lib/actions'
import { DocumentPlusIcon } from '@heroicons/react/24/outline'
import { lusitana } from '@/app/ui/fonts'
import { DTOGetAllDocumentTypesResponse } from '@/app/lib/orval/src/bcp.schemas'

export default function UploadPDFForm({ data }: { data: DTOGetAllDocumentTypesResponse }) {
    const { document_types } = data
    const initialState: State = { message: null }
    const [state, formAction] = useActionState(createDocument, initialState)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setSelectedFile(file)
        }
    }

    return (
        <div className='rounded-xl bg-gray-50 p-6'>
            <h2 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
                Upload PDF Document
            </h2>

            <form action={formAction} className='space-y-4'>
                <div>
                    <label htmlFor='file' className='mb-2 block text-sm font-medium text-gray-700'>
                        PDF File *
                    </label>
                    <div className='flex items-center gap-4'>
                        <label
                            htmlFor='file'
                            className='flex cursor-pointer items-center gap-2 rounded-md border-2 border-dashed border-gray-300 bg-white px-4 py-6 text-sm text-gray-600 transition hover:border-blue-400 hover:bg-blue-50'
                        >
                            <DocumentPlusIcon className='h-6 w-6' />
                            <span>{selectedFile ? selectedFile.name : 'Choose PDF file...'}</span>
                        </label>
                        <input
                            id='file'
                            name='file'
                            type='file'
                            accept='.pdf'
                            onChange={handleFileChange}
                            className='hidden'
                            aria-describedby='file-error'
                        />
                    </div>
                </div>

                <div>
                    <label htmlFor='type' className='mb-2 block text-sm font-medium text-gray-700'>
                        Document Type *
                    </label>
                    <select
                        id='type'
                        name='type'
                        defaultValue=''
                        className='block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
                        aria-describedby='type-error'
                    >
                        <option value='' disabled>
                            Select type
                        </option>
                        {document_types.map(docType => (
                            <option key={String(docType.id)} value={String(docType.name)}>
                                {String(docType.name)}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label
                        htmlFor='user_email'
                        className='mb-2 block text-sm font-medium text-gray-700'
                    >
                        User Email *
                    </label>
                    <input
                        id='user_email'
                        name='user_email'
                        type='email'
                        defaultValue='admin@bcpextractor.com'
                        className='block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
                        aria-describedby='user_email-error'
                    />
                </div>
                {state?.message ? (
                    <div className='mt-2 rounded-md bg-red-100 p-2 text-sm text-red-700'>
                        {state.message}
                    </div>
                ) : null}
                <button
                    type='submit'
                    className='w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                >
                    Process PDF
                </button>
            </form>
        </div>
    )
}
